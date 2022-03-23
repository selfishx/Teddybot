import os
import re
from platform import python_version as kontol
from telethon import events, Button
from telegram import __version__ as telever
from telethon import __version__ as tlhver
from pyrogram import __version__ as pyrover
from SiestaRobot.events import register
from SiestaRobot import telethn as tbot


PHOTO = "https://telegra.ph/file/ff2fa22dfa6ae838cc6cd.jpg"

@register(pattern=("/alive"))
async def awake(event):
  TEXT = f"**Hi [{event.sender.first_name}](tg://user?id={event.sender.id}), I'm Teddy Robot.** \n\n"
  TEXT += "💠 **I'м ωσякιиg ωιтн ѕємχу ѕρєє∂** \n\n"
  TEXT += f"💠 **Mу мαѕтєя : [Suru](https://t.me/sweetttu_1)** \n\n"
  TEXT += f"💠 **Lιвяαяу νєяѕισи :** `{telever}` \n\n"
  TEXT += f"💠 **Tєℓєтнσи νєяѕισи :** `{tlhver}` \n\n"
  TEXT += f"💠 **Pуяσgяαм νєяѕισи :** `{pyrover}` \n\n"
  TEXT += "**Tнαикѕ fσя α∂∂ιиg мє нєяє ❤️**"
  BUTTON = [[Button.url("Help", "https://t.me/TeddyxRobot_bot?start=help"), Button.url("Support", "https://t.me/XO_XPAM")]]
  await tbot.send_file(event.chat_id, PHOTO, caption=TEXT,  buttons=BUTTON)
