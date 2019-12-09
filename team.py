import re
class Team:
        def __init__(self, arr):
            self.rank = int(arr[0])
            self.name = arr[1].split(" (")[0].strip()
            self.coach = re.findall(r"\((.+)\)",arr[1])[0].split()[0]
            self.threes = int(arr[2])
            self.rebounds = int(arr[3])
            self.assists = int(arr[4])
            self.steals = int(arr[5])
            self.blocks = int(arr[6])
            self.turnovers = int(arr[7])
            self.points = int(arr[8])
        def __repr__(self):
            return self.name
        def __lt__(self, other):
            return self.rank < other.rank
        def __eq__(self, other):
            return self.rank == other.rank

class Player:
    def __init__(self, arr):
        self.Name = arr[1]
        self.Threes = float(arr[6])
        self.Rebounds = float(arr[7])
        self.Assists = float(arr[8])
        self.Steals = float(arr[9])
        self.Blocks = float(arr[10])
        self.Turnovers = float(arr[11])
        self.Points = float(arr[12])
        self.games = arr[16]
    def __str__(self):
        return self.Name
    def __repr__(self):
        return f"{self.Name} ({self.games} games)"
    