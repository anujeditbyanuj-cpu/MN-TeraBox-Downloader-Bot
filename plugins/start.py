# please give credits https://github.com/MN-BOTS
# @MrMNTG @MusammilN

from pyrogram import Client as MN_Bot
from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from verify_patch import (
    IS_VERIFY,
    validate_token_and_verify,
    is_verified,
    build_verification_link,
    HOW_TO_VERIFY
)

# =========================
# Texts
# =========================

class TEXT:

    START = """
<b>👋 Welcome To MN Terabox Downloader</b>

📥 Send Any Terabox Link To Download

⚡ Features:
• Fast Download
• Auto Upload
• Protected Files
• Auto Delete After 12 Hours

⚠️ Only Files Under 2GB Supported
"""

    VERIFIED = """
✅ <b>Verification Successful</b>

You Can Now Use The Bot For 12 Hours.
"""

    INVALID = """
❌ <b>Invalid Or Expired Verification Link</b>
"""

    VERIFY_REQUIRED = """
🔐 <b>Verification Required</b>

Please Verify Yourself Before Using The Bot.

⏳ Verification Valid For 12 Hours.
"""

# =========================
# Buttons
# =========================

class BUTTONS:

    START_BTN = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "👨‍💻 Developer",
                    url="https://t.me/anujedits76"
                )
            ],
            [
                InlineKeyboardButton(
                    "📢 Updates",
                    url="https://t.me/logs_akbot"
                ),
                InlineKeyboardButton(
                    "💬 Support",
                    url="https://t.me/logs_akbot"
                )
            ]
        ]
    )

# =========================
# Start Command
# =========================

@MN_Bot.on_message(filters.command("start") & filters.private)
async def start(client: MN_Bot, message: Message):

    user_id = message.from_user.id

    args = message.text.split()

    # =========================
    # Verify Token
    # =========================

    if len(args) > 1 and args[1].startswith("verify_"):

        token = args[1].split("_", 1)[1]

        verified = await validate_token_and_verify(
            user_id,
            token
        )

        if verified:

            return await message.reply_text(
                TEXT.VERIFIED
            )

        return await message.reply_text(
            TEXT.INVALID
        )

    # =========================
    # Verification Check
    # =========================

    if IS_VERIFY:

        verified = await is_verified(user_id)

        if not verified:

            verify_link = await build_verification_link(
                client.me.username,
                user_id
            )

            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "✅ Verify Now",
                            url=verify_link
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "📖 Verification Guide",
                            url=HOW_TO_VERIFY
                        )
                    ]
                ]
            )

            return await message.reply_text(
                TEXT.VERIFY_REQUIRED,
                disable_web_page_preview=True,
                reply_markup=buttons
            )

    # =========================
    # Start Message
    # =========================

    await message.reply_text(
        TEXT.START,
        disable_web_page_preview=True,
        reply_markup=BUTTONS.START_BTN
    )
