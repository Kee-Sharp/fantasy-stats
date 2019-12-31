"""Type in password as argument to script"""
from selenium import webdriver
import csv
import team
import utils
import time
import pathlib
import json
import datetime as dt
import os

def main(args):
    if len(args) == 1 and pathlib.os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            settings = json.loads(f.read())
    else:
        print("Settings.json file is missing. Create JSON object with email and password fields for logging into ESPN")
        return 

    driver = webdriver.Chrome()
    try:
        URL = "https://fantasy.espn.com/basketball/league/standings?leagueId=28621056"
        driver.get(URL)
        login(driver,settings["email"],settings["password"])
        statsdiv = driver.find_element_by_class_name("season--stats--table")
        subTables = statsdiv.find_elements_by_class_name("Table2__table")
        tbodies = [s.find_element_by_tag_name("tbody") for s in subTables]
        group3rows = [b.find_elements_by_tag_name("tr") for b in tbodies]
        rows = []
        for i in range(14):
            rows.append(group3rows[0][i].find_elements_by_tag_name("td")+group3rows[1][i].find_elements_by_tag_name("td")+group3rows[2][i].find_elements_by_tag_name("td"))
        data = [[utils.rmChar(d.text,"\n") for d in arr] for arr in rows]
        teams = [team.Team(arr[1:]) for arr in data]
        driver.close()   
        if not pathlib.os.path.exists("data"):
            pathlib.Path("data").mkdir()
        today = dt.date.today()
        with open(f"data/{today.strftime('%m-%d-%y')}.csv","w", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(["Name","Threes","Rebounds","Assists","Steals","Blocks","Turnovers","Points"])
            for t in teams:
                writer.writerow([t.name,*t.stats()])
        dataFiles = [(n,toDate(n)) for n in os.listdir("data")]
        twoWeeksAgo = today - dt.timedelta(days=14)
        closestDataFile = sorted(dataFiles, key=lambda f: abs((f[1] - twoWeeksAgo)).days)[0][0]
        print("Using:", closestDataFile)
        with open(f"data/{closestDataFile}", "r") as oldF:
            reader = csv.reader(oldF)
            oldTeams = [team.Team(r, arrMode=1) for i,r in enumerate(reader) if i > 0]
        dOldTeams = {t.name: t.stats() for t in oldTeams}
        dNewTeams = {t.name: t.stats() for t in teams}
        modifiedTeams = {name: [dNewTeams[name][i] - dOldTeams[name][i] for i in range(7)] for name in dNewTeams}
        with open("lastTwoWeeks.csv", "w", newline="") as out2:
            writer = csv.writer(out2)
            writer.writerow(["Name","Threes","Rebounds","Assists","Steals","Blocks","Turnovers","Points"])
            for t in modifiedTeams:
                writer.writerow([t, *modifiedTeams[t]])
        print("Stats Updated!")
    except Exception as e:
        print(e)
        driver.close()

def login(driver, email, password):
    """Logs into the ESPN fantasy website given an email and password"""
    time.sleep(4)
    iframe = driver.find_element_by_css_selector("div#disneyid-wrapper iframe")
    driver.switch_to.frame(iframe)
    emailBox,passBox = driver.find_elements_by_tag_name("input")
    emailBox.send_keys(email)
    passBox.send_keys(password)
    driver.find_element_by_css_selector("button[type=submit]").click()
    time.sleep(1)
    driver.refresh()
    time.sleep(8)
def toDate(filename):
    s = filename.split(".csv")[0]
    nums = s.split("-")
    return dt.date(2000+int(nums[2]),int(nums[0]),int(nums[1]))
     
if __name__ == "__main__":
    import sys
    main(sys.argv)


    