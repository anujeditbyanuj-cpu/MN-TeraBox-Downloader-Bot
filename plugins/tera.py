# please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN

import os
import asyncio
import aiohttp
import tempfile

from urllib.parse import (
    urlencode,
    urlparse,
    parse_qs
)

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from pymongo import MongoClient

from verify_patch import (
    IS_VERIFY,
    is_verified,
    build_verification_link,
    HOW_TO_VERIFY
)

from config import CHANNEL, DATABASE

# =========================================
# MongoDB
# =========================================

mongo_client = MongoClient(DATABASE.URI)
db = mongo_client[DATABASE.NAME]

# =========================================
# Regex
# =========================================

TERABOX_REGEX = r"https?://(?:www\.)?[^/\s]*tera[^/\s]*\.[a-z]+/s/[^\s]+"

# =========================================
# Cookie
# =========================================

COOKIE = "ndus=YOUR_COOKIE_HERE"

# =========================================
# Headers
# =========================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/135.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.terabox.com/",
    "Origin": "https://www.terabox.com",
    "Connection": "keep-alive",
    "Cookie": COOKIE
}

DL_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/135.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.terabox.com/",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Cookie": COOKIE
}

# =========================================
# Utils
# =========================================

def get_size(size):

    if size >= 1024**3:
        return f"{size / 1024**3:.2f} GB"

    elif size >= 1024**2:
        return f"{size / 1024**2:.2f} MB"

    elif size >= 1024:
        return f"{size / 1024:.2f} KB"

    return f"{size} B"


def find_between(text, start, end):

    try:
        return text.split(start, 1)[1].split(end, 1)[0]
    except:
        return ""

# =========================================
# Session Creator
# =========================================

def create_session(headers):

    connector = aiohttp.TCPConnector(
        ssl=False,
        limit=20,
        ttl_dns_cache=300
    )

    timeout = aiohttp.ClientTimeout(
        total=600
    )

    return aiohttp.ClientSession(
        headers=headers,
        connector=connector,
        timeout=timeout
    )

# =========================================
# Get File Info
# =========================================

async def get_file_info(url):

    async with create_session(HEADERS) as session:

        async with session.get(
            url,
            allow_redirects=True
        ) as resp:

            if resp.status != 200:
                raise Exception(
                    f"Invalid Link ({resp.status})"
                )

            final_url = str(resp.url)

        parsed = urlparse(final_url)

        surl = parse_qs(parsed.query).get(
            "surl",
            [None]
        )[0]

        if not surl:
            raise Exception(
                "Failed To Get SURL"
            )

        async with session.get(final_url) as page:
            html = await page.text()

        js_token = find_between(
            html,
            'fn%28%22',
            '%22%29'
        )

        logid = find_between(
            html,
            'dp-logid=',
            '&'
        )

        bdstoken = find_between(
            html,
            'bdstoken":"',
            '"'
        )

        if not all([js_token, logid, bdstoken]):
            raise Exception(
                "Failed To Extract Tokens"
            )

        params = {
            "app_id": "250528",
            "web": "1",
            "channel": "dubox",
            "clienttype": "0",
            "jsToken": js_token,
            "dp-logid": logid,
            "page": "1",
            "num": "20",
            "by": "name",
            "order": "asc",
            "site_referer": final_url,
            "shorturl": surl,
            "root": "1"
        }

        api = (
            "https://www.terabox.app/share/list?"
            + urlencode(params)
        )

        async with session.get(api) as r:
            data = await r.json()

        if data.get("errno") != 0:
            raise Exception(
                data.get("errmsg", "API Error")
            )

        files = data.get("list")

        if not files:
            raise Exception(
                "No Files Found"
            )

        file = files[0]

        return {
            "name": file.get(
                "server_filename",
                "file"
            ),
            "size": int(
                file.get("size", 0)
            ),
            "size_text": get_size(
                int(file.get("size", 0))
            ),
            "dlink": file.get("dlink")
        }

# =========================================
# Download File
# =========================================

async def download_file(url, path):

    async with create_session(DL_HEADERS) as session:

        async with session.get(url) as resp:

            if resp.status != 200:
                raise Exception(
                    f"Download Failed ({resp.status})"
                )

            with open(path, "wb") as f:

                async for chunk in resp.content.iter_chunked(
                    1024 * 1024
                ):
                    f.write(chunk)

# =========================================
# Main Handler
# =========================================

@Client.on_message(
    filters.private &
    filters.regex(TERABOX_REGEX)
)
async def terabox_handler(
    client: Client,
    message: Message
):

    user_id = message.from_user.id

    # =====================================
    # Verification
    # =====================================

    if IS_VERIFY and not await is_verified(user_id):

        verify_url = await build_verification_link(
            client.me.username,
            user_id
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ Verify",
                        url=verify_url
                    ),
                    InlineKeyboardButton(
                        "📖 Tutorial",
                        url=HOW_TO_VERIFY
                    )
                ]
            ]
        )

        return await message.reply_text(
            "🔐 Verification Required\n\n"
            "⏳ Verification Valid For 12 Hours.",
            reply_markup=buttons
        )

    url = message.text.strip()

    processing = await message.reply_text(
        "🔍 Fetching File Info..."
    )

    temp_path = None

    try:

        # =====================================
        # Get File Info
        # =====================================

        info = await get_file_info(url)

        file_name = info["name"]
        file_size = info["size_text"]
        dlink = info["dlink"]

        await processing.edit_text(
            f"📥 Downloading...\n\n"
            f"📄 {file_name}\n"
            f"📦 {file_size}"
        )

        # =====================================
        # Temp File
        # =====================================

        temp_dir = tempfile.gettempdir()

        temp_path = os.path.join(
            temp_dir,
            file_name
        )

        # =====================================
        # Download
        # =====================================

        await download_file(
            dlink,
            temp_path
        )

        caption = (
            f"📄 File Name: {file_name}\n"
            f"📦 Size: {file_size}\n\n"
            f"🔗 {url}"
        )

        # =====================================
        # Log Channel Upload
        # =====================================

        if CHANNEL.ID:

            try:

                await client.send_document(
                    chat_id=CHANNEL.ID,
                    document=temp_path,
                    caption=caption,
                    file_name=file_name
                )

            except:
                pass

        # =====================================
        # User Upload
        # =====================================

        sent = await client.send_document(
            chat_id=message.chat.id,
            document=temp_path,
            caption=caption,
            file_name=file_name,
            protect_content=True
        )

        await processing.delete()

        await message.reply_text(
            "✅ Uploaded Successfully\n\n"
            "🗑 File Will Auto Delete In 12 Hours."
        )

        # =====================================
        # Auto Delete
        # =====================================

        await asyncio.sleep(43200)

        try:
            await sent.delete()
        except:
            pass

    except Exception as e:

        await processing.edit_text(
            f"❌ Error:\n\n{e}"
        )

    finally:

        try:

            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

        except:
            pass
