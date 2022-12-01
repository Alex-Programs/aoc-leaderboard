from flask import Flask, request, send_file, send_from_directory, render_template
from waitress import serve
import AOC
from config import get_config
import threading
import time
import datetime
from threading import Thread

dev = get_config()["dev"]

# Stateful info
class State():
    totalLeaderboardData = None
    todayLeaderboardData = None
    lastUpdatedLeaderboardData = None
    doEarlyRefresh = False
    doReload = False


def getWaitTime():
    if dev:
        return 150

    day = AOC.get_event_start_time().day

    # Change the amount of time between refresh over time
    if day == 1:
        return 20 * 60

    elif day < 5:
        return 15 * 60

    elif day < 10:
        return 8 * 60

    else:
        return 4 * 60


# Periodic update
def periodic_update_data():
    leaderboardID = get_config()["leaderboardID"]
    year = get_config()["year"]
    sessionCode = get_config()["sessionCode"]

    while True:
        refreshTime = getWaitTime()

        while True:
            error, total_leaderboard = AOC.get_total_leaderboard(leaderboardID, year, sessionCode)
            if not error:
                break

            print(f"ERROR: {str(total_leaderboard)}")

            time.sleep(20)

        while True:
            error, todays_leaderboard = AOC.get_todays_leaderboard(leaderboardID, year, sessionCode)
            if not error:
                break

            print(f"ERROR: {str(todays_leaderboard)}")

            time.sleep(20)

        State.totalLeaderboardData = total_leaderboard
        State.todayLeaderboardData = todays_leaderboard
        State.lastUpdatedLeaderboardData = time.time()

        while True:
            time.sleep(0.2)
            if State.doEarlyRefresh:
                print("Breaking due to early refresh!")
                State.doEarlyRefresh = False
                break

            # Do it one second earlier than you tell the clients you will
            if time.time() - refreshTime + 1 > State.lastUpdatedLeaderboardData:
                break


threading.Thread(target=periodic_update_data).start()

while State.lastUpdatedLeaderboardData is None:
    print("Waiting for initial data update...")
    time.sleep(0.1)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("leaderboard.html", leaderboardCode=get_config()["leaderboardCode"])


@app.route("/assets/<path:path>")
def serve_assets(path):
    return send_from_directory("assets/", path)


@app.route("/api/data")
def leaderboard():
    event_start = AOC.get_event_start_time()
    if event_start != "INVALID":
        event_start = str(event_start.day).rjust(2, "0")

    return {
        "total": State.totalLeaderboardData,
        "today": State.todayLeaderboardData,
        "lastUpdated": State.lastUpdatedLeaderboardData,
        "refreshTime": getWaitTime(),
        "day": event_start,
        "reload": State.doReload,
    }


@app.route("/api/reload_on")
def reload_on():
    State.doReload = True
    if not request.cookies.get("auth") or "gibaccess" not in request.cookies.get("auth"):
        return "No", 403
    def disable_after_delay():
        time.sleep(30)
        State.doReload = False

    threading.Thread(target=disable_after_delay).start()
    return "OK: Reload Enabled"

@app.route("/api/reload_off")
def reload_off():
    if not request.cookies.get("auth") or "gibaccess" not in request.cookies.get("auth"):
        return "No", 403
    State.doReload = False
    return "OK: Reload Disabled"

@app.route("/api/refresh")
def refresh():
    if not request.cookies.get("auth") or "gibaccess" not in request.cookies.get("auth"):
        return "No", 403
    State.doEarlyRefresh = True
    return "OK: Refresh Early"


@app.route("/api/admin")
def admin():
    if not request.cookies.get("auth") or "gibaccess" not in request.cookies.get("auth"):
        return "No", 403
    return render_template("admin.html")

@app.route("/api/reload_status")
def reload_status():
    return str(State.doReload)

if get_config()["dev"]:
    app.run(host="0.0.0.0", port=8095)

else:
    print("Serving on 0.0.0.0:8095")
    serve(app, host="0.0.0.0", port=8095)
