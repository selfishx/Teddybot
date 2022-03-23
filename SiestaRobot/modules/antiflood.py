import html
from typing import Optional, List
import re

from telegram import Message, Chat, Update, User, ChatPermissions

from SiestaRobot import TIGERS, WOLVES, dispatcher
from SiestaRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    is_user_admin,
    user_admin,
    user_admin_no_reply,
)
from SiestaRobot.modules.log_channel import loggable
from SiestaRobot.modules.sql import antiflood_sql as sql
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import mention_html
from SiestaRobot.modules.helper_funcs.string_handling import extract_time
from SiestaRobot.modules.connection import connected
from SiestaRobot.modules.helper_funcs.alternate import send_message
from SiestaRobot.modules.sql.approve_sql import is_approved
from SiestaRobot.modules.language import gs

FLOOD_GROUP = 3


@loggable
def check_flood(update, context) -> str:
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]
    msg = update.effective_message  # type: Optional[Message]
    if not user:  # ignore channels
        return ""

    # ignore admins and whitelists
    if is_user_admin(chat, user.id) or user.id in WOLVES or user.id in TIGERS:
        sql.update_flood(chat.id, None)
        return ""
    # ignore approved users
    if is_approved(chat.id, user.id):
        sql.update_flood(chat.id, None)
        return
    should_ban = sql.update_flood(chat.id, user.id)
    if not should_ban:
        return ""

    try:
        getmode, getvalue = sql.get_flood_setting(chat.id)
        if getmode == 1:
            chat.kick_member(user.id)
            execstrings = "Bαииє∂"
            tag = "BANNED"
        elif getmode == 2:
            chat.kick_member(user.id)
            chat.unban_member(user.id)
            execstrings = "Kι¢кє∂"
            tag = "KICKED"
        elif getmode == 3:
            context.bot.restrict_chat_member(
                chat.id,
                user.id,
                permissions=ChatPermissions(can_send_messages=False),
            )
            execstrings = "Mυтє∂"
            tag = "MUTED"
        elif getmode == 4:
            bantime = extract_time(msg, getvalue)
            chat.kick_member(user.id, until_date=bantime)
            execstrings = "Bαииє∂ fσя {}".format(getvalue)
            tag = "TBAN"
        elif getmode == 5:
            mutetime = extract_time(msg, getvalue)
            context.bot.restrict_chat_member(
                chat.id,
                user.id,
                until_date=mutetime,
                permissions=ChatPermissions(can_send_messages=False),
            )
            execstrings = "Mυтє∂ fσя {}".format(getvalue)
            tag = "TMUTE"
        send_message(
            update.effective_message,
            "вєєρ вσσρ! вσσρ вєєρ!!\n{}!".format(execstrings),
        )

        return (
            "<b>{}:</b>"
            "\n#{}"
            "\n<b>User:</b> {}"
            "\nFlooded the group.".format(
                tag,
                html.escape(chat.title),
                mention_html(user.id, html.escape(user.first_name)),
            )
        )

    except BadRequest:
        msg.reply_text(
            "I ¢αи'т яєѕтяι¢т ρєσρℓє нєяє, gινє мє ρєямιѕѕισиѕ fιяѕт! υитιℓ тнєи, ι'ℓℓ ∂ιѕαвℓє αитι-fℓσσ∂.",
        )
        sql.set_flood(chat.id, 0)
        return (
            "<b>{}:</b>"
            "\n#INFO"
            "\nDon't have enough permission to restrict users so automatically disabled anti-flood".format(
                chat.title,
            )
        )


@user_admin_no_reply
@bot_admin
def flood_button(update: Update, context: CallbackContext):
    bot = context.bot
    query = update.callback_query
    user = update.effective_user
    match = re.match(r"unmute_flooder\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat = update.effective_chat.id
        try:
            bot.restrict_chat_member(
                chat,
                int(user_id),
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )
            update.effective_message.edit_text(
                f"Uимυтє∂ ву {mention_html(user.id, html.escape(user.first_name))}.",
                parse_mode="HTML",
            )
        except:
            pass


@user_admin
@loggable
def set_flood(update, context) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "Tнιѕ ¢σммαи∂ ιѕ мєαит тσ υѕє ιи gяσυρ иσт ιи ρм",
            )
            return ""
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if len(args) >= 1:
        val = args[0].lower()
        if val in ["off", "no", "0"]:
            sql.set_flood(chat_id, 0)
            if conn:
                text = message.reply_text(
                    "Aитι-fℓσσ∂ нαѕ вєєи ∂ιѕαвℓє∂ ιи {}.".format(chat_name),
                )
            else:
                text = message.reply_text("Aитι-fℓσσ∂ нαѕ вєєи ∂ιѕαвℓє∂.")

        elif val.isdigit():
            amount = int(val)
            if amount <= 0:
                sql.set_flood(chat_id, 0)
                if conn:
                    text = message.reply_text(
                        "Aитι-fℓσσ∂ нαѕ вєєи ∂ιѕαвℓє∂ ιи {}.".format(chat_name),
                    )
                else:
                    text = message.reply_text("Aитι-fℓσσ∂ нαѕ вєєи ∂ιѕαвℓє∂.")
                return (
                    "<b>{}:</b>"
                    "\n#SETFLOOD"
                    "\n<b>Admin:</b> {}"
                    "\nDisable antiflood.".format(
                        html.escape(chat_name),
                        mention_html(user.id, html.escape(user.first_name)),
                    )
                )

            if amount <= 3:
                send_message(
                    update.effective_message,
                    "Aитι-fℓσσ∂ мυѕт вє єιтнєя 0 (∂ιѕαвℓє∂) σя иυмвєя gяєαтєя тнαи 3!",
                )
                return ""
            sql.set_flood(chat_id, amount)
            if conn:
                text = message.reply_text(
                    "Aитι-fℓσσ∂ нαѕ вєєи ѕєт тσ {} ιи ¢нαт: {}".format(
                        amount,
                        chat_name,
                    ),
                )
            else:
                text = message.reply_text(
                    "Sυ¢¢єѕѕfυℓℓу υρ∂αтє∂ αитι-fℓσσ∂ ℓιмιт тσ {}!".format(amount),
                )
            return (
                "<b>{}:</b>"
                "\n#SETFLOOD"
                "\n<b>Admin:</b> {}"
                "\nSet antiflood to <code>{}</code>.".format(
                    html.escape(chat_name),
                    mention_html(user.id, html.escape(user.first_name)),
                    amount,
                )
            )

        else:
            message.reply_text("Iиναℓι∂ αяgυмєит ρℓєαѕє υѕє α иυмвєя, 'σff' σя 'σи'")
    else:
        message.reply_text(
            (
                "Use `/setflood number` тσ єиαвℓє-flooantid.\nOr use `/setflood off` тσ ∂ιѕαвℓєantiflood!."
            ),
            parse_mode="markdown",
        )
    return ""


def flood(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "Tнιѕ ¢σммαи∂ ιѕ мєαит тσ υѕє ιи gяσυρ иσт ιи ρм",
            )
            return
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        if conn:
            text = msg.reply_text(
                "I'м иσт єиfσя¢ιиg αиу fℓσσ∂ ¢σитяσℓ ιи {}!".format(chat_name),
            )
        else:
            text = msg.reply_text("I'm not enforcing any flood control here!")
    else:
        if conn:
            text = msg.reply_text(
                "I'м ¢υяяєитℓу яєѕтяι¢тιиg мємвєяѕ αfтєя {} ¢σиѕє¢υтινє мєѕѕαgєѕ ιи {}.".format(
                    limit,
                    chat_name,
                ),
            )
        else:
            text = msg.reply_text(
                "I'м ¢υяяєитℓу яєѕтяι¢тιиg мємвєяѕ αfтєя {} ¢σиѕє¢υтινє мєѕѕαgєѕ.".format(
                    limit,
                ),
            )


@user_admin
def set_flood_mode(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "Tнιѕ ¢σммαи∂ ιѕ мєαит тσ υѕє ιи gяσυρ иσт ιи ρм",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() == "ban":
            settypeflood = "ban"
            sql.set_flood_strength(chat_id, 1, "0")
        elif args[0].lower() == "kick":
            settypeflood = "kick"
            sql.set_flood_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeflood = "mute"
            sql.set_flood_strength(chat_id, 3, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """It looks like you tried to set time value for antiflood but you didn't specified time; Try, `/setfloodmode tban <timevalue>`.
    Examples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeflood = "tban for {}".format(args[1])
            sql.set_flood_strength(chat_id, 4, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = (
                    update.effective_message,
                    """It looks like you tried to set time value for antiflood but you didn't specified time; Try, `/setfloodmode tmute <timevalue>`.
    Examples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks.""",
                )
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeflood = "tmute for {}".format(args[1])
            sql.set_flood_strength(chat_id, 5, str(args[1]))
        else:
            send_message(
                update.effective_message,
                "I σиℓу υи∂єяѕтαи∂ вαи/кι¢к/мυтє/тнαи/тмυтє!",
            )
            return
        if conn:
            text = msg.reply_text(
                "Eχ¢єє∂ιиg ¢σиѕє¢υтινє fℓσσ∂ ℓιмιт ωιℓℓ яєѕυℓт ιи {} ιи {}!".format(
                    settypeflood,
                    chat_name,
                ),
            )
        else:
            text = msg.reply_text(
                "Eχ¢єє∂ιиg ¢σиѕє¢υтινє fℓσσ∂ ℓιмιт ωιℓℓ яєѕυℓт ιи {}!".format(
                    settypeflood,
                ),
            )
        return (
            "<b>{}:</b>\n"
            "<b>Admin:</b> {}\n"
            "Hαѕ ¢нαиgє∂ αитι-fℓσσ∂ мσ∂є. User will {}.".format(
                settypeflood,
                html.escape(chat.title),
                mention_html(user.id, html.escape(user.first_name)),
            )
        )
    getmode, getvalue = sql.get_flood_setting(chat.id)
    if getmode == 1:
        settypeflood = "ban"
    elif getmode == 2:
        settypeflood = "kick"
    elif getmode == 3:
        settypeflood = "mute"
    elif getmode == 4:
        settypeflood = "tban for {}".format(getvalue)
    elif getmode == 5:
        settypeflood = "tmute for {}".format(getvalue)
    if conn:
        text = msg.reply_text(
            "Sєи∂ιиg мσяє мєѕѕαgєѕ тнαи fℓσσ∂ ℓιмιт ωιℓℓ яєѕυℓт ιи {} ιи {}.".format(
                settypeflood,
                chat_name,
            ),
        )
    else:
        text = msg.reply_text(
            "Sєи∂ιиg мσяє мєѕѕαgєѕ тнαи fℓσσ∂ ℓιмιт ωιℓℓ яєѕυℓт ιи {}.".format(
                settypeflood,
            ),
        )
    return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        return "Not enforcing to flood control."
    return "Aитι-fℓσσ∂ нαѕ вєєи ѕєт тσ`{}`.".format(limit)

def helps(chat):
    return gs(chat, "antiflood_help")

__mod_name__ = "Anti-Flood"

FLOOD_BAN_HANDLER = MessageHandler(
    Filters.all & ~Filters.status_update & Filters.chat_type.groups,
    check_flood,
    run_async=True,
)
SET_FLOOD_HANDLER = CommandHandler(
    "setflood", set_flood, filters=Filters.chat_type.groups, run_async=True
)
SET_FLOOD_MODE_HANDLER = CommandHandler(
    "setfloodmode",
    set_flood_mode,
    pass_args=True,
    run_async=True,
)  # , filters=Filters.chat_type.group)
FLOOD_QUERY_HANDLER = CallbackQueryHandler(
    flood_button, pattern=r"unmute_flooder", run_async=True
)
FLOOD_HANDLER = CommandHandler(
    "flood", flood, filters=Filters.chat_type.groups, run_async=True
)

dispatcher.add_handler(FLOOD_BAN_HANDLER, FLOOD_GROUP)
dispatcher.add_handler(FLOOD_QUERY_HANDLER)
dispatcher.add_handler(SET_FLOOD_HANDLER)
dispatcher.add_handler(SET_FLOOD_MODE_HANDLER)
dispatcher.add_handler(FLOOD_HANDLER)

__handlers__ = [
    (FLOOD_BAN_HANDLER, FLOOD_GROUP),
    SET_FLOOD_HANDLER,
    FLOOD_HANDLER,
    SET_FLOOD_MODE_HANDLER,
]
