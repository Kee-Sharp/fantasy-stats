import csv
from utils import rmKeys,list_representation

def main(args):
    """Shows both types of category advice for the matchup"""
    cats = advice1(args[1],args[2])
    print(f"Focus on {list_representation(cats)}")
    advice2(args[1],args[2])

def advice1(name1,name2):
    """Gives the four categories with the best chance of winning"""
    with open("output/updated_stats.csv", "r",encoding="utf-8-sig") as f:
        csvin = csv.DictReader(f)
        teamLines = [dict(entry) for entry in csvin]
    teams = {t["Name"]:rmKeys(t,["Name","Rank"]) for t in teamLines}
    team1,team2 = teams[name1],teams[name2]
    rankedCats = sorted(team1.keys(), key=lambda cat: 2*(team1[cat]-team2[cat])/abs(team1[cat]+team2[cat]), reverse=True)
    return rankedCats[0:4]

def advice2(name1,name2):
    """Shows which categories name1 is losing in, also notifies if they are close"""
    with open("output/updated_stats.csv", "r",encoding="utf-8-sig") as f:
        csvin = csv.DictReader(f)
        teamLines = [dict(entry) for entry in csvin]
    translation = {"Tres":"threes","Boards":"rebounds","Oops":"assists","Cookies":"steals","Dikembes":"blocks","JR's":"turnovers","Points":"points"}
    teams = {t["Name"]:rmKeys(t,["Name","Rank"]) for t in teamLines}
    team1,team2 = teams[name1],teams[name2]
    catsLosing = []
    for cat in team1:
        t = [t1,t2] = [team1[cat],team2[cat]]
        if t1 < t2:
            largePercentage = True
            if float(max(t))/min(t) < 1.1:
                largePercentage = False
            catsLosing.append((cat,largePercentage))
    catsLosing = dict(catsLosing)
    losing = list_representation(list(catsLosing))
    close = list_representation([cat for cat in catsLosing if not catsLosing[cat]])
    advice = f"Losing {losing} {'none of which are close' if not any(catsLosing.values()) else 'but can win '+close}"
    print(advice)

if __name__ == "__main__":
    import sys
    main(sys.argv)
    
     