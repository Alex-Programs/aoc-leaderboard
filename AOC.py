import requests
import json
import datetime
import config
from random import choice
from dataclasses import dataclass
from tuner import score as score_time

dev = config.get_config()["dev"]


def gen_fake_leaderboard():
    def make_members(amount):
        members = {}

        for i in range(amount):
            uid = str(i)
            last_star_ts = 1575221560 + choice(range(-10000, 10000))
            name = "Fake Name " + str(i)
            stars = choice(range(1, 10))
            local_score = choice(range(1, 1000))
            completion_day_level = {}

            for i in range(0, 10):
                if choice([True, False]):
                    completion_day_level[str(i)] = {
                        "1": {"get_star_ts": last_star_ts - choice(range(100, 10000))},
                        "2": {"get_star_ts": last_star_ts}}

            global_score = choice(range(1, 1000))

            members[str(uid)] = {"id": uid, "last_star_ts": last_star_ts, "name": name, "stars": stars,
                                  "local_score": local_score, "completion_day_level": completion_day_level,
                                  "global_score": global_score}

        return members

    return {"members": make_members(100), "owner_id": "123456789", "event": "2019"}


def get_leaderboard(leaderboardID, year, sessionCode):
    if dev:
        return False, gen_fake_leaderboard()

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

    return False, sorted(leaderboard, key=lambda x: x.local_score, reverse=True)


@dataclass
class DayLeaderboardPosition():
    uid: str
    name: str
    stars: int
    star1_time: int
    star2_time: int
    points: int


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
        print(str(eventStartTime.strftime("%y-%m-%d")) + " " + str(dayExists))

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

            total_points = 0
            star1_mult = 200
            star2_mult = 500

            if stars >= 1:
                total_points += score_time(star1_time / 60) * star1_mult

            if stars == 2:
                total_points += score_time(star2_time / 60) * star2_mult

            leaderboard.append(DayLeaderboardPosition(uid, value["name"], stars, star1_time, star2_time, total_points))

    return False, leaderboard


def get_event_start_time():
    year = config.get_config()["year"]

    if dev:
        return datetime.datetime(year, 12, 1, 4)

    currentTime = datetime.datetime.now()

    month = currentTime.month
    day = currentTime.day

    if month != 12:
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

    print(str(get_total_leaderboard(data["leaderboardID"], data["year"], data["sessionCode"])))
    print(str(get_todays_leaderboard(data["leaderboardID"], data["year"], data["sessionCode"])))
