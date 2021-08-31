import os
import time

from asyncio.streams import start_server
import websockets
import json
import asyncio
import requests
import os
from datetime import date, datetime, timedelta

from main import run

while 1:
    run()
    print("Restarting...")
    time.sleep(1)
