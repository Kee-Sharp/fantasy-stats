import csv
from utils import rmKeysF,list_representation

def main(args):
    """Shows both types of category advice for the matchup"""
    name1 = args[1].lower()
    name2 = args[2].lower()
    cats = advice1(name1,name2)
    print(f"Focus on {list_representation(cats)}")
    advice2(name1,name2)

def advice1(name1,name2):
    """Gives the five categories with the best chance of winning"""
    with open("lastTwoWeeks.csv", "r", encoding="utf-8-sig") as f:
        csvin = csv.DictReader(f)
        teamLines = [dict(entry) for entry in csvin]
    teams = {t["Name"].lower():rmKeysF(t,["Name","Rank"]) for t in teamLines}
    team1,team2 = teams[name1],teams[name2]
    #the 'winningness' of each category is measured by difference divided by the average
    rankedCats = sorted(team1.keys(), key=lambda cat: 2*(team1[cat]-team2[cat])/abs(team1[cat]+team2[cat]), reverse=True)
    return rankedCats[:5]

def advice2(name1,name2):
    """Shows which categories name1 is losing in, also notifies if they are close"""
    with open("lastTwoWeeks.csv", "r", encoding="utf-8-sig") as f:
        csvin = csv.DictReader(f)
        teamLines = [dict(entry) for entry in csvin]
    translation = {"Tres":"threes","Boards":"rebounds","Oops":"assists","Cookies":"steals","Dikembes":"blocks","JR's":"turnovers","Points":"points"}
    teams = {t["Name"].lower():rmKeysF(t,["Name","Rank"]) for t in teamLines}
    team1,team2 = teams[name1],teams[name2]
    catsLosing = []
    for cat in team1:
        t = [t1,t2] = [team1[cat],team2[cat]]
        minT, maxT = (min(t),max(t)) if t1 > 0 else (max(t),min(t))
        if t1 < t2:
            largePercentage = True
            if abs(float(maxT)/minT) < 1.1:
                largePercentage = False
            catsLosing.append((cat,largePercentage))
    catsLosing = dict(catsLosing)
    losing = list_representation(list(catsLosing))
    close = list_representation([cat for cat in catsLosing if not catsLosing[cat]])
    advice = f"Losing {losing} {'none of which are close' if all(catsLosing.values()) else 'but can win '+close}"
    print(advice)

if __name__ == "__main__":
    import sys
    main(sys.argv)
    
     