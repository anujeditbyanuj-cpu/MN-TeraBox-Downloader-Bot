import logging
import threading

from flask import Flask
from pyrogram import Client

from config import BOT, API, OWNER

# =========================
# Logging
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] %(message)s"
)

logging.getLogger("pyrogram").setLevel(logging.ERROR)

# =========================
# Flask App
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "MN Bot Running Successfully ✅"

def run_flask():
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
    )

# =========================
# Bot Client
# =========================

class MN_Bot(Client):

    def __init__(self):

        super().__init__(
            name="MN-Bot",
            api_id=API.ID,
            api_hash=API.HASH,
            bot_token=BOT.TOKEN,
            plugins=dict(root="plugins"),
            workers=50,
            sleep_threshold=30
        )

    async def start(self):

        await super().start()

        me = await self.get_me()

        self.username = me.username
        self.mention = me.mention

        BOT.USERNAME = f"@{me.username}"

        logging.info(f"{me.first_name} Started Successfully")

        try:
            await self.send_message(
                OWNER.ID,
                f"✅ {me.first_name} Started Successfully"
            )
        except Exception as e:
            logging.error(f"Owner Message Error: {e}")

    async def stop(self, *args):

        await super().stop()

        logging.info("Bot Stopped")

# =========================
# Main
# =========================

if __name__ == "__main__":

    flask_thread = threading.Thread(target=run_flask)

    flask_thread.start()

    MN_Bot().run()
