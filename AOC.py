import requests
import json
import datetime
import config
from dataclasses import dataclass

dev = config.get_config()["dev"]


def get_leaderboard(leaderboardID, year, sessionCode):
    url = f"https://adventofcode.com/{str(year)}/leaderboard/private/view/{str(leaderboardID)}.json"
    r = requests.get(url, cookies={"session": sessionCode})

    print(str(r.content))

    if r.status_code == 200:
        try:
            return False, json.loads(r.content)
        except json.decoder.JSONDecodeError:
            return True, "ERROR: Invalid Session Code"

    return True, "ERROR: " + str(r.status_code)


@dataclass
class TotalLeaderboardPosition():
    uid: str
    name: str
    stars: int
    local_score: float


# Parse and return as dataclasses
def get_total_leaderboard(leaderboardID, year, sessionCode):
    error, data = get_leaderboard(leaderboardID, year, sessionCode)
    if error:
        return True, data

    leaderboard = []

    for uid, value in data["members"].items():
        info = value

        name = info["name"]
        stars = info["stars"]
        local_score = info["local_score"]

        leaderboard.append(TotalLeaderboardPosition(uid, name, stars, local_score))

    return False, leaderboard


@dataclass
class DayLeaderboardPosition():
    uid: str
    name: str
    stars: int
    star1_time: int
    star2_time: int


def get_todays_leaderboard(leaderboardID, year, sessionCode):
    error, data = get_leaderboard(leaderboardID, year, sessionCode)
    if error:
        return True, data

    leaderboard = []

    eventStartTime = get_event_start_time()

    if eventStartTime == "INVALID":
        return True, "Invalid time"

    for uid, value in data["members"].items():
        dayCompletions = value["completion_day_level"]

        dayExists = dayCompletions.get(str(eventStartTime.day))
        print(str(eventStartTime.day), dayCompletions)

        if dayExists:
            data = dayCompletions[str(eventStartTime.day)]
            star1_time = None
            star2_time = None

            stars = 0
            if data.get("1"):
                stars += 1
                star1_time = data["1"]["get_star_ts"] - eventStartTime.timestamp()

            if data.get("2"):
                stars += 1
                star2_time = data["1"]["get_star_ts"] - eventStartTime.timestamp()

            leaderboard.append(DayLeaderboardPosition(uid, value["name"], stars, star1_time, star2_time))

    return False, leaderboard


def get_event_start_time():
    year = config.get_config()["year"]

    if dev:
        return datetime.datetime(year, 11, 1, 4)

    currentTime = datetime.datetime.now()

    month = currentTime.month
    day = currentTime.day

    if month != 11:
        return "INVALID"

    if currentTime.hour < 4:
        if day == 1:
            return "INVALID"
        return datetime.datetime(year, month, day - 1, 4)

    # Account for being 4 UTC
    return datetime.datetime(year, month, day, 4)


if __name__ == "__main__":
    data = config.get_config()

    print(str(get_leaderboard(data["leaderboardID"], data["year"], data["sessionCode"])))

    print(str(get_event_start_time()))

    print(str(get_total_leaderboard(data["leaderboardID"], data["year"], data["sessionCode"])))
    print(str(get_todays_leaderboard(data["leaderboardID"], data["year"], data["sessionCode"])))
