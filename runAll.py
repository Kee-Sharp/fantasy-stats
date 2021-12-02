import countStatistics
def main(args):
    cats = ["Threes", "Rebounds", "Assists", "Steals", "Blocks", "Turnovers", "Points"]
    for cat in cats:
        countStatistics.main(["", "-s", cat]) #+ (["--columns", "19"] if i > 4 else [])) #*args[1:]])

if __name__ == "__main__":
    import sys
    main(sys.argv)