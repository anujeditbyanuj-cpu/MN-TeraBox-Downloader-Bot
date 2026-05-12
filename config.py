from dotenv import load_dotenv
load_dotenv()

import os

class BOT:
    TOKEN = os.environ.get("TOKEN", "8726665578:AAHLSN3AxqWoRzeSJU2oV4Bm4QPfKKSkPKo")

class API:
    HASH = os.environ.get("API_HASH", "8dc570c08d8e35e88fb9bfc73c65d7fa")
    ID = int(os.environ.get("API_ID", 34446649))

class OWNER:
    ID = int(os.environ.get("OWNER", 7892805795))

class CHANNEL:
    ID = int(os.environ.get("CHANNEL_ID", -1003475522251))

class WEB:
    PORT = int(os.environ.get("PORT", 9090))

class DATABASE:
    URI = os.environ.get("DB_URI", "mongodb+srv://Anujedit:Anujedit@cluster0.7cs2nhd.mongodb.net/?appName=Cluster0")
    NAME = os.environ.get("DB_NAME", "Anujedit")
