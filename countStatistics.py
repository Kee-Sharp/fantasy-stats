"""Run with arg 'missed' if you want to count missed games, otherwise will count total games played"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
import traceback
import json
import datetime as dt
import pandas as pd
import os
from utils import setParams

def getStatistic(driver, URL, current, seen, missed):
    driver.get(URL)
    try:
        n1,n2 = [a.text for a in WebDriverWait(driver, timeout=10).until(lambda d: d.find_elements_by_css_selector(".teamHeaders span.owner-name"))]
        if n1 == "Jordan Chernof":
            name1 = "jordanc"
            name2 = n2.split()[0].lower()
        elif n2 == "Jordan Chernof":
            name1 = n1.split()[0].lower()
            name2 = "jordanc"
        else:
            name1 = n1.split()[0].lower()
            name2 = n2.split()[0].lower()
        for name,start,stop in [(name1,1,3),(name2,3,5)]:
            bodies = driver.find_elements_by_css_selector(".Table2__table__wrapper tbody.Table2__tbody")[start:stop]
            trs = [b.find_elements_by_tag_name("tr") for b in bodies]
            rows = [[*trs[0][i].find_elements_by_tag_name("td"),*trs[1][i].find_elements_by_tag_name("td")] for i in range(10)]
            data = [[d.text for d in r] for r in rows]
            if missed:
                stat = sum([1 if row[3] and row[4] == "--" else 0 for row in data])
            else:
                stat = sum([0 if row[4] == "--" else 1 for row in data])
            seen[name] = True
            current[name] += stat
    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        driver.close()
def main(args):
    start = time.perf_counter()
    countMissed = len(args) == 2 and args[1] == "missed"
    stat = "missed" if countMissed else "total"
    #Gather calculation from previous weeks
    if f"{stat}Games.xlsx" in os.listdir():
        df = pd.read_excel(f"{stat}Games.xlsx", index_col=0)
        statsByWeek = df.to_dict()
        del statsByWeek["Total"]
        start = max([int(s.split("Week")[1]) for s in df.columns if s != "Total"]) - 1 # recalculate last week in case that weeks games were not finished
    else:
        statsByWeek = {}
        start = 0
    with open("teamIds.json", "r") as f:
        teamIds = json.loads(f.read())
    URL = "https://fantasy.espn.com/basketball/boxscore?leagueId=28621056&seasonId=2020"
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("--headless")
    chromeOptions.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=chromeOptions)
    totalDays = (dt.date.today() - dt.date(2019,10,21)).days
    totalWeeks = int(totalDays/7)
    print(start, totalWeeks+1)
    for i in range(start, totalWeeks+1): 
        currentWeek = {name: 0 for name in teamIds}
        for j in range(7):
            scoringId = i*7 + j
            if scoringId and scoringId < totalDays:
                seen = {name: False for name in teamIds}
                for name, teamId in teamIds.items():
                    if not seen[name]:
                        getStatistic(driver,setParams(URL, {"teamId": teamId, "scoringPeriodId": scoringId}),currentWeek, seen, countMissed)
        statsByWeek[f"Week{i+1}"] = currentWeek
        print(currentWeek)
    driver.close()
    df = pd.DataFrame(statsByWeek)
    df = df.reindex(teamIds.keys())
    df["Total"] = df.apply(lambda row: sum(row.values), axis=1)
    print(df.sort_values("Total"))
    with pd.ExcelWriter(f"{'missed' if countMissed else 'total'}Games.xlsx") as writer:
        df.to_excel(writer, sheet_name="Team Order")
        df.sort_values("Total").to_excel(writer, sheet_name="Team Order")
    finish = time.perf_counter()
    print(f"Finished in {finish-start} second(s)")
if __name__ == "__main__":
    import sys
    main(sys.argv)


