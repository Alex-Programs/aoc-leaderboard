from flask import Flask, request, send_file, send_from_directory, render_template
from waitress import serve
import AOC
from config import get_config
import threading
import time
from clientmanager import ClientManager
from functools import wraps
from log import log
import log as Logger
from flask_limiter import Limiter

dev = get_config()["dev"]

# Stateful info
class State():
    totalLeaderboardData = None
    todayLeaderboardData = None
    lastUpdatedLeaderboardData = None
    doEarlyRefresh = False

manager = ClientManager(120)

Logger.start_logging()

log("Starting server...")

def getWaitTime():
    if dev:
        return 150

    day = AOC.get_event_start_time().day

    current_month = time.localtime().tm_mon
    if current_month != 12:
        return 2 * 60

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

            log(f"ERROR: {str(total_leaderboard)}")

            time.sleep(20)

        while True:
            error, todays_leaderboard = AOC.get_todays_leaderboard(leaderboardID, year, sessionCode)
            if not error:
                break

            log(f"ERROR: {str(todays_leaderboard)}")

            time.sleep(20)

        State.totalLeaderboardData = total_leaderboard
        State.todayLeaderboardData = todays_leaderboard
        State.lastUpdatedLeaderboardData = time.time()

        while True:
            time.sleep(0.2)
            if State.doEarlyRefresh:
                log("Breaking due to early refresh!")
                State.doEarlyRefresh = False
                break

            # Do it one second earlier than you tell the clients you will
            if time.time() - refreshTime + 1 > State.lastUpdatedLeaderboardData:
                break


threading.Thread(target=periodic_update_data).start()

while State.lastUpdatedLeaderboardData is None:
    print("Waiting for data to be loaded...")
    time.sleep(1)

app = Flask(__name__)


def get_remote_address():
    if request.headers.get("CF-Connecting-IP"):
        return request.headers.get("CF-Connecting-IP")

    return request.remote_addr

limiter = Limiter(
    get_remote_address,    
    app=app,
    default_limits=["200000 per day", "50000 per hour"],
    storage_uri="memory://",
)

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

    decoded = manager.decode_data(request.args.get("uid"))

    print(str(decoded) + " - decoded data from client")

    manager.registerClientConnect(decoded["id"], request.headers.get("CF-Connecting-IP"), decoded)

    evaluations = manager.getClientEvaluations(decoded["id"])
    manager.clearClientEvaluations(decoded["id"])

    return {
        "total": State.totalLeaderboardData,
        "today": State.todayLeaderboardData,
        "lastUpdated": State.lastUpdatedLeaderboardData,
        "refreshTime": getWaitTime(),
        "day": event_start,
        "evaluate": evaluations,
        "reload": True,  # make old clients reload,
    }


def is_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.cookies.get("auth") != get_config()["adminKey"]:
            return render_template("login.html"), 401

        return f(*args, **kwargs)

    return decorated_function


@app.route("/admin")
@is_admin
def admin():
    return render_template("admin.html")


@app.route("/api/admin/admindata")
@is_admin
def clients():
    clientData = manager.getClients()
    return {"clients": clientData, "lastLogChange": Logger.Buffer.lastChangedTime,
            "lastClientChange": manager.lastChangeTime}


@app.route("/api/admin/logs/from/<int:fromLine>")
@is_admin
def pull_logs(fromLine):
    with open(get_config()["logfile"], "r") as f:
        lines = f.readlines()

    inBuffer = Logger.Buffer.data

    totalLogs = lines + inBuffer

    return {"logs": totalLogs[fromLine:]}


@app.route("/api/admin/evaluate", methods=["POST"])
@is_admin
def evaluate():
    data = request.get_json()
    manager.addClientEvaluation(data.get("uid"), data.get("code"))
    return "OK"


@app.route("/api/admin/refresh", methods=["POST"])
@is_admin
def refresh():
    State.doEarlyRefresh = True
    return "OK: Refresh Early"


@app.route("/login", methods=["POST"])
@limiter.limit("200 per day")
@limiter.limit("1 per second")
def login():
    jdata = request.get_json()

    if jdata.get("password") == get_config()["adminKey"]:
        resp = app.make_response({"success": True})
        resp.set_cookie("auth", get_config()["adminKey"])
        return resp

    return {"success": False}, 401


if get_config()["dev"]:
    log("Running in dev mode")
    app.run(host="127.0.0.1", port=8095)

else:
    log("Serving on 0.0.0.0:8095")
    serve(app, host="0.0.0.0", port=8095)