from selenium import webdriver
import csv
import team
import utils
import time
import pathlib
import json
import datetime as dt
import os
from selenium.webdriver.support.ui import WebDriverWait

def main():
    start = time.perf_counter()
    driver = webdriver.Chrome()
    try:
        URL = "https://fantasy.espn.com/basketball/league/standings?leagueId=28621056"
        driver.get(URL)
        #collect stats for each category
        statsdiv = WebDriverWait(driver, timeout=10).until(lambda d: d.find_element_by_class_name("season--stats--table"))
        tbodies = statsdiv.find_elements_by_tag_name("tbody")
        group3rows = [b.find_elements_by_tag_name("tr") for b in tbodies]
        rows = []
        for i in range(8):
            rows.append(group3rows[0][i].find_elements_by_tag_name("td")+group3rows[1][i].find_elements_by_tag_name("td")+group3rows[2][i].find_elements_by_tag_name("td"))
        data = [[utils.rmChar(d.text,"\n") for d in arr] for arr in rows]
        teams = [team.Team(arr[1:]) for arr in data]
        #collect win record and percentage
        tbody = driver.find_element_by_css_selector("div.innerTable tbody.Table__TBODY")
        rows = tbody.find_elements_by_tag_name("tr")
        data = [[d.text for d in row.find_elements_by_tag_name("td")] for row in rows]
        stats = [[f"'{row[2]}-{row[3]}-{row[4]}",row[5]] for row in data] #the ' at the beginning is for Google sheets formatting
        driver.close()   
        if not pathlib.os.path.exists("data"):
            pathlib.Path("data").mkdir()
        #write raw data to file
        today = dt.date.today()
        with open(f"data/{today.strftime('%m-%d-%y')}.csv","w", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(["Name","Fg%","Ft%","Threes","Rebounds","Assists","Steals","Blocks","Turnovers","Points"])
            for t in teams:
                writer.writerow([t.name,*t.stats()])
        with open("winRecord.csv", "w", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(["Name","Win Record", "Win Percentage"])
            for t, statLine in zip(teams, stats):
                writer.writerow([t.name, *statLine])
        # calculate last two weeks and write to file
        dataFiles = [(n,toDate(n)) for n in os.listdir("data")]
        twoWeeksAgo = today - dt.timedelta(days=14)
        closestDataFile = sorted(dataFiles, key=lambda f: abs((f[1] - twoWeeksAgo)).days)[0][0]
        print("Using:", closestDataFile)
        with open(f"data/{closestDataFile}", "r") as oldF:
            reader = csv.reader(oldF)
            oldTeams = [team.Team(r, arrMode=1) for i,r in enumerate(reader) if i > 0]
        dOldTeams = {t.name: t.stats() for t in oldTeams}
        dNewTeams = {t.name: t.stats() for t in teams}
        modifiedTeams = {name: [dNewTeams[name][i+2] - dOldTeams[name][i+2] for i in range(7)] for name in dNewTeams}
        for name in modifiedTeams:
            modifiedTeams[name] = [*dNewTeams[name][:2], *modifiedTeams[name]]
        with open("lastTwoWeeks.csv", "w", newline="") as out2:
            writer = csv.writer(out2)
            writer.writerow(["Name","Fg","Ft","Threes","Rebounds","Assists","Steals","Blocks","Turnovers","Points"])
            for teamName,stats in modifiedTeams.items():
                writer.writerow([teamName, *stats])
        print("Stats Updated!")
        finish = time.perf_counter()
        print(f"Finished in {finish-start} second(s)")
    except Exception as e:
        print(e)
        driver.close()

def toDate(filename):
    s = filename.split(".csv")[0]
    nums = s.split("-")
    return dt.date(2000+int(nums[2]),int(nums[0]),int(nums[1]))
     
if __name__ == "__main__":
    main()


