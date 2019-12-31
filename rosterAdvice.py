from selenium import webdriver
import time
import functools
import pprint as pp
import pathlib
import json
import datetime as dt
from updateData import login
from matchupAdvice import advice1
from team import Player
from utils import list_representation

def main(args):
    if len(args) == 3 and pathlib.os.path.exists("settings.json"):
        name1 = args[1].lower()
        name2 = args[2].lower()
        teamOwner = name1 == "spencer"
        with open("settings.json", "r") as f:
            settings = json.loads(f.read())
    else:
        print("settings.json file is missing. Create JSON object with email and password fields for logging into ESPN")
        return 
    driver = webdriver.Chrome()
    try:
        with open("teamIds.json", "r") as f2:
            teamIds = json.loads(f2.read())
        URL = f"https://fantasy.espn.com/basketball/team?leagueId=28621056&teamId={teamIds[name1]}"
        driver.get(URL)
        login(driver, settings["email"], settings["password"])
        driver.find_element_by_css_selector("option[value='last15']").click()
        time.sleep(3)
        tbodies = driver.find_elements_by_class_name("Table2__tbody")
        group2rows = [b.find_elements_by_tag_name("tr") for b in tbodies]
        rows = []
        for i in range(len(group2rows[0])-1):
            rows.append(group2rows[0][i].find_elements_by_tag_name("td")+group2rows[1][i].find_elements_by_tag_name("td"))
        data = [[d.text.split("\n")[0] for d in arr] for arr in rows]
        # Grab the amount of games from the schedule
        today = dt.date.today()
        if today.weekday() == 0:
            driver.find_element_by_css_selector("button[aria-label='Schedule']").click()
            body = driver.find_element_by_class_name("Table2__tbody")
            schedRows = body.find_elements_by_tag_name("tr")
            schedRows = [row.find_elements_by_tag_name("td") for i,row in enumerate(schedRows) if i < 13]
            fgi = 4 if teamOwner else 3 #index of the first game in row dependent on whether or not team is owned
            schedData = [[d.text.split("\n")[0] for i,d in enumerate(arr) if i in range(fgi,fgi+7)] for arr in schedRows]
            games = [sum([1 if d and d != "--" else 0 for d in row]) for row in schedData]
        else:
            scoringId = int((today - dt.date(2019,10,21)).days/7)*7
            URL += f"&view=schedule&scoringPeriodId={scoringId}"
            driver.get(URL)
            time.sleep(3)
            tbody = driver.find_element_by_css_selector("tbody.Table2__tbody")
            trows = tbody.find_elements_by_tag_name("tr")
            gameData = [r.find_element_by_css_selector(f"td:nth-child({4 if teamOwner else 3})").text for r in trows]
            games = [len(t.split(", ")) for t in gameData]
        driver.close()
        playerData = [[*data[i],games[i]] for i in range(13)]
        players = [Player(row, teamOwner) for row in playerData]
        pp.pprint(players)
        cats = advice1(name1,name2)
        print(f"\nFocus on {list_representation(cats)}")
        orderedPlayers = sorted(players, key=functools.cmp_to_key(compGenerate(cats)), reverse=True) # comparator deprecated
        print("\n")
        print(f"For the four focused categories you should use {list_representation([str(p) for i,p in enumerate(orderedPlayers) if i < 10])}")
        orderedPlayers = sorted(players, key=functools.cmp_to_key(compGenerate(["Threes","Rebounds","Assists","Steals","Blocks","Turnovers","Points"])), reverse=True) # comparator deprecated
        print("\n")
        print(f"For all categories you should use {list_representation([str(p) for i,p in enumerate(orderedPlayers) if i < 10])}")
    except Exception as e:
        print(e)
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



        
        
