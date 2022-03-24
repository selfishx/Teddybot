import html
import random

from time import sleep
from telegram import (
    ParseMode,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.error import BadRequest
from telegram.ext import CallbackContext, Filters, CommandHandler, run_async, CallbackQueryHandler
from telegram.utils.helpers import mention_html
from typing import Optional, List
from telegram import TelegramError

import SiestaRobot.modules.sql.users_sql as sql
from SiestaRobot.modules.disable import DisableAbleCommandHandler
from SiestaRobot.modules.helper_funcs.filters import CustomFilters
from SiestaRobot import (
    DEV_USERS,
    LOGGER,
    OWNER_ID,
    DRAGONS,
    DEMONS,
    TIGERS,
    WOLVES,
    dispatcher,
)
from SiestaRobot.modules.helper_funcs.chat_status import (
    user_admin_no_reply,
    bot_admin,
    can_restrict,
    connection_status,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
    user_admin,
    user_can_ban,
    can_delete,
    dev_plus,
)
from SiestaRobot.modules.helper_funcs.extraction import extract_user_and_text
from SiestaRobot.modules.helper_funcs.string_handling import extract_time
from SiestaRobot.modules.log_channel import gloggable, loggable
from SiestaRobot.modules.language import gs



@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot = context.bot
    args = context.args
    reason = ""
    if message.reply_to_message and message.reply_to_message.sender_chat:
        r = bot.ban_chat_sender_chat(chat_id=chat.id, sender_chat_id=message.reply_to_message.sender_chat.id)
        if r:
            message.reply_text("Cнαииєℓ {} ωαѕ вαииє∂ ѕυ¢¢єѕѕfυℓℓу fяσм {}".format(
                html.escape(message.reply_to_message.sender_chat.title),
                html.escape(chat.title)
            ),
                parse_mode="html"
            )
        else:
            message.reply_text("Fαιℓє∂ тσ вαи ¢нαииєℓ")
        return

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("⚠️ Uѕєя иσт fσυи∂.")
        return log_message
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "Uѕєя иσт fσυи∂":
            raise
        message.reply_text("Cαи'т ѕєєм тσ fιи∂ тнιѕ ρєяѕσи.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Oσн уєαн, вαи муѕєℓf, иσσв!")
        return log_message

    if is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
        if user_id == OWNER_ID:
            message.reply_text("Tяуιиg тσ ρυт мє αgαιиѕт α кιиg нυн?")
        elif user_id in DEV_USERS:
            message.reply_text("I ¢αи'т α¢т αgαιиѕт συя ρяιи¢є.")
        elif user_id in DRAGONS:
            message.reply_text(
                "Fιgнтιиg тнιѕ ємρєяσя нєяє ωιℓℓ ρυт υѕєя ℓινєѕ αт яιѕк."
            )
        elif user_id in DEMONS:
            message.reply_text(
                "Bяιиg αи σя∂єя fяσм ¢αρтαιи тσ fιgнт α αѕѕαѕѕιи ѕєяναит."
            )
        elif user_id in TIGERS:
            message.reply_text(
                "Bяιиg αи σя∂єя fяσм ѕσℓ∂ιєя тσ fιgнт α ℓαи¢єя ѕєяναит."
            )
        elif user_id in WOLVES:
            message.reply_text("Tяα∂єя α¢¢єѕѕ мαкє тнєм вαи ιммυиє!!")
        else:
            message.reply_text("⚠️ Cαииσт вαииє∂ α∂мιи.")
        return log_message
    if message.text.startswith("/s"):
        silent = True
        if not can_delete(chat, context.bot.id):
            return ""
    else:
        silent = False
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#{'S' if silent else ''}BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.ban_member(user_id)

        if silent:
            if message.reply_to_message:
                message.reply_to_message.delete()
            message.delete()
            return log

        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        reply = (
            f"{mention_html(member.user.id, html.escape(member.user.first_name))} [<code>{member.user.id}</code>] Banned."
        )
        if reason:
            reply += f"\nReason: {html.escape(reason)}"

        bot.sendMessage(
            chat.id,
            reply,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔄  Uивαи", callback_data=f"unbanb_unban={user_id}"
                        ),
                        InlineKeyboardButton(text="🗑️  Dєℓєтє", callback_data="unbanb_del"),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Rєρℓу мєѕѕαgє иσт fσυи∂":
            # Do not reply
            if silent:
                return log
            message.reply_text("Bαииє∂!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR вαииιиg υѕєя %s ιи ¢нαт %s (%s) ∂υє тσ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Uυнм..тнαт ∂ι∂и'т ωσяк...")

    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def temp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("⚠️ Uѕєя иσт fσυи∂.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "Uѕєя иσт fσυи∂":
            raise
        message.reply_text("I ¢αи'т ѕєєм тσ fιи∂ тнαт υѕєя.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Iм и0т gσииα вαи муѕєℓf, αяє уσυ ¢яαzу?")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I ∂σи'т fєєℓ ℓιкє тнαт.")
        return log_message

    if not reason:
        message.reply_text("Yσυ нανєи'т ѕρє¢ιfιє∂ α тιмє тσ вαи тнιѕ fσя!!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "#TEMP BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>Time:</b> {time_val}"
    )
    if reason:
        log += "\nReason: {}".format(reason)

    try:
        chat.ban_member(user_id, until_date=bantime)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker

        reply_msg = (
            f"{mention_html(member.user.id, html.escape(member.user.first_name))} [<code>{member.user.id}</code>] Temporary Banned"
            f" for (`{time_val}`)."
        )

        if reason:
            reply_msg += f"\nReason: `{html.escape(reason)}`"

        bot.sendMessage(
            chat.id,
            reply_msg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔄  Uивαи", callback_data=f"unbanb_unban={user_id}"
                        ),
                        InlineKeyboardButton(text="🗑️  Dєℓєтє", callback_data="unbanb_del"),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Rєρℓу мєѕѕαgє иσт fσυи∂":
            # Do not reply
            message.reply_text(
                f"{mention_html(member.user.id, html.escape(member.user.first_name))} [<code>{member.user.id}</code>] banned for {time_val}.", quote=False
            )
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR вαииιиg υѕєя %s ιи ¢нαт %s (%s) ∂υє тσ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Wєℓℓ ∂αми, ι ¢αи'т ρυи¢н тнαт υѕєя")

    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin_no_reply
@user_can_ban
@loggable
def unbanb_btn(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user
    if query.data != "unbanb_del":
        splitter = query.data.split("=")
        query_match = splitter[0]
        if query_match == "unbanb_unban":
            user_id = splitter[1]
            if not is_user_admin(chat, int(user.id)):
                bot.answer_callback_query(
                    query.id,
                    text="⚠️ Yσυ ∂σи'т нανє єиσυgн яιgнтѕ тσ υимυтє ρєσρℓє",
                    show_alert=True,
                )
                return ""
            log_message = ""
            try:
                member = chat.get_member(user_id)
            except BadRequest:
                pass
            chat.unban_member(user_id)
            query.message.edit_text(
                f"{member.user.first_name} [{member.user.id}] Unbanned."
            )
            bot.answer_callback_query(query.id, text="Unbanned!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#UNBANNED\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
            )

    else:
        if not is_user_admin(chat, int(user.id)):
            bot.answer_callback_query(
                query.id,
                text="⚠️ Yσυ ∂σи'т нανє єиσυgн яιgнтѕ тσ ∂єℓєтє тнιѕ мєѕѕαgє.",
                show_alert=True,
            )
            return ""
        query.message.delete()
        bot.answer_callback_query(query.id, text="Deleted!")
        return ""

    
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def punch(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("⚠️ Uѕєя иσт fσυи∂")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "Uѕєя иσт fσυи∂":
            raise

        message.reply_text("⚠️ I ¢αи'т ѕєєм тσ fιи∂ тнιѕ υѕєя.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Yуєαннн ι'м иσт gσииα ∂σ тнαт.")
        return log_message

    if is_user_ban_protected(chat, user_id):
        message.reply_text("I яєαℓℓу ωιѕн ι ¢συℓ∂ ρυи¢н тнιѕ υѕєя....")
        return log_message

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"{mention_html(member.user.id, html.escape(member.user.first_name))} [<code>{member.user.id}</code>] Kicked.",
            parse_mode=ParseMode.HTML
        )
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#KICKED\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<b>Reason:</b> {reason}"

        return log

    else:
        message.reply_text("⚠️ Wєℓℓ ∂αми, ι ¢αи'т ρυи¢н тнαт υѕєя.")

    return log_message



@bot_admin
@can_restrict
def punchme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("I ωιѕн ι ¢συℓ∂...вυт уσυ'яє αи α∂мιи.")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text(
            "Pυи¢нєѕ уσυ συт σf тнє gяσυρ!",
        )
    else:
        update.effective_message.reply_text("Huh? I can't :/")


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def unban(update: Update, context: CallbackContext) -> Optional[str]:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""
    bot, args = context.bot, context.args
    if message.reply_to_message and message.reply_to_message.sender_chat:
        r = bot.unban_chat_sender_chat(chat_id=chat.id, sender_chat_id=message.reply_to_message.sender_chat.id)
        if r:
            message.reply_text("Cнαииєℓ {} ωαѕ вαииє∂ ѕυ¢¢єѕѕfυℓℓу fяσм {}".format(
                html.escape(message.reply_to_message.sender_chat.title),
                html.escape(chat.title)
            ),
                parse_mode="html"
            )
        else:
            message.reply_text("Fαιℓє∂ тσ υивαи ¢нαииєℓ")
        return

    user_id, reason = extract_user_and_text(message, args)
    if not user_id:
        message.reply_text("⚠️ Uѕєя иσт fσυи∂.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "Uѕєя иσт fσυи∂":
            raise
        message.reply_text("I ¢αи'т ѕєєм тσ fιи∂ тнαт υѕєя.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Hσω ωσυℓ∂ ι υивαи муѕєℓf ιf ι ωαѕи'т нєяє...?")
        return log_message

    if is_user_in_chat(chat, user_id):
        message.reply_text(f"⚠️ Uѕєя иσт fσυи∂.")
        return log_message

    chat.unban_member(user_id)
    message.reply_text(
        f"{member.user.first_name} [{member.user.id}] Unbanned."
    )

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNBANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += f"\n<b>Reason:</b> {reason}"

    return log


@connection_status
@bot_admin
@can_restrict
@gloggable
def selfunban(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in DRAGONS or user.id not in TIGERS:
        return

    try:
        chat_id = int(args[0])
    except:
        message.reply_text("gινє α ναℓι∂ ¢нαт ι∂")
        return

    chat = bot.getChat(chat_id)

    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "Uѕєя иσт fσυи∂":
            message.reply_text("I ¢αи'т ѕєєм тσ fιи∂ тнιѕ υѕєя.")
            return
        else:
            raise

    if is_user_in_chat(chat, user.id):
        message.reply_text("Aяєи'т уσυ αℓяєα∂у ιи тнє ¢нαт??")
        return

    chat.unban_member(user.id)
    message.reply_text(f"Yєρ, ι нανє υивαииє∂ тнє υѕєя.")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNBANNED\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )

    return log


@bot_admin
@can_restrict
@loggable
def banme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    chat = update.effective_chat
    user = update.effective_user
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("⚠️ I ¢αииσт вαииє∂ α∂мιи..")
        return

    res = update.effective_chat.ban_member(user_id)
    if res:
        update.effective_message.reply_text("Yєѕ, уσυ'яє яιgнт! gтfσ..")
        return (
            "<b>{}:</b>"
            "\n#BANME"
            "\n<b>User:</b> {}"
            "\n<b>ID:</b> <code>{}</code>".format(
                html.escape(chat.title),
                mention_html(user.id, user.first_name),
                user_id,
            )
        )

    else:
        update.effective_message.reply_text("Huh? I can't :/")


@dev_plus
def snipe(update: Update, context: CallbackContext):
    args = context.args
    bot = context.bot
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError:
        update.effective_message.reply_text("Pℓєαѕє gινє мє α ¢нαт тσ є¢нσ тσ!")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            bot.sendMessage(int(chat_id), str(to_send))
        except TelegramError:
            LOGGER.warning("Cσυℓ∂и'т ѕєи∂ тσ gяσυρ %s", str(chat_id))
            update.effective_message.reply_text(
                "Cσυℓ∂и'т ѕєи∂ тнє мєѕѕαgє. ρєянαρѕ ι'м иσт ραят σf тнαт gяσυρ?"
            )


def helps(chat):
    return gs(chat, "bansmutes_help")


__mod_name__ = "Bans/Mutes"

BAN_HANDLER = CommandHandler(["ban", "sban"], ban, run_async=True)
TEMPBAN_HANDLER = CommandHandler(["tban"], temp_ban, run_async=True)
KICK_HANDLER = CommandHandler(["kick", "punch"], punch, run_async=True)
UNBAN_HANDLER = CommandHandler("unban", unban, run_async=True)
ROAR_HANDLER = CommandHandler("roar", selfunban, run_async=True)
UNBAN_BUTTON_HANDLER = CallbackQueryHandler(unbanb_btn, pattern=r"unbanb_")
KICKME_HANDLER = DisableAbleCommandHandler(["kickme", "punchme"], punchme, filters=Filters.chat_type.groups, run_async=True)
SNIPE_HANDLER = CommandHandler("snipe", snipe, pass_args=True, filters=CustomFilters.sudo_filter, run_async=True)
BANME_HANDLER = CommandHandler("banme", banme, run_async=True)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(ROAR_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)
dispatcher.add_handler(UNBAN_BUTTON_HANDLER)
dispatcher.add_handler(SNIPE_HANDLER)
dispatcher.add_handler(BANME_HANDLER)

__handlers__ = [
    BAN_HANDLER,
    TEMPBAN_HANDLER,
    KICK_HANDLER,
    UNBAN_HANDLER,
    ROAR_HANDLER,
    KICKME_HANDLER,
    UNBAN_BUTTON_HANDLER,
    SNIPE_HANDLER,
    BANME_HANDLER,
]
