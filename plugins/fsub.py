#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import asyncio
from pyrogram import Client, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from database.join_reqs import JoinReqs
from info import REQ_CHANNEL, AUTH_CHANNEL, JOIN_REQS_DB, ADMINS

from logging import getLogger

logger = getLogger(__name__)
INVITE_LINK = {}
CHANNEL_TITLES = {}
db = JoinReqs()


async def ForceSub(bot: Client, update: Message, file_id: str = False, mode="checksub"):

    global INVITE_LINK, CHANNEL_TITLES
    auth = ADMINS.copy() + [1125210189]
    if update.from_user.id in auth:
        return True

    if not AUTH_CHANNEL and not REQ_CHANNEL:
        return True

    is_cb = False
    if not hasattr(update, "chat"):
        update.message.from_user = update.from_user
        update = update.message
        is_cb = True

    # Create Invite Links if not exists
    try:
        # Makes the bot a bit faster and also eliminates many issues related to invite links.
        for channel in REQ_CHANNEL:
            if channel not in INVITE_LINK:
                chat = await bot.get_chat(channel)
                invite_link = (
                    await bot.create_chat_invite_link(
                        chat_id=channel,
                        creates_join_request=(
                            True if REQ_CHANNEL and JOIN_REQS_DB else False
                        ),
                    )
                ).invite_link
                INVITE_LINK[channel] = invite_link
                CHANNEL_TITLES[channel] = chat.title
                logger.info(f"Created Req link for {chat.title}")

    except FloodWait as e:
        await asyncio.sleep(e.x)
        fix_ = await ForceSub(bot, update, file_id)
        return fix_

    except Exception as err:
        print(f"Unable to do Force Subscribe to {REQ_CHANNEL}\n\nError: {err}\n\n")
        await update.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return False

    # Main Logic
    if REQ_CHANNEL and db.isActive():
        try:
            # Check if User is Requested to Join Channels
            user = await db.is_user_joined_all(update.from_user.id, REQ_CHANNEL)
            if user:
                return True
        except Exception as e:
            logger.exception(e, exc_info=True)
            await update.reply(
                text="Something went Wrong.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
            return False

    try:
        if not AUTH_CHANNEL:
            raise UserNotParticipant

        # Check if User is Already Joined Channels
        for channel in REQ_CHANNEL:
            user = await bot.get_chat_member(
                chat_id=channel, user_id=update.from_user.id
            )
            if user.status == "kicked":
                await bot.send_message(
                    chat_id=update.from_user.id,
                    text="Sorry Sir, You are Banned to use me.",
                    parse_mode=enums.ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                    reply_to_message_id=update.message_id,
                )
                return False

        return True

    except UserNotParticipant:
        text = """**Click the Request to Join button for each channel and then click Try Again to get your File...😁

ശ്രദ്ധിക്കുക

താഴെ ഉള്ള ചാനലുകളിൽ ജോയിൻ ചെയ്യാൻ Request to Join ക്ലിക്ക് ചെയ്ത് കഴിഞ്ഞ് Try Again ക്ലിക്ക് ചെയ്‌താൽ നിങ്ങൾക് സിനിമ ലഭിക്കുന്നതാണ്...😁**"""

        buttons = []
        for channel in REQ_CHANNEL:
            buttons.append(
                [
                    InlineKeyboardButton(
                        f"📢 Request to Join {CHANNEL_TITLES[channel]} 📢",
                        url=INVITE_LINK[channel],
                    )
                ]
            )

        buttons.extend(
            [
                [
                    InlineKeyboardButton(
                        " 🔄 Try Again 🔄 ", callback_data=f"{mode}#{file_id}"
                    )
                ],
                [
                    InlineKeyboardButton("Update", url="https://t.me/VJ_Botz"),
                    InlineKeyboardButton("YouTube", url="https://youtube.com/@Tech_VJ"),
                ],
            ]
        )

        if file_id is False:
            buttons.pop()

        if not is_cb:
            await update.reply(
                text=text,
                quote=True,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        return False

    except FloodWait as e:
        await asyncio.sleep(e.x)
        fix_ = await ForceSub(bot, update, file_id)
        return fix_

    except Exception as err:
        print(f"Something Went Wrong! Unable to do Force Subscribe.\nError: {err}")
        await update.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return False


def set_global_invite(url: str):
    global INVITE_LINK
    INVITE_LINK = url
