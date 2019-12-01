import csv
from utils import rmK,list_representation

def main(args):
    name1,name2 = args[1:3]
    with open("updated_stats.csv", "r",encoding="utf-8-sig") as f:
        csvin = csv.DictReader(f)
        teamLines = [dict(entry) for entry in csvin]
    translation = {"Tres":"threes","Boards":"rebounds","Oops":"assists","Cookies":"steals","Dikembes":"blocks","JR's":"turnovers","Points":"points"}
    teams = {t["Name"]:rmK(t,["Name","Rank"]) for t in teamLines}
    team1,team2 = teams[name1],teams[name2]
    catsLosing = []
    for cat in team1:
        t = [t1,t2] = [team1[cat],team2[cat]]
        loss = t1 > t2 if cat == "JR's" else t1 < t2
        if loss:
            largePercentage = True
            if float(max(t))/min(t) < 1.1:
                largePercentage = False
            catsLosing.append((cat,largePercentage))
    catsLosing = dict(catsLosing)
    losing = list_representation([translation[c] for c in list(catsLosing)])
    close = list_representation([translation[cat] for cat in catsLosing if not catsLosing[cat]])
    advice = f"Losing {losing} {'none of which are close' if not any(catsLosing.values()) else 'but can win '+close}"
    print(advice)

if __name__ == "__main__":
    import sys
    main(sys.argv)
    
     