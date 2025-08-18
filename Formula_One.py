# F1 Simulator Classes

class Driver:
    def __init__(self, name, skill, team, points=0):
        self.name = name
        self.team = team
        self.skill = skill
        self.points = points

    def __str__(self):
        return f"{self.name} ({self.team})"

class Constructor:
    def __init__(self, name, performance, points=0):
        self.name = name
        self.performance = performance
        self.points = points

    def __str__(self):
        return self.name

class Track:
    def __init__(self, name, length, difficulty):
        self.name = name
        self.length = float(length)
        self.difficulty = difficulty

    def __str__(self):
        return f"{self.name} ({self.length} km)"

class Setting:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f"{self.name} - {self.value}"



if __name__ == "__main__":
    print("This is a library, it doesn't do anything itself")