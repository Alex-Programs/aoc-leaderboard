import datetime
import time
import threading


class Buffer():
    data = []
    lastChangedTime = 0

def log(message):
    iso = datetime.datetime.now().isoformat()
    message = f"[{iso}] {message}"
    print(message)
    Buffer.data.append(message)
    Buffer.lastChangedTime = time.time()

def write_periodically():
    while True:
        time.sleep(10)
        data = Buffer.data.copy()
        Buffer.data.clear()
        if len(data) == 0:
            print("Nothing in logs to write")
            continue
        print("Writing to logs")
        with open("log.txt", "a") as f:
            toWrite = ""
            for message in data:
                toWrite += message.replace("\n", "[NEWLINE]") + "\n"

            f.write(toWrite)


def start_logging():
    t = threading.Thread(target=write_periodically)
    t.start()
