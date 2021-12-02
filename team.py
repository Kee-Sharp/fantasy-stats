import re
class Team:
    def __init__(self, arr, arrMode=0):
        """{arr} contains all relevant information
        {arrMode} the arr has 3 different formats, depending on if it comes from the website, a csv file, or the stats function
        arrMode:0 for website, arrMode:1 for csv file, arrMode:2 for stats arr"""
        if not arrMode: 
            self.name = re.findall(r"\((\w+).+\)",arr[0])[0]
        elif arrMode == 1: self.name = arr[0].split()[0]
        else: self.name = arr[0]
        self.fg = f(arr[1])
        self.ft = f(arr[2])
        self.threes = int(arr[3])
        self.rebounds = int(arr[4])
        self.assists = int(arr[5])
        self.steals = int(arr[6])
        self.blocks = int(arr[7])
        self.turnovers = -int(arr[8]) if not arrMode else int(arr[8])
        self.points = int(arr[9])
    def __repr__(self):
        return self.name
    def stats(self):
        return [self.fg,self.ft,self.threes,self.rebounds,self.assists,self.steals,self.blocks,self.turnovers,self.points]

class Player:
    def __init__(self, arr):
        self.Name = arr[1]
        self.Fg = f(arr[5])
        self.Ft = f(arr[7])
        self.Threes = f(arr[8])
        self.Rebounds = f(arr[9])
        self.Assists = f(arr[10])
        self.Steals = f(arr[11])
        self.Blocks = f(arr[12])
        self.Turnovers = -f(arr[13])
        self.Points = f(arr[14])
        self.games = len(arr[2].split(", "))
    def __str__(self):
        return self.Name
    def __repr__(self):
        return f"{self.Name} ({self.games} games)"

def f(s):
    try:
        ret = float(s)
        return ret
    except Exception:
        return 0
    