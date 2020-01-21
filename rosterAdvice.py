from selenium import webdriver
import functools
import pprint as pp
import json
import datetime as dt
import time
import traceback
from matchupAdvice import advice1
from team import Player
from utils import list_representation
from selenium.webdriver.support.ui import WebDriverWait

def main(args):
    start = time.perf_counter()
    if len(args) == 1 and pathlib.os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            settings = json.loads(f.read())
    elif len(args) == 1:
        print("settings.json file is missing. Create JSON object with email and password fields for logging into ESPN")
        return 
    else:
        print("Don't pass any arguments")
        return
    
    with open("teamIds.json", "r") as f2:
        teamIds = json.loads(f2.read())
    name1 = input("Name of first team?\n").lower()
    while name1 not in teamIds:
        name1 = input("Name not recognized, try again\n").lower()
    name2 = input("Name of second team?\n").lower()
    while name2 not in teamIds:
        name2 = input("Name not recognized, try again\n").lower()
    thisWeek = input("Is the matchup this week? Type 'yes' if so, type 'no' if you want to look at another week\n") == "yes"
    if thisWeek:
        date = dt.date.today()
    else:
        month,day,year = input("Type date in month/day/year format, e.g. May 2nd 2020 -> 5/2/2020\n").split("/")
        month = int(month)
        day = int(day)
        year = int(year)
        date = dt.date(year,month,day)
        if date < dt.date.today():
            actionPresent = False
    isMonday = date.weekday() == 0
    driver = webdriver.Chrome()
    try:
        scoringId = int((date - dt.date(2019,10,21)).days/7)*7
        URL = f"https://fantasy.espn.com/basketball/team?leagueId=28621056&teamId={teamIds[name1]}&view=stats&scoringPeriodId={scoringId}&statSplit=last15"
        print(URL)
        driver.get(URL)
        tbodies = WebDriverWait(driver, timeout=10).until(lambda d: d.find_elements_by_class_name("Table2__tbody"))
        group2rows = [b.find_elements_by_tag_name("tr") for b in tbodies]
        rows = []
        for i in range(len(group2rows[0])-1):
            rows.append(group2rows[0][i].find_elements_by_tag_name("td")+group2rows[1][i].find_elements_by_tag_name("td"))
        data = [[d.text.split("\n")[0] for d in arr] for arr in rows]
        # Grab the amount of games from the schedule
        if thisWeek and isMonday:
            driver.find_element_by_css_selector("button[aria-label='Schedule']").click()
            body = driver.find_element_by_class_name("Table2__tbody")
            schedRows = body.find_elements_by_tag_name("tr")
            schedRows = [row.find_elements_by_tag_name("td") for i,row in enumerate(schedRows) if i < 13]
            schedData = [[d.text.split("\n")[0] for i,d in enumerate(arr) if i in range(3,10)] for arr in schedRows]
            games = [sum([1 if d and d != "--" else 0 for d in row]) for row in schedData]
            for gameTotal, row in zip(games,data):
                row[2] = gameTotal
                del row[3]
        driver.close()
        players = [Player(row, monday=isMonday) for i,row in enumerate(data) if i < 13]
        pp.pprint(players)
        cats = advice1(name1,name2)
        print(f"\nFocus on {list_representation(cats)}")
        orderedPlayers = sorted(players, key=functools.cmp_to_key(compGenerate(cats)), reverse=True) # comparator deprecated
        print("\n")
        print(f"For the four focused categories you should use {list_representation([str(p) for i,p in enumerate(orderedPlayers) if i < 10])}")
        orderedPlayers = sorted(players, key=functools.cmp_to_key(compGenerate(["Threes","Rebounds","Assists","Steals","Blocks","Turnovers","Points"])), reverse=True)
        print("\n")
        print(f"For all categories you should use {list_representation([str(p) for i,p in enumerate(orderedPlayers) if i < 10])}")
        finish = time.perf_counter()
        print(f"Finished in {finish-start} second(s)")
    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        driver.close()


def compGenerate(cats):
    # Compares players based on their ability to perform in specified 4 categories
    def comp(p1, p2):
        # print(p1,p2)
        value = []
        for c in cats:
            v1 = p1.games * vars(p1)[c] # Value = The amount of games for the week times expected performance
            v2 = p2.games * vars(p2)[c]
            if v1 > v2:
                value.append(1)
            elif v1 == v2:
                value.append(0)
            else:
                value.append(-1)
        # print(value)
        return sum(value)
    return comp

if __name__ == "__main__":
    import sys
    main(sys.argv)



        
        
