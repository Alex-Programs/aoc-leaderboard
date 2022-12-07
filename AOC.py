import requests
import json
import datetime
import config
from random import choice
from dataclasses import dataclass
import tunerday
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


def get_deltas(data, day):
    deltas = []

    for uid, value in data["members"].items():
        dayCompletions = value["completion_day_level"]

        dayExists = dayCompletions.get(str(day))

        if dayExists:
            data = dayCompletions[str(day)]
            star1_time = None
            star2_time = None

            if data.get("1"):
                star1_time = data["1"]["get_star_ts"]

            if data.get("2"):
                star2_time = data["2"]["get_star_ts"]

            if star2_time and star1_time:
                deltas.append(star2_time - star1_time)

    return deltas

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

        for day, dayInfo in info["completion_day_level"].items():
            dayStartTime = datetime.datetime(year, 12, int(day) + 1, 4)
            star1Time = None
            star2Time = None

            if dayInfo.get("1"):
                star1Time = dayInfo["1"]["get_star_ts"]

            if dayInfo.get("2"):
                star2Time = dayInfo["2"]["get_star_ts"]

            points = process_points(star1Time, star2Time, dayStartTime, tunerday.score, dayStartTime.day, get_deltas(data, day),name)

            stars = 0
            if star1Time:
                stars += 1

            if star2Time:
                stars += 1

            sumScore += points
            sumStars += stars

        leaderboard.append(TotalLeaderboardPosition(uid, name, sumStars, sumScore))

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


def process_points(star1_abs, star2_abs, dayStartTime, score_func, day, deltas, name=None):
    star1_mult = 200
    star2_mult = 600

    if star1_abs:
        star1_time = star1_abs - dayStartTime.timestamp()
        star1_score = score_func(star1_time / 3600) * star1_mult
    else:
        star1_score = 0

    if star2_abs:
        star2_time = star2_abs - dayStartTime.timestamp()
        star2_score = score_func(star2_time / 3600) * star2_mult
    else:
        star2_score = 0

    total_unadjusted = star1_score + star2_score

    deltaTime = None

    if star1_abs and star2_abs:
        deltaTime = star2_abs - star1_abs

    if deltaTime:
        # Control time is the median of the top group (before the jump to the next group > 2.5x the existing median)
        topGroup = []
        for index, element in enumerate(sorted(deltas)):
            if index == 0:
                topGroup.append(element)
                continue

            median = topGroup[math.floor(len(topGroup) / 2)]
            if element > median * 2.5:
                break

            topGroup.append(element)

        if len(topGroup) > 1:
            controlTime = topGroup[math.floor(len(topGroup) / 2)]
        else:
            controlTime = topGroup[0]

        log("CONTROL TIME: " + str(controlTime))
        log("DELTA TIME: " + str(deltaTime))

        deltaTimeSegment = deltaTime / controlTime

        deltaTimeSegment = score_func(deltaTimeSegment * 24) * 150

        # Shouldn't be needed
        deltaTimeSegment = max(0, deltaTimeSegment)

        # Delta segment is your delta time divided by the control time
        log(name)
        log("Delta time segment: " + str(deltaTimeSegment))
        normalSegment = total_unadjusted
        log("Normal segment:     " + str(normalSegment))
        log("_------_")
        total_adjusted = normalSegment + deltaTimeSegment
    else:
        total_adjusted = total_unadjusted

    total_adjusted = round(total_adjusted / 50)

    return total_adjusted


def get_todays_leaderboard(leaderboardID, year, sessionCode):
    error, data = get_leaderboard(leaderboardID, year, sessionCode)
    origdata = data
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

            stars = 0
            if data.get("1"):
                stars += 1
                star1_time = data["1"]["get_star_ts"]

            if data.get("2"):
                stars += 1
                star2_time = data["2"]["get_star_ts"]

            name = value["name"]
            if not name:
                name = f"Anonymous {str(uid)}"

            score = process_points(star1_time, star2_time, eventStartTime, tunerday.score, eventStartTime.day, get_deltas(origdata, eventStartTime.day), name)

            leaderboard.append(
                DayLeaderboardPosition(uid, name, stars, star1_time - eventStartTime.timestamp(),
                                       star2_time - eventStartTime.timestamp(), score, star1_time, star2_time))

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
