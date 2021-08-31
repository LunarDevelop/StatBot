from asyncio.streams import start_server
import websockets
import json
import asyncio
import requests
import os
from datetime import date, datetime, timedelta


timeout = 10  # in minutes
json_file = ".json"
auth_file = "auth.json"


class BotPingFailed(Exception):
    """Bot has failed to ping within 10 minutes
    The bot might be offline. 
    Throwing exception to post offline message for admin to check out"""

    def __init__(self, botName, duration) -> None:
        self.botName = botName
        self.duration = duration


def open_file():
    with open(json_file, 'r') as f:
        return json.load(f)


def save_file(data):
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)


class clientClass():

    async def recv(self, websocket, path):
        message = await websocket.recv()
        print(f"< {message}")

        data = json.loads(message)

        try:

            if data["type"].lower() == "ping":
                pong = {
                    "type": "pong"
                }
                await self.send(websocket, str(pong))
                return

            elif data["type"].lower() == "restart":
                quit()

            elif data["type"] == "01":
                """Heartbeat message received by client"""

                time = datetime.utcnow()
                botName = data["data"]["botName"]

                self.save_time(botName, time)

                sendData = {
                    "type": "02",
                    "data": {
                        "message": f"Heartbeat Received for {botName}"
                    }
                }

                await self.send(websocket, sendData)

            elif data["type"] == "04":
                jData = open_file()

                for bot in jData["bots"]:
                    if bot["botName"] == data["data"]["botName"].lower():
                        try:
                            bot["commandCount"] += 1

                        except KeyError:
                            bot["commandCount"] = 1

                        save_file(jData)

                        message = {
                            "type": "03",
                            "data": {
                                "message": f'Command has been executed on {data["data"]["botName"]} and updated bot info'
                            }
                        }

                        await self.send(websocket, message)

                        return

            elif data["type"] == "05":
                raise NotImplementedError

            elif data["type"] == "06":
                raise NotImplementedError

            elif data["type"] == "07":
                raise NotImplementedError

            elif data["type"] == "08":
                raise NotImplementedError

            elif data["type"] == "09":
                dataObj = open_file()
                botName = data["data"]["botName"]

                time = datetime.utcnow()
                saving_time = time.strftime("%d-%m-%Y (%H:%M:%S)")

                botFound = False

                for bot in dataObj["bots"]:
                    if bot["botName"] == botName.lower():
                        bot["uptime"] = saving_time
                        botFound = True
                        break

                if not botFound:

                    botData = {
                        "botName": botName.lower(),
                        "uptime": saving_time
                    }

                    dataObj["bots"].append(botData)

                save_file(dataObj)

                message = {
                    "type": "03",
                            "data": {
                                "message": f'Uptime mark received, {data["data"]["botName"]}, and updated bot info'
                            }
                }

                await self.send(websocket, message)

            elif data["type"] == "10":
                dataObj = open_file()
                botName = data["data"]["botName"]

                for bot in dataObj["bots"]:
                    if bot["botName"] == botName.lower():

                        uptime = bot["uptime"]
                        uptimeDatetime = datetime.strptime(
                            uptime, "%d-%m-%Y (%H:%M:%S)")
                        currentTime = datetime.utcnow()

                        duration = currentTime - uptimeDatetime

                        a = duration.seconds//3600
                        b = (duration.seconds % 3600)//60
                        c = (duration.seconds % 3600) % 60

                        message = {
                            "type": "03",
                            "data": {
                                "uptime": f"{duration.days}:{a}:{b}:{c}",
                                "message": f"{botName} has been online since {uptime}"
                            }
                        }

                        await self.send(websocket, message)

            elif data["type"] == "1001":
                raise NotImplementedError

            elif data["type"] == "1002":
                raise NotImplementedError

            elif data["type"] == "1003":
                raise NotImplementedError

            elif data["type"] == "1004":
                raise NotImplementedError

        except NotImplementedError:

            message = {
                "type": "501",
                "data": {
                    "message": "This feature is not yet implemented into the websocket yet"
                }
            }

            await self.send(websocket, message)

    async def send(self, websocket, message):
        """Sends a message to client"""

        await websocket.send(str(message))

        print(f"> {message}")

    async def error(self):
        while True:
            duration = 0
            with open(json_file) as file:
                data = json.load(file)

            for bot in data["bots"]:
                time = datetime.utcnow()

                botTime = self.load_time(bot["botName"])
                duration = time-botTime

                try:
                    if duration <= timedelta(minutes=timeout):
                        pass

                    else:

                        raise BotPingFailed(bot["botName"], duration)

                except BotPingFailed:
                    a = duration.seconds//3600
                    b = (duration.seconds % 3600)//60
                    c = (duration.seconds % 3600) % 60
                    duration = timedelta(hours=a, minutes=b, seconds=c)
                    datetimeDuration = datetime.strptime(
                        str(duration), "%H:%M:%S")
                    stringDuration = datetimeDuration.strftime("%H:%M:%S")

                    webhook_failed = {
                        "content": "",
                        "embeds": [
                            {
                                "title": f'Connection Failed | {bot["botName"]}',
                                "description": "<@268035643760836608>***, FIX NOW!!***",  # Tags Solar for attention
                                "color": 16711714,
                                "fields": [
                                    {
                                        "name": "Bot Name",
                                        "value": f'{bot["botName"]}'
                                    },
                                    {
                                        "name": "Down Time",
                                        "value": f"{str(stringDuration)}"
                                    }
                                ],
                                "author": {
                                    "name": "Status Bot",
                                    "icon_url": "https://imgur.com/wlTPzmM.png"
                                },
                                "thumbnail": {
                                    "url": "https://i.imgur.com/OLKMWlj.png"
                                }
                            }
                        ]
                    }

                    request = requests.post(
                        url="Enter Webhook key from Discord", json=webhook_failed)

                    if request.ok:
                        print("> Webhook Failed Connection Send")

                    else:
                        print("> Webhook Failed Connection Failed To Send")

            await asyncio.sleep(900)

    def save_time(self, botName, time):
        with open(json_file, 'r') as file:
            dataObj = json.load(file)

        saving_time = time.strftime("%d-%m-%Y (%H:%M:%S)")

        botFound = False

        for bot in dataObj["bots"]:
            if bot["botName"] == botName.lower():
                bot["timestamp"] = saving_time
                botFound = True
                break

        if not botFound:

            botData = {
                "botName": botName.lower(),
                "timestamp": saving_time
            }

            dataObj["bots"].append(botData)

        with open(json_file, 'w') as file:
            json.dump(dataObj, file, indent=4)

    def load_time(self, botName):
        with open(json_file, 'r') as file:
            dataObj = json.load(file)

        for bot in dataObj["bots"]:
            if bot["botName"] == botName.lower():
                timestamp = bot["timestamp"]

                data = datetime.strptime(timestamp, "%d-%m-%Y (%H:%M:%S)")
                return data


def run():
    # Rest of the code
    client = clientClass()

    startServer = websockets.serve(client.recv, "localhost", 8765)

    tasks = [
        asyncio.ensure_future(client.error()),
        asyncio.ensure_future(startServer)
    ]

    loop = asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
    loop = asyncio.get_event_loop().run_forever()
