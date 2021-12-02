"""Run with arg 'missed' if you want to count missed games, otherwise will count total games played"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
import traceback
import json
import datetime as dt
import pandas as pd
import os
import argparse
from utils import setParams,numToPos

categories = ["Threes", "Rebounds", "Assists", "Steals", "Blocks", "Turnovers", "Points"]
percentageCategories = ["Fg%", "Ft%"]

def getData(driver, URL, seen):
    driver.get(URL)
    try:
        n1,n2 = [a.text for a in WebDriverWait(driver, timeout=20).until(lambda d: d.find_elements_by_css_selector(".teamHeaders span.owner-name"))]
        name1 = n1.split()[0].lower()
        name2 = n2.split()[0].lower()
        ret = [] #return the data and the name for each
        for i,name in enumerate([name1, name2]):
            #website has each stats table split into two separate table elements
            bodies = driver.find_elements_by_css_selector("section.players-table tbody.Table__TBODY")[i*2:i*2+2]
            trs = [b.find_elements_by_tag_name("tr") for b in bodies]
            #collect the rows from both halves of the table into one row
            rows = [[*trs[0][i].find_elements_by_tag_name("td"),*trs[1][i].find_elements_by_tag_name("td")] for i in range(10)]
            ret.append(([[d.text for d in r] for r in rows],name))
            seen[name] = True
        return ret
    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        driver.close()
def getStatistic(driver, URL, current, seen, stat):
    print(URL)
    result = getData(driver, URL, seen)
    print(result)
    for data,name in result:
        if stat == "Missed":
            num = sum([1 if row[3] and row[4] == "--" else 0 for row in data])
            current[name] += num
        elif stat == "total":
            num = sum([0 if row[4] == "--" else 1 for row in data])
            current[name] += num
        elif stat in categories:
            index = categories.index(stat)
            num = sum([0 if row[9 + index] == "--" else int(row[9 + index]) for row in data])
            current[name] += num
        else:
            index = percentageCategories.index(stat)
            index = 5 + index*2
            newData = (sum([0 if row[index] == "--/--" else int(row[index].split("/")[0]) for row in data]), 
                        sum([0 if row[index] == "--/--" else int(row[index].split("/")[1]) for row in data]))
            oldData = current[name]
            current[name] = (oldData[0]+newData[0], oldData[1]+newData[1])

    
def main(args):
    startTime = time.perf_counter()
    seasonStartDate = dt.date(2020,12,22)
    totalDays = (dt.date.today() - seasonStartDate).days
    totalWeeks = int(totalDays/7)
    parser = argparse.ArgumentParser(description='Gather statistics.')
    parser.add_argument('--columns', type=int, nargs='+', default=[], choices=range(totalWeeks+1),
                        help='The indices of columns to recalculate')
    parser.add_argument('--stat', "-s", default="total", choices=["total","Missed", *categories, *percentageCategories], help='Which stat to calculate')
    parser.add_argument('--recalculateLast', "-re", action='store_true')
    a = parser.parse_args(args[1:])
    print(a)
    stat, columns, re = a.stat, a.columns, a.recalculateLast
    if re: columns += [totalWeeks - 1]
    file = f"total{'Games' if stat == 'total' else stat}"
    fileName = file + ".xlsx"
    progressFileName = file + ".txt"
    statsByWeek = {}
    start = 0
    #Gather calculation from previous weeks and previous runs that have been interrupted
    if fileName in os.listdir():
        df = pd.read_excel(fileName, index_col=0)
        if "Total" in df.columns: df = df.drop("Total", axis=1)
        print(df)
        statsByWeek = df.to_dict()
        start = max([int(s.split("Week")[1]) for s in df.columns]) - 1
    if progressFileName not in os.listdir():
        with open(progressFileName, "w") as f:
            f.write(json.dumps({"start": start})+"\n")
    else:
        print(f"Found leftover progress at {progressFileName}")
        with open(progressFileName, "r") as f:
            bigS = f.read()
            bigS = bigS[:-1]
        lines = bigS.split("\n")
        progressStart = json.loads(lines[0])["start"]
        statsByWeek = processNewLines(lines[1:], progressStart, statsByWeek)
        print(pd.DataFrame(statsByWeek))
        start = max([int(s.split("Week")[1]) for s in statsByWeek.keys()], default=1) - 1
    with open("teamIds.json", "r") as f:
        teamIds = json.loads(f.read())
    URL = "https://fantasy.espn.com/basketball/boxscore?leagueId=28621056&seasonId=2021"
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("--headless")
    chromeOptions.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=chromeOptions)
    weeksToCalculate = list(set([*columns, *range(start, totalWeeks+1)]))#, totalWeeks]))
    percentageTotal = {name: (0, 0) for name in teamIds} #season total, only used for the percentageCategories
    cumulativeStatsByWeek = {} #only used for the percentageCategories
    print(weeksToCalculate)
    for i in weeksToCalculate: 
        currentWeek = {name: 0 if stat not in percentageCategories else (0,0) for name in teamIds}
        for j in range(7):
            scoringId = i*7 + j
            if scoringId and scoringId <= totalDays:
                seen = {name: False for name in teamIds}
                for name, teamId in teamIds.items():
                    if not seen[name]:
                        getStatistic(driver,setParams(URL, {"teamId": teamId, "scoringPeriodId": scoringId}),currentWeek, seen, stat)
        print(currentWeek)
        if stat in percentageCategories:
            cumulativeWeek = {}
            for name, (made, attempted) in currentWeek.items():
                currentWeek[name] = made/attempted
                #also update the total for the season
                oldMade, oldAttempted = percentageTotal[name]
                percentageTotal[name] = (oldMade+made,oldAttempted+attempted)
                cumulativeWeek[name] = percentageTotal[name][0]/percentageTotal[name][1]
            cumulativeStatsByWeek[f"Week{i+1}"] = cumulativeWeek
            print(cumulativeWeek)
        statsByWeek[f"Week{i+1}"] = currentWeek
        # print(currentWeek)
        with open(progressFileName, "a") as f:
            f.write(json.dumps(currentWeek)+"\n") #write progress to file so can be read from if interrupted
    driver.close()
    df = pd.DataFrame(statsByWeek)
    df = df.reindex(teamIds.keys())
    if stat in percentageCategories:
        df["Total"] = [percentageTotal[name][0]/percentageTotal[name][1] for name in teamIds]
    else:
        df["Total"] = df.apply(lambda row: sum(row.values), axis=1)
    # print(df.sort_values("Total"))
    with pd.ExcelWriter(fileName) as writer:
        df.to_excel(writer, sheet_name="Team Order")
        df = df.drop("Total", axis=1)
        if stat in percentageCategories:
            df = pd.DataFrame(cumulativeStatsByWeek)
        else:
            for i,c in enumerate(df.columns):
                if i != 0:
                    df[c] = df[df.columns[i-1]] + df[c]
            print(df)
        df = df.sort_values(df.columns[-1])
        df.to_excel(writer, sheet_name="Cumulative")
        leaders = pd.DataFrame()
        for c in df.columns:
            index = df[c].sort_values(ascending=False).keys()
            leaders[c] = pd.Series(index, [numToPos(i) for i in range(1,9)])
        leaders.to_excel(writer, sheet_name="Weekly Leaders")
        #custom rule: =B2=INDEX(SORT(B$2:B$15,,-1,),3,1) | =B2=MAX(B$2:B$15)
    if progressFileName in os.listdir(): os.remove(progressFileName)
    finish = time.perf_counter()
    print(f"Finished in {finish-startTime} second(s)")

def strtod(s):
    ret = ''
    for l in s:
        ret += l if l != "'" else '"'
    return json.loads(ret)
def processNewLines(lines, start=0, oldDictionary={}):
    d = {w:strtod(s) for w,s in zip([f"Week{n+1}" for n in range(start,start+len(lines))],lines)}
    oldD = oldDictionary.copy()
    oldD.update(d)
    return oldD
if __name__ == "__main__":
    import sys
    main(sys.argv)


