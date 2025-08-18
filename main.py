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
        SELECT name, length, difficulty FROM Tracks
        ORDER BY length DESC;
    """)

    results = c.fetchall()
    tracks = []

    for row in results:
        tracks.append(f1.Track(row[0], float(row[1]), row[2]))

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
def simulateRace(teamdict, track, max_dnfs):
    scoring = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    dnfs = []
    drivers_race = drivers.copy()
    for i in range(random.randint(0, max_dnfs)):
        dnf = random.choice(drivers_race)
        drivers_race.remove(dnf)
        dnfs.append(dnf)
    results = []
    for driver in drivers_race:
        team = teamdict.get(driver.team)
        chaos = TRACK_CHAOS.get(track.name, 10)

        # Base score heavily weighted on skill and team
        base_score = (driver.skill * 0.7) + (team.performance * 0.7) - track.difficulty

        # Randomness proportional to track chaos but capped
        rand = random.gauss(0, chaos)
        rand = max(min(rand, 10), -10)  # cap to ±10

        # Occasional tiny underdog chance
        underdog = random.uniform(0, 5) if random.random() < 0.02 else 0

        score = base_score + rand + underdog
        results.append((driver, score))

    # Sort descending
    results.sort(key=lambda x: x[1], reverse=True)

    print(f"Race at {track.name} Results:")
    for pos, (driver, score) in enumerate(results, start=1):
        if pos <= 10:
            driver.points += scoring[pos - 1]
        if colourise_enabled:
            if pos == 1:
                colour = POSITION_RGB["P1"]
            elif pos == 2:
                colour = POSITION_RGB["P2"]
            elif pos == 3:
                colour = POSITION_RGB["P3"]
            elif pos <= 10:
                colour = POSITION_RGB["POINTS"]
            else:
                colour = POSITION_RGB["NO POINTS"]
            print_rgb(f"{pos}.\t{driver} - {driver.points} pts", colour)
        else:
            print(f"{pos}.\t{driver} - {driver.points} pts")
    for driver in dnfs:
        if colourise_enabled:
            print_rgb(f"DNF.\t{driver}", POSITION_RGB["DNF"])
        else:
            print(f"DNF.\t{driver}")

def simulateChampionship(teamdict, max_dnfs):
    scoring = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    tracks_champ = tracks.copy()
    champ_results = []

    # Reset driver and constructor points
    for driver in drivers:
        driver.points = 0
    for constructor in constructors:
        constructor.points = 0

    # Simulate each race
    for race_num in range(24):
        # Select random track and remove from remaining tracks
        track = random.choice(tracks_champ)
        tracks_champ.remove(track)

        dnfs = []
        drivers_race = drivers.copy()
        # Random DNFs
        dnf_amount = random.randint(0, max_dnfs)
        for _ in range(dnf_amount):
            if drivers_race:
                dnf = random.choice(drivers_race)
                drivers_race.remove(dnf)
                dnfs.append(dnf)

        # Calculate scores for drivers
        results = []
        for driver in drivers_race:
            team = teamdict.get(driver.team)
            chaos = TRACK_CHAOS.get(track.name, 10)

            # Base score heavily weighted on skill and team
            base_score = (driver.skill * 0.7) + (team.performance * 0.7) - track.difficulty

            # Randomness proportional to track chaos but capped
            rand = random.gauss(0, chaos)
            rand = max(min(rand, 10), -10)

            # Occasional tiny underdog chance
            underdog = random.uniform(0, 5) if random.random() < 0.02 else 0

            score = base_score + rand + underdog
            results.append((driver, score))

        # Sort descending by score
        results.sort(key=lambda x: x[1], reverse=True)

        # Award points to drivers
        for pos, (driver, score) in enumerate(results, start=1):
            if pos <= 10:
                driver.points += scoring[pos - 1]

        # Award points to constructors (top 2 drivers per race only)
        constructor_scores = {}
        for pos, (driver, _) in enumerate(results, start=1):
            points_this_race = scoring[pos - 1] if pos <= 10 else 0
            constructor_scores.setdefault(driver.team, []).append(points_this_race)

        for team_name, pts_list in constructor_scores.items():
            top_two_points = sum(sorted(pts_list, reverse=True)[:2])
            constructor_lookup[team_name].points += top_two_points


    # === Final Driver Standings ===
    champ_results = sorted(drivers, key=lambda d: d.points, reverse=True)
    print("\n🏁 Drivers Championship Standings 🏁")
    for pos, driver in enumerate(champ_results, start=1):
        if colourise_enabled:
            if pos == 1:
                colour = POSITION_RGB["P1"]
            elif pos == 2:
                colour = POSITION_RGB["P2"]
            elif pos == 3:
                colour = POSITION_RGB["P3"]
            else:
                colour = POSITION_RGB["POINTS"]
            print_rgb(f"{pos}.\t{driver} - {driver.points} pts", colour)
        else:
            print(f"{pos}.\t{driver} - {driver.points} pts")

    # === Final Constructor Standings ===
    constructor_results = sorted(constructors, key=lambda c: c.points, reverse=True)
    print("\n🏁 Constructors Championship Standings 🏁")
    for pos, constructor in enumerate(constructor_results, start=1):
        if colourise_enabled:
            colour = POSITION_RGB["POINTS"] if pos > 3 else POSITION_RGB[f"P{pos}"]
            print_rgb(f"{pos}.\t{constructor.name} - {constructor.points} pts", colour)
        else:
            print(f"{pos}.\t{constructor.name} - {constructor.points} pts")



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
    "Simulate a Race": True,
    "Simulate a Championship": True,
    "View current drivers": True,
    "View current teams": True,
    "View current tracks": True,
    "Settings": True,
    "Exit": True,
    "Max DNFs": True,
    "Toggle Colourise": True,
    "Back to Main Menu": True
}
settings_options = [
    f1.Setting("Max DNFs", 0),
    f1.Setting("Toggle Colourise", True)
]
constructor_lookup = {c.name: c for c in constructors}
colourise_enabled = bool(settings_options[1].value)  # default is ON

# === Constants ===
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
    "NO POINTS": (211, 211, 211),
    "DNF": (255, 0, 0)
}
TRACK_CHAOS = {
    "Melbourne Grand Prix Circuit": 15,
    "Shanghai International Circuit": 10,
    "Suzuka International Racing Course": 12,
    "Bahrain International Circuit": 8,
    "Jeddah Corniche Circuit": 20,
    "Miami International Autodrome": 12,
    "Autodromo Enzo e Dino Ferrari": 10,
    "Circuit de Monaco": 25,
    "Circuit de Barcelona-Catalunya": 8,
    "Circuit Gilles-Villeneuve": 15,
    "Red Bull Ring": 10,
    "Silverstone Circuit": 10,
    "Circuit de Spa-Francorchamps": 15,
    "Hungaroring": 12,
    "Circuit Zandvoort": 18,
    "Autodromo Nazionale Monza": 5,
    "Baku City Circuit": 20,
    "Marina Bay Street Circuit": 20,
    "Circuit of The Americas": 12,
    "Autodromo Hermanos Rodriguez": 15,
    "Autódromo José Carlos Pace": 15,
    "Las Vegas Strip Circuit": 18,
    "Losail International Circuit": 10,
    "Yas Marina Circuit": 12
}

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
                for driver in drivers:
                    driver.points = 0
                for team in constructors:
                    team.points = 0
                print("Select a track: ")
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
                inp3 = int(input("Selection: "))
                track = tracks[inp3 - 1]
                simulateRace(constructor_lookup, track, settings_options[0].value)
            case 2:
                for driver in drivers:
                    driver.points = 0
                for team in constructors:
                    team.points = 0
                simulateChampionship(constructor_lookup, settings_options[0].value)

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
                                inp2 = int(input("How many maximum DNFs (per race): (0-19) "))
                                clear_console()
                                if inp2 < 0 or inp2 > 19:
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