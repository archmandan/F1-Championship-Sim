import sqlite3
import os
import sys
import Formula_One as f1
import random

# === Get info from database ===
def retrieveDrivers():
    conn = sqlite3.connect('f1.db')
    c = conn.cursor()

    c.execute("""
        SELECT Drivers.name, Constructors.name AS team_name FROM Drivers
        JOIN Constructors ON Drivers.team_id = Constructors.id
        ORDER BY Constructors.performance DESC;
    """)

    results = c.fetchall()
    drivers = []

    for row in results:
        drivers.append(f1.Driver(row[0], 0, row[1]))

    return drivers

def retrieveConstructors():
    conn = sqlite3.connect('f1.db')
    c = conn.cursor()

    c.execute("""
        SELECT name, performance FROM Constructors
        ORDER BY performance DESC;
    """)

    results = c.fetchall()
    teams = []

    for row in results:
        teams.append(f1.Constructor(row[0], row[1]))

    return teams

def retrieveTracks():
    conn = sqlite3.connect('f1.db')
    c = conn.cursor()

    c.execute("""
        SELECT name, length FROM Tracks
        ORDER BY length DESC;
    """)

    results = c.fetchall()
    tracks = []

    for row in results:
        tracks.append(f1.Track(row[0], float(row[1])))

    return tracks

# === Other Functions ===
def print_rgb(text, rgb):
    r, g, b = rgb
    print(f"\033[38;2;{r};{g};{b}m{text}\033[0m")

def colourise_lengths():
    far, medium, short = [], [], []
    for track in tracks:
        if (tracks.index(track) + 1) <= 8:
            far.append(track)
        elif (tracks.index(track) + 1) <= 16 and (tracks.index(track) + 1) > 8:
            medium.append(track)
        elif (tracks.index(track) + 1) <= 24 and (tracks.index(track) + 1) > 16:
            short.append(track)
    return far, medium, short

def clear_console():
    os.system("clear" if os.name == 'posix' else "cls")

# === Sim Race ===
def simulateRace():
    pass

# === Lists and Variables ===
drivers = retrieveDrivers()
constructors = retrieveConstructors()
tracks = retrieveTracks()
far, medium, short = colourise_lengths()
menu_options = [
    "Simulate a Race",
    "Simulate a Championship",
    "View current drivers",
    "View current teams",
    "View current tracks",
    "Settings",
    "Exit"
]
option_status = {
    "Simulate a Race": False,
    "Simulate a Championship": False,
    "View current drivers": True,
    "View current teams": True,
    "View current tracks": True,
    "Settings": True,
    "Exit": True,
    "Add DNFs": True,
    "Toggle Colourise": True,
    "Back to Main Menu": False
}
TEAM_RGB = {
    "Mercedes-AMG Petronas F1 Team": (0, 215, 182),
    "Oracle Red Bull Racing": (71, 129, 215),
    "Scuderia Ferrari HP": (237, 17, 49),
    "McLaren Formula 1 Team": (244, 118, 0),
    "BWT Alpine F1 Team": (0, 161, 232),
    "Visa Cash App Racing Bulls F1 Team": (108, 152, 255),
    "Aston Martin Aramco F1 Team": (34, 153, 113),
    "Atlassian Williams Racing": (24, 104, 219),
    "Stake F1 Team Kick Sauber": (1, 192, 14),
    "MoneyGram Haas F1 Team": (156, 159, 162)
}
TRACK_RGB = {
    "far": (237, 17, 49),
    "medium": (255, 191, 0),
    "short": (0, 215, 0)
}
MENU_RGB = {
    "enabled": (0, 215, 0),
    "disabled": (237, 17, 49)
}
POSITION_RGB = {
    "P1": (211, 175, 55),
    "P2": (196, 196, 196),
    "P3": (183, 65, 14),
    "POINTS": (48, 92, 222),
    "NO POINTS": (211, 211, 211)
}
settings_options = [
    f1.Setting("Add DNFs", 0),
    f1.Setting("Toggle Colourise", True)
]
colourise_enabled = bool(settings_options[1].value)  # default is ON


# === Main Loop ===
def main():
    global colourise_enabled
    print("Welcome to the F1 Simulator!")
    while True:
        print("Menu:")
        for option in menu_options:
            if colourise_enabled:
                colour = MENU_RGB["enabled"] if option_status.get(option, True) else MENU_RGB["disabled"]
                print_rgb(f"{menu_options.index(option) + 1}.\t{option}", colour)
            else:
                print(f"{menu_options.index(option) + 1}.\t{option}")
        inp = int(input("Select an option: "))
        clear_console()
        match inp:
            case 1:
                simulateRace()
            case 2:
                pass
            case 3:
                for driver in drivers:
                    if colourise_enabled:
                        rgb = TEAM_RGB.get(driver.team, (255, 255, 255))  # default to white
                        print_rgb(f"{drivers.index(driver) + 1}.\t{driver.name} ({driver.team})", rgb)
                    else:
                        print(f"{drivers.index(driver) + 1}.\t{driver.name} ({driver.team})")
            case 4:
                for team in constructors:
                    if colourise_enabled:
                        rgb = TEAM_RGB.get(team.name, (255, 255, 255))
                        print_rgb(f"{constructors.index(team) + 1}.\t{team.name} - Performance: {team.performance}", rgb)
                    else:
                        print(f"{constructors.index(team) + 1}.\t{team.name} - Performance: {team.performance}")
            case 5:
                for track in far:
                    if colourise_enabled:
                        print_rgb(f"{tracks.index(track) + 1}.\t{track.name} ({track.length} km)", TRACK_RGB["far"])
                    else:
                        print(f"{tracks.index(track) + 1}.\t{track.name} ({track.length} km)")
                for track in medium:
                    if colourise_enabled:
                        print_rgb(f"{tracks.index(track) + 1}.\t{track.name} ({track.length} km)", TRACK_RGB["medium"])
                    else:
                        print(f"{tracks.index(track) + 1}.\t{track.name} ({track.length} km)")
                for track in short:
                    if colourise_enabled:
                        print_rgb(f"{tracks.index(track) + 1}.\t{track.name} ({track.length} km)", TRACK_RGB["short"])
                    else:
                        print(f"{tracks.index(track) + 1}.\t{track.name} ({track.length} km)")
            case 6:
                while True:
                    i = 1
                    print("Settings:")
                    for setting in settings_options:
                        val_display = setting.value
                        if colourise_enabled:
                            colour = MENU_RGB["enabled"] if option_status.get(setting.name, True) else MENU_RGB["disabled"]
                            print_rgb(f"{settings_options.index(setting) + 1}.\t{setting.name} - {val_display}", colour)
                        else:
                            print(f"{settings_options.index(setting) + 1}.\t{setting.name} - {val_display}")
                        i += 1
                    if colourise_enabled:
                        print_rgb(f"{i}.\tBack to Main Menu", MENU_RGB["enabled"])
                    else:
                        print(f"{i}.\tBack to Main Menu")
                    inp1 = int(input("Select an option: "))
                    clear_console()
                    match inp1:
                        case 1:
                            while True:
                                inp2 = int(input("How many maximum DNFs (per race): (0-5) "))
                                clear_console()
                                if inp2 < 0 or inp2 > 5:
                                    print(f"Invalid amount: {inp2}")
                                else:
                                    settings_options[0].value = inp2
                                    break
                        case 2:
                            settings_options[1].value = not settings_options[1].value
                            colourise_enabled = settings_options[1].value
                        case 3:
                            break
                        case _:
                            print("Invalid choice")
            case 7:
                print("Thanks for playing! Ciao")
                sys.exit()
            case _:
                print("Invalid choice")


if __name__ == "__main__":
    main()