import html
from SiestaRobot.modules.disable import DisableAbleCommandHandler
from SiestaRobot import dispatcher, DRAGONS
from SiestaRobot.modules.helper_funcs.extraction import extract_user
from telegram.ext import CallbackContext, CallbackQueryHandler
import SiestaRobot.modules.sql.approve_sql as sql
from SiestaRobot.modules.helper_funcs.chat_status import user_admin
from SiestaRobot.modules.log_channel import loggable
from SiestaRobot.modules.language import gs
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.utils.helpers import mention_html
from telegram.error import BadRequest


@loggable
@user_admin
def approve(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "I ∂σи'т киσω ωнσ уσυ'яє тαℓкιиg αвσυт, уσυ'яє gσιиg тσ иєє∂ тσ ѕρє¢ιfу α υѕєя!",
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status in ("administrator", "creator"):
        message.reply_text(
            "Uѕєя ιѕ αℓяєα∂у α∂мιи - ℓι¢кѕ, вℓσ¢кℓιѕт, αи∂ αитι-fℓσσ∂ αℓяєα∂у ∂σи'т αρρℓу тσ тнєм.",
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"[{member.user['first_name']}](tg://user?id={member.user['id']}) ιѕ αℓяєα∂у αρρяσνє∂ ιи {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.approve(message.chat_id, user_id)
    message.reply_text(
        f"[{member.user['first_name']}](tg://user?id={member.user['id']}) нαѕ вєєи αρρяσνє∂ ιи {chat_title}! Tнєу ωιℓℓ иσω вє ιgиσяє∂ ву αυтσмαтє∂ α∂мιи α¢тισиѕ ℓιкє ℓσ¢кѕ, вℓσ¢кℓιѕт, αи∂ αитι-fℓσσ∂.",
        parse_mode=ParseMode.MARKDOWN,
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#APPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@loggable
@user_admin
def disapprove(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "I ∂σи'т киσω ωнσ уσυ'яє тαℓкιиg αвσυт, уσυ'яє gσιиg тσ иєє∂ тσ ѕρє¢ιfу α υѕєя!",
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status in ("administrator", "creator"):
        message.reply_text("Tнιѕ υѕєя ιѕ αи α∂мιи, тнєу ¢αи'т вє υиαρρяσνє∂.")
        return ""
    if not sql.is_approved(message.chat_id, user_id):
        message.reply_text(f"{member.user['first_name']} isn't approved yet!")
        return ""
    sql.disapprove(message.chat_id, user_id)
    message.reply_text(
        f"{member.user['first_name']} ιѕ иσ ℓσиgєя αρρяσνє∂ ιи {chat_title}.",
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNAPPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@user_admin
def approved(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "Tнє fσℓℓσωιиg υѕєяѕ αяє αρρяσνє∂.\n"
    approved_users = sql.list_approved(message.chat_id)
    for i in approved_users:
        member = chat.get_member(int(i.user_id))
        msg += f"- `{i.user_id}`: {member.user['first_name']}\n"
    if msg.endswith("approved.\n"):
        message.reply_text(f"Nσ υѕєяѕ αяє αρρяσνє∂ ιи {chat_title}.")
        return ""
    message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


@user_admin
def approval(update, context):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    member = chat.get_member(int(user_id))
    if not user_id:
        message.reply_text(
            "I ∂σи'т киσω ωнσ уσυ'яє тαℓкιиg αвσυт, уσυ'яє gσιиg тσ иєє∂ тσ ѕρє¢ιfу α υѕєя!",
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"{member.user['first_name']} iѕ αи αρρяσνє∂ υѕєя. ℓσ¢кѕ, вℓσ¢кℓιѕт, αи∂ αитι-fℓσσ∂ ωσи'т αρρℓу тσ тнєм.",
        )
    else:
        message.reply_text(
            f"{member.user['first_name']} ιѕ иσт αи αρρяσνє∂ υѕєя, тнєу αяє αffє¢тє∂ ву иσямαℓ ¢σммαи∂ѕ.",
        )


def unapproveall(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in DRAGONS:
        update.effective_message.reply_text(
            "Oиℓу тнє ¢нαт σωиєя ¢αи υиαρρяσνє αℓℓ υѕєяѕ αт σи¢є.",
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Uиαρρяσνє αℓℓ υѕєяѕ",
                        callback_data="unapproveall_user",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Cαи¢єℓ",
                        callback_data="unapproveall_cancel",
                    ),
                ],
            ],
        )
        update.effective_message.reply_text(
            f"Aяє уσυ ѕυяє ωσυℓ∂ уσυ ℓιкє тσ υиαρρяνє αℓℓ υѕєяѕ ιи {chat.title}? Tнιѕ α¢тισи ¢αииσт вє υи∂σиє.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


def unapproveall_btn(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "unapproveall_user":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            approved_users = sql.list_approved(chat.id)
            users = [int(i.user_id) for i in approved_users]
            for user_id in users:
                sql.disapprove(chat.id, user_id)
            message.edit_text("Sυ¢¢єѕѕfυℓℓу υиαρρяσνє∂ αℓℓ υѕєя ιи тнιѕ ¢нαт.")
            return

        if member.status == "administrator":
            query.answer("Oиℓу σωиєя σf тнє ¢нαт ¢αи ∂σ тнιѕ.")

        if member.status == "member":
            query.answer("Yσυ иєє∂ тσ вє α∂мιи тσ ∂σ тнιѕ.")
    elif query.data == "unapproveall_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            message.edit_text("Rємσνιиg σf αℓℓ αρρяσνє∂ υѕєяѕ нαѕ вєєи ¢αи¢єℓℓє∂.")
            return ""
        if member.status == "administrator":
            query.answer("Oиℓу σωиєя σf тнє ¢нαт ¢αи ∂σ тнιѕ.")
        if member.status == "member":
            query.answer("Yσυ иєє∂ тσ вє α∂мιи тσ ∂σ тнιѕ.")


def helps(chat):
    return gs(chat, "approve_help")

APPROVE = DisableAbleCommandHandler("approve", approve, run_async=True)
DISAPPROVE = DisableAbleCommandHandler("unapprove", disapprove, run_async=True)
APPROVED = DisableAbleCommandHandler("approved", approved, run_async=True)
APPROVAL = DisableAbleCommandHandler("approval", approval, run_async=True)
UNAPPROVEALL = DisableAbleCommandHandler("unapproveall", unapproveall, run_async=True)
UNAPPROVEALL_BTN = CallbackQueryHandler(
    unapproveall_btn, pattern=r"unapproveall_.*", run_async=True
)

dispatcher.add_handler(APPROVE)
dispatcher.add_handler(DISAPPROVE)
dispatcher.add_handler(APPROVED)
dispatcher.add_handler(APPROVAL)
dispatcher.add_handler(UNAPPROVEALL)
dispatcher.add_handler(UNAPPROVEALL_BTN)

__mod_name__ = "Approvals"
__command_list__ = ["approve", "unapprove", "approved", "approval"]
__handlers__ = [APPROVE, DISAPPROVE, APPROVED, APPROVAL]
