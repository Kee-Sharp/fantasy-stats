class Team:
        def __init__(self, arr):
            self.rank = int(arr[0])
            self.name = arr[1].split(" (")[0].strip()
            self.coach = arr[1].split(" (")[1].split(")")[0]
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