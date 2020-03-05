import countStatistics
def main(args):
    cats = ["total", "Missed", "Threes", "Rebounds", "Assists", "Steals", "Blocks", "Turnovers", "Points"]
    for cat in cats:
        countStatistics.main(["", "-s", cat])

if __name__ == "__main__":
    import sys
    main(sys.argv)