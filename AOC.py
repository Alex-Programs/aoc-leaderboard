import requests
import json
import datetime
import config
from random import choice
from dataclasses import dataclass
import tunerday
import tunertotal
import math
from log import log

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

    log("Gotten data: " + str(r.content))

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


def total_leaderboard_old(leaderboardID, year, sessionCode):
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


# Parse and return as dataclasses
def get_total_leaderboard(leaderboardID, year, sessionCode):
    if config.get_config()["doNewTotalLeaderboard"] == False:
        return total_leaderboard_old(leaderboardID, year, sessionCode)

    error, data = get_leaderboard(leaderboardID, year, sessionCode)
    if error:
        return True, data

    leaderboard = []
    for uid, value in data["members"].items():
        info = value

        name = info["name"]

        if not name:
            name = f"Anonymous {str(uid)}"

        sumScore = 0
        sumStars = 0

        star1_mult = 200
        star2_mult = 500

        for day, dayInfo in info["completion_day_level"].items():
            dayStartTime = datetime.datetime(year, 12, int(day) + 1, 4)
            star1Time = None
            star2Time = None

            if dayInfo.get("1"):
                star1Time = dayInfo["1"]["get_star_ts"] - dayStartTime.timestamp()
                star1Score = tunertotal.score(star1Time / 3600) * star1_mult
            else:
                star1Score = 0

            if dayInfo.get("2"):
                star2Time = dayInfo["2"]["get_star_ts"] - dayStartTime.timestamp()
                star2Score = tunertotal.score(star2Time / 3600) * star2_mult
            else:
                star2Score = 0

            totalScore = star1Score + star2Score

            stars = 0
            if star1Time:
                stars += 1

            if star2Time:
                stars += 1

            totalScore = totalScore

            sumScore += totalScore
            sumStars += stars

        leaderboard.append(TotalLeaderboardPosition(uid, name, sumStars, round(sumScore / 10)))

    return False, leaderboard


@dataclass
class DayLeaderboardPosition():
    uid: str
    name: str
    stars: int
    star1_time: int
    star2_time: int
    points: int
    star1_abs: int
    star2_abs: int


def process_points(star1_abs, star2_abs, dayStartTime)
    total_unadjusted = 0
    star1_mult = 200
    star2_mult = 500

    if star1_abs:
        star1_time = star1_abs - dayStartTime.timestamp()
        star1_score = tunerday.score(star1_time / 3600) * star1_mult
    else:
        star1_score = 0

    if star2_abs:
        star2_time = star2_abs - dayStartTime.timestamp()
        star2_score = tunerday.score(star2_time / 3600) * star2_mult
    else:
        star2_score = 0

    total_unadjusted = star1_score + star2_score

    

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

        if dayExists:
            data = dayCompletions[str(eventStartTime.day)]
            star1_time = None
            star2_time = None
            star1_abs = None
            star2_abs = None

            stars = 0
            if data.get("1"):
                stars += 1
                star1_time = data["1"]["get_star_ts"] - eventStartTime.timestamp()
                star1_abs = data["1"]["get_star_ts"]

            if data.get("2"):
                stars += 1
                star2_time = data["2"]["get_star_ts"] - eventStartTime.timestamp()
                star2_abs = data["2"]["get_star_ts"]

            star1_mult = 200
            star2_mult = 500

            star1_points = 0
            star2_points = 0

            if stars >= 1:
                star1_points = tunerday.score(star1_time / 3600) * star1_mult

            if stars == 2:
                star2_points = tunerday.score(star2_time / 3600) * star2_mult

            if star2_time and star1_time:
                delta = star2_time - star1_time
            else:
                delta = 1

            total_points = star1_points + star2_points

            print("POINTS - 1: " + total_points)
            print("POINTS - DELTA: " + delta)

            total_points = total_points / (delta / 100)

            print("POINTS - 2: " + total_points)

            total_points = round(total_points / 50)

            name = value["name"]
            if not name:
                name = f"Anonymous {str(uid)}"

            leaderboard.append(
                DayLeaderboardPosition(uid, name, stars, star1_time, star2_time, total_points, star1_abs, star2_abs))

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
