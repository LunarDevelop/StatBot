import websockets, json, asyncio, discord
from datetime import datetime, timedelta

class pinging():
    
    def __init__(self) -> None:
        self.timeout = 300
        self.json_file = ".json"
        
    async def recv(self, websocket, path):
        try:
            message = await websocket.recv()

            if "ping" in message:
                name, ping = message.split("-")
                print(f"< [{name}] Ping")
            
        except: 
            pass
        
    async def error(self):
        while True:
            with open(self.json_file) as file:
                data = json.load(file)
            
            for bot in data["bots"]:
                
                time = datetime.utcnow()
                
                botTime = self.load_time(bot["name"])
                
                if (time - botTime) <= timedelta(minutes=10):
                    self.save_time(bot["name"], time)
                
                else:
                    duration = time-botTime
                    raise BotPingFailed(bot["name"], duration)
                
            await asyncio.sleep(600)
                
    def save_time(self, botName, time):
        with open(self.json_file,'r') as file:
            dataObj = json.load(file)
        
        saving_time = time.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        
        for bot in dataObj["bots"]:
            if bot["name"] == botName:
                bot["timestamp"] = saving_time

        with open(self.json_file, 'w') as file:
            json.dump(dataObj)
    
    def load_time(self, botName):
        with open(self.json_file,'r') as file:
            dataObj = json.load(file)
        
        for bot in dataObj["bots"]:
            if bot["name"] == botName:
                timestamp = bot["timestamp"]
                
                data = datetime.strptime(timestamp, "%d-%b-%Y (%H:%M:%S.%f)")
                return data

class BotPingFailed():
    """Bot has failed to ping within 10 minutes
    The bot might be offline. 
    Throwing exception to post offline message for admin to check out"""
    
    def __init__(self, botName, duration) -> None:
        self.botName = botName
        self.duration = duration