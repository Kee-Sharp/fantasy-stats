"""Type in password as argument to script"""
from selenium import webdriver
import csv
import team
import utils
import time
import pathlib

def main(args):
    if len(args) > 1 and "." in args[1]:
        with open (args[1], "r") as f:
            password = f.readline()
    elif len(args) > 1:
        password = args[1]
    else:
        print("Enter in either password or one-line file containing password as second argument")
        return
    driver = webdriver.Chrome()
    try:
        URL = "https://fantasy.espn.com/basketball/league/standings?leagueId=28621056"
        driver.get(URL)
        login(driver, "keetwosuccess@gmail.com",password)
        statsdiv = driver.find_element_by_class_name("season--stats--table")
        subTables = statsdiv.find_elements_by_class_name("Table2__table")
        tbodies = [s.find_element_by_tag_name("tbody") for s in subTables]
        group3rows = [b.find_elements_by_tag_name("tr") for b in tbodies]
        rows = []
        for i in range(14):
            rows.append(group3rows[0][i].find_elements_by_tag_name("td")+group3rows[1][i].find_elements_by_tag_name("td")+group3rows[2][i].find_elements_by_tag_name("td"))
        data = [[utils.rmChar(d.text,"\n") for d in arr] for arr in rows]
        print(data)        
        teams = [team.Team(arr) for arr in data]
        if not pathlib.os.path.exists("output"):
            pathlib.Path("output").mkdir()
        with open("output/updated_stats.csv","w", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(["Name","Threes","Rebounds","Assists","Steals","Blocks","Turnovers","Points","Rank"])
            for t in teams:
                writer.writerow([t.coach,t.threes,t.rebounds,t.assists,t.steals,t.blocks,-t.turnovers,t.points,t.rank])
        print("Stats Updated!")
        driver.close()   
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
     
if __name__ == "__main__":
    import sys
    main(sys.argv)


    