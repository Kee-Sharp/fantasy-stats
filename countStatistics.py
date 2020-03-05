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

def getData(driver, URL, seen):
    driver.get(URL)
    try:
        n1,n2 = [a.text for a in WebDriverWait(driver, timeout=20).until(lambda d: d.find_elements_by_css_selector(".teamHeaders span.owner-name"))]
        if n1 == "Jordan Chernof":
            name1 = "jordanc"
            name2 = n2.split()[0].lower()
        elif n2 == "Jordan Chernof":
            name1 = n1.split()[0].lower()
            name2 = "jordanc"
        else:
            name1 = n1.split()[0].lower()
            name2 = n2.split()[0].lower()
        ret = [] #return the data and the name for each
        for name,start,stop in [(name1,1,3),(name2,3,5)]:
            bodies = driver.find_elements_by_css_selector(".Table2__table__wrapper tbody.Table2__tbody")[start:stop]
            trs = [b.find_elements_by_tag_name("tr") for b in bodies]
            rows = [[*trs[0][i].find_elements_by_tag_name("td"),*trs[1][i].find_elements_by_tag_name("td")] for i in range(10)]
            ret.append(([[d.text for d in r] for r in rows],name))
            seen[name] = True
        return ret
    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        driver.close()
def getStatistic(driver, URL, current, seen, stat):
    result = getData(driver, URL, seen)
    for data,name in result:
        if stat == "Missed":
            num = sum([1 if row[3] and row[4] == "--" else 0 for row in data])
        elif stat == "total":
            num = sum([0 if row[4] == "--" else 1 for row in data])
        elif stat in categories:
            index = categories.index(stat)
            num = sum([0 if row[5 + index] == "--" else int(row[5 + index]) for row in data])
        current[name] += num
    
def main(args):
    startTime = time.perf_counter()
    totalDays = (dt.date.today() - dt.date(2019,10,21)).days
    totalWeeks = int(totalDays/7)
    parser = argparse.ArgumentParser(description='Gather statistics.')
    parser.add_argument('--columns', type=int, nargs='+', default=[], choices=range(totalWeeks+1),
                        help='The indices of columns to recalculate')
    parser.add_argument('--stat', "-s", default="total", choices=["total","Missed", *categories], help='Which stat to calculate')
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
        start = max([int(s.split("Week")[1]) for s in df.columns])
    if progressFileName in os.listdir():
        print(f"Found leftover progress at {progressFileName}")
        with open(progressFileName, "r") as f:
            bigS = f.read()
            bigS = bigS[:-1]
        statsByWeek = processNewLines(bigS, start, statsByWeek)
        print(pd.DataFrame(statsByWeek))
        start = max([int(s.split("Week")[1]) for s in statsByWeek.keys()])
    with open("teamIds.json", "r") as f:
        teamIds = json.loads(f.read())
    URL = "https://fantasy.espn.com/basketball/boxscore?leagueId=28621056&seasonId=2020"
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("--headless")
    chromeOptions.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=chromeOptions)
    weeksToCalculate = list(set([*columns, *range(start, totalWeeks+1)]))#, totalWeeks]))
    print(weeksToCalculate)
    for i in weeksToCalculate: 
        currentWeek = {name: 0 for name in teamIds}
        for j in range(7):
            scoringId = i*7 + j
            if scoringId and scoringId < totalDays:
                seen = {name: False for name in teamIds}
                for name, teamId in teamIds.items():
                    if not seen[name]:
                        getStatistic(driver,setParams(URL, {"teamId": teamId, "scoringPeriodId": scoringId}),currentWeek, seen, stat)
        statsByWeek[f"Week{i+1}"] = currentWeek
        print(currentWeek)
        with open(progressFileName, "a") as f:
            f.write(json.dumps(currentWeek)+"\n") #write progress to file so can be read from if interrupted
    driver.close()
    df = pd.DataFrame(statsByWeek)
    df = df.reindex(teamIds.keys())
    df["Total"] = df.apply(lambda row: sum(row.values), axis=1)
    # print(df.sort_values("Total"))
    with pd.ExcelWriter(fileName) as writer:
        df.to_excel(writer, sheet_name="Team Order")
        df = df.drop("Total", axis=1)
        for i,c in enumerate(df.columns):
            if i != 0:
                df[c] = df[df.columns[i-1]] + df[c]
        print(df)
        df = df.sort_values(df.columns[-1])
        df.to_excel(writer, sheet_name="Cumulative")
        leaders = pd.DataFrame()
        for c in df.columns:
            index = df[c].sort_values(ascending=False).keys()
            leaders[c] = pd.Series(index, [numToPos(i) for i in range(1,15)])
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
def processNewLines(bigS, start=0, oldDictionary={}):
    lines = bigS.split("\n")
    d = {w:strtod(s) for w,s in zip([f"Week{n+1}" for n in range(start,start+len(lines))],lines)}
    oldD = oldDictionary.copy()
    oldD.update(d)
    return oldD
if __name__ == "__main__":
    import sys
    main(sys.argv)


