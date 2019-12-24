import re
class Team:
    def __init__(self, arr, arrMode=0):
        """{arr} contains all relevant information
        {arrMode} the arr has 3 different formats, depending on if it comes from the website, a csv file, or the stats function
        arrMode:0 for website, arrMode:1 for csv file, arrMode:2 for stats arr"""
        if not arrMode: 
            full = re.findall(r"\((.+)\)",arr[0])[0]
            if full == "Jordan Chernof": self.name = "JordanC"
            else: self.name = full.split()[0]
        elif not arrMode - 1: self.name = arr[0].split()[0]
        else: self.name = arr[0]
        self.threes = int(arr[1])
        self.rebounds = int(arr[2])
        self.assists = int(arr[3])
        self.steals = int(arr[4])
        self.blocks = int(arr[5])
        self.turnovers = -int(arr[6]) if not arrMode else int(arr[6])
        self.points = int(arr[7])
    def __repr__(self):
        return self.name
    def stats(self):
        return [self.threes,self.rebounds,self.assists,self.steals,self.blocks,self.turnovers,self.points]

class Player:
    def __init__(self, arr):
        self.Name = arr[1]
        self.Threes = float(arr[6])
        self.Rebounds = float(arr[7])
        self.Assists = float(arr[8])
        self.Steals = float(arr[9])
        self.Blocks = float(arr[10])
        self.Turnovers = -float(arr[11])
        self.Points = float(arr[12])
        self.games = arr[16]
    def __str__(self):
        return self.Name
    def __repr__(self):
        return f"{self.Name} ({self.games} games)"
    