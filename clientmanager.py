from dataclasses import dataclass
from threading import Thread
import time
import base64
import json
from log import log

@dataclass
class Client():
    uid: str
    data: dict
    ip: str
    lastConnected: int
    evalMessages: list[int]

# Manages state for various clients, so that I can send them updates
class ClientManager():
    def __init__(self, dropTime):
        self.clients = []
        self.dropTime = dropTime
        Thread(target=self.continuousRemoveOldClients).start()

    def getClients(self):
        return self.clients

    def decode_data(self, uid):
        return json.loads(base64.b64decode(uid).decode("utf-8"))

    def registerClientConnect(self, uid, ip, data):
        for client in self.clients:
            if client.uid == uid:
                client.ip = ip
                client.lastConnected = time.time()
                return

        log("New client connected with uid " + str(uid) + " and ip " + str(ip) + " and data " + str(data))
        self.clients.append(Client(uid, data, ip, time.time(), ["console.log('Connected to server! Test evaluation.');"]))

    def getClientEvaluations(self, uid):
        for client in self.clients:
            if client.uid == uid:
                return client.evalMessages

        return []

    def clearClientEvaluations(self, uid):
        for client in self.clients:
            if client.uid == uid:
                client.evalMessages = []

    def addClientEvaluation(self, uid, code):
        log("Told to add client evaluation for uid " + uid + " with code " + code)
        for client in self.clients:
            if client.uid == uid or uid == "*":
                client.evalMessages.append(code)
                log("Found! Added evaluation.")
                if uid != "*":
                    return

        if uid != "*":
            log("Not found!")

    def removeOldClients(self):
        deleteList = [] # to make it all one operation. I could use a list comprehension, but then I wouldn't get to log it.
        for client in self.clients:
            if time.time() - client.lastConnected > self.dropTime:
                log("Planning to remove client with uid " + client.uid + " due to inactivity")
                deleteList.append(client)

        self.clients = [client for client in self.clients if not client in deleteList]

    def continuousRemoveOldClients(self):
        while True:
            self.removeOldClients()
            time.sleep(5)