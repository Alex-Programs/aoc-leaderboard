from flask import Flask, request, send_file, send_from_directory, render_template
from waitress import serve
import AOC
from config import get_config
import threading
import time
import datetime


# Stateful info
class State():
    totalLeaderboardData = None
    todayLeaderboardData = None
    lastUpdatedLeaderboardData = None


# Periodic update
def periodic_update_data():
    leaderboardID = get_config()["leaderboardID"]
    year = get_config()["year"]
    sessionCode = get_config()["sessionCode"]

    while True:
        day = datetime.datetime.now().day
        # Change the amount of time between refresh over time
        if day == 1:
            refreshTime = (20 * 60)

        elif day < 5:
            refreshTime = (15 * 60)

        elif day < 10:
            refreshTime = (12 * 60)

        elif day < 25:
            refreshTime = (5 * 60)

        while True:
            error, total_leaderboard = AOC.get_total_leaderboard(leaderboardID, year, sessionCode)
            if not error:
                break

            time.sleep(120)

        while True:
            error, todays_leaderboard = AOC.get_todays_leaderboard(leaderboardID, year, sessionCode)
            if not error:
                break

            time.sleep(120)

        State.totalLeaderboardData = total_leaderboard
        State.todayLeaderboardData = todays_leaderboard
        State.lastUpdatedLeaderboardData = time.time()

        time.sleep(refreshTime)


threading.Thread(target=periodic_update_data).start()

while State.lastUpdatedLeaderboardData is None:
    print("Waiting for initial data update...")
    time.sleep(1)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/assets/<path:path>")
def serve_assets(path):
    return send_from_directory("assets/", path)
