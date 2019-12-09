from selenium import webdriver
import time
from updateData import login
import functools
from team import Player
from matchupAdvice import advice1
from utils import list_representation
import pprint as pp

def main(args):
    if len(args) == 4 and "." in args[1]:
        with open (args[1], "r") as f:
            password = f.readline()
        name1,name2 = args[2:4]
    elif len(args) == 4:
        password = args[1]
    else:
        print("Enter in either password or one-line file containing password as second argument")
        return
    driver = webdriver.Chrome()
    # try:
    URL = "https://fantasy.espn.com/basketball/team?leagueId=28621056&teamId=6"
    driver.get(URL)
    login(driver, "keetwosuccess@gmail.com", password)
    driver.find_element_by_css_selector("option[value='last15']").click()
    time.sleep(3)
    tbodies = driver.find_elements_by_class_name("Table2__tbody")
    group2rows = [b.find_elements_by_tag_name("tr") for b in tbodies]
    rows = []
    for i in range(len(group2rows[0])-1):
        rows.append(group2rows[0][i].find_elements_by_tag_name("td")+group2rows[1][i].find_elements_by_tag_name("td"))
    data = [[d.text.split("\n")[0] for d in arr] for arr in rows]
    # Grab the amount of games from the schedule
    driver.find_element_by_css_selector("button[aria-label='Schedule']").click()
    body = driver.find_element_by_class_name("Table2__tbody")
    schedRows = body.find_elements_by_tag_name("tr")
    schedRows = [row.find_elements_by_tag_name("td") for i,row in enumerate(schedRows) if i < 13]
    schedData = [[d.text.split("\n")[0] for i,d in enumerate(arr) if i in range(4,11)] for arr in schedRows]
    games = [sum([1 if d and d != "--" else 0 for d in row]) for row in schedData]
    playerData = [[*data[i],games[i]] for i in range(13)]
    players = [Player(row) for row in playerData]
    pp.pprint(players)
    cats = advice1(name1,name2)
    print(f"\nFocus on {list_representation(cats)}")
    orderedPlayers = sorted(players, key=functools.cmp_to_key(compGenerate(cats)), reverse=True) # comparator deprecated
    print("\n")
    print(f"You should use {list_representation([str(p) for i,p in enumerate(orderedPlayers) if i < 10])}")
# except Exception as e:
#     print(e)
    driver.close()


def compGenerate(cats):
    # Compares players based on their ability to perform in specified 4 categories
    def comp(p1, p2):
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
        if sum(value) == 0:
            print("tie: ",p1,p2)
        return sum(value)
    return comp

if __name__ == "__main__":
    import sys
    main(sys.argv)



        
        
        