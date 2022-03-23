import html

from telegram import ParseMode, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from SiestaRobot import DRAGONS, dispatcher
from SiestaRobot.modules.disable import DisableAbleCommandHandler
from SiestaRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_pin,
    can_promote,
    connection_status,
    user_admin,
    ADMIN_CACHE,
)

from SiestaRobot.modules.helper_funcs.admin_rights import user_can_changeinfo, user_can_promote
from SiestaRobot.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from SiestaRobot.modules.log_channel import loggable
from SiestaRobot.modules.helper_funcs.alternate import send_message
from SiestaRobot.modules.language import gs


@bot_admin
@user_admin
def set_sticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text("yσυ'яє мιѕѕιиg яιgнтѕ тσ ¢нαиgє ¢нαт ιиfσ!")

    if msg.reply_to_message:
        if not msg.reply_to_message.sticker:
            return msg.reply_text(
                "Yσυ иєє∂ тσ яєρℓу тσ ѕσмє ѕтι¢кєя тσ ѕєт ¢нαт ѕтι¢кєя ѕєт!"
            )
        stkr = msg.reply_to_message.sticker.set_name
        try:
            context.bot.set_chat_sticker_set(chat.id, stkr)
            msg.reply_text(f"Sυ¢¢єѕѕfυℓℓу ѕєт иєω gяσυρ ѕтι¢кєяѕ ιи {chat.title}!")
        except BadRequest as excp:
            if excp.message == "Participants_too_few":
                return msg.reply_text(
                    "Sorry, due to telegram restrictions chat needs to have minimum 100 members before they can have group stickers!"
                )
            msg.reply_text(f"Error! {excp.message}.")
    else:
        msg.reply_text("Yσυ иєє∂ тσ яєρℓу тσ ѕσмє ѕтι¢кєя тσ ѕєт ¢нαт ѕтι¢кєя ѕєт!")
       
    
@bot_admin
@user_admin
def setchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("Yσυ'яє мιѕѕιиg яιgнтѕ тσ ¢нαиgє gяσυρ ιиfσ!")
        return

    if msg.reply_to_message:
        if msg.reply_to_message.photo:
            pic_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            pic_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("Yσυ ¢αи σиℓу ѕєт ѕσмє ρнσтσ αѕ ¢нαт ρι¢!")
            return
        dlmsg = msg.reply_text("ʝυѕт α ѕє¢...")
        tpic = context.bot.get_file(pic_id)
        tpic.download("gpic.png")
        try:
            with open("gpic.png", "rb") as chatp:
                context.bot.set_chat_photo(int(chat.id), photo=chatp)
                msg.reply_text("Sυ¢¢єѕѕfυℓℓу ѕєт иєω ¢нαтρι¢!")
        except BadRequest as excp:
            msg.reply_text(f"Error! {excp.message}")
        finally:
            dlmsg.delete()
            if os.path.isfile("gpic.png"):
                os.remove("gpic.png")
    else:
        msg.reply_text("Rєρℓу тσ ѕσмє ρнσтσ σя fιℓє тσ ѕєω иєω ¢нαт ρι¢!")
        
@bot_admin
@user_admin
def rmchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("Yσυ ∂σит нανє єиσυgн яιgнтѕ тσ ∂єℓєтє gяσυρ ρнσтσ")
        return
    try:
        context.bot.delete_chat_photo(int(chat.id))
        msg.reply_text("Sυ¢¢єѕѕfυℓℓу ∂єℓєтє∂ ¢нαт'ѕ ρяσfιℓє ρнσтσ!")
    except BadRequest as excp:
        msg.reply_text(f"Error! {excp.message}.")
        return
    
@bot_admin
@user_admin
def set_desc(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text("Yσυ'яє мιѕѕιиg яιgнтѕ тσ ¢нαиgє ¢нαт ιиfσ!")

    tesc = msg.text.split(None, 1)
    if len(tesc) >= 2:
        desc = tesc[1]
    else:
        return msg.reply_text("Sєттιиg ємρту ∂єѕ¢яιρтισи ωσи'т ∂σ αиутнιиg!")
    try:
        if len(desc) > 255:
            return msg.reply_text("Dєѕ¢яιρтισи мυѕт иєє∂ѕ тσ вє υи∂єя 255 ¢нαяα¢тєя'ѕ!")
        context.bot.set_chat_description(chat.id, desc)
        msg.reply_text(f"Sυ¢¢єѕѕfυℓℓу υρ∂αтє∂ ¢нαт ∂єѕ¢яιρтισи ιи {chat.title}!")
    except BadRequest as excp:
        msg.reply_text(f"Error! {excp.message}.")        
        
@bot_admin
@user_admin
def setchat_title(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    args = context.args

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("Yσυ'яє мιѕѕιиg яιgнтѕ тσ ¢нαиgє ¢нαт ιиfσ!")
        return

    title = " ".join(args)
    if not title:
        msg.reply_text("Eитєя ѕσмє тєχт тσ ѕєт иєω тιтℓє ιи уσυя ¢нαт!")
        return

    try:
        context.bot.set_chat_title(int(chat.id), str(title))
        msg.reply_text(
            f"Sυ¢¢єѕѕfυℓℓу ѕєт <b>{title}</b> as new chat title!",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        msg.reply_text(f"Error! {excp.message}.")
        return
        
        
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def promote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text("Yσυ ∂σит нανє иє¢єѕѕαяу яιgнтѕ тσ ∂σ тнαт!")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "Yσυ ∂σи'т ѕєєм тσ вє яєfєяяιиg тσ α υѕєя σя тнє ι∂ ѕρє¢ιfιє∂ ιѕ ιи¢σяяє¢т...",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ('administrator', 'creator'):
        message.reply_text("Hσω αм ι мєαит тσ ρяσмσтє ѕσмєσиє тнαт'ѕ αℓяєα∂у αи α∂мιи?")
        return

    if user_id == bot.id:
        message.reply_text("I ¢αи'т ρяσмσтє муѕєℓf! gєт αи α∂мιи тσ ∂σ ιт fσя мє.")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            # can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("I ¢αи'т ρяσмσтє ѕσмєσиє ωнσ ιѕи'т ιи тнє gяσυρ.")
        else:
            message.reply_text("Aи єяяσя σ¢¢υяяє∂ ωнιℓє ρяσмσтιиg.")
        return

    bot.sendMessage(
        chat.id,
        f"Promoting a user in <b>{chat.title}</b>\n\nUser: {mention_html(user_member.user.id, user_member.user.first_name)}\nAdmin: {mention_html(user.id, user.first_name)}",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#PROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def fullpromote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text("Yσυ ∂σит нανє иє¢єѕѕαяу яιgнтѕ тσ ∂σ тнαт!")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "Yσυ ∂σи'т ѕєєм тσ вє яєfєяяιиg тσ α υѕєя σя тнє ι∂ ѕρє¢ιfιє∂ ιѕ ιи¢σяяє¢т...",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ('administrator', 'creator'):
        message.reply_text("Hσω αм ι мєαит тσ ρяσмσтє ѕσмєσиє тнαт'ѕ αℓяєα∂у αи α∂мιи?")
        return

    if user_id == bot.id:
        message.reply_text("I ¢αи'т ρяσмσтє муѕєℓf! gєт αи α∂мιи тσ ∂σ ιт fσя мє..")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_voice_chats=bot_member.can_manage_voice_chats,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("I ¢αи'т ρяσмσтє ѕσмєσиє ωнσ ιѕи'т ιи тнє gяσυρ.")
        else:
            message.reply_text("Aи єяяσя σ¢¢υяяє∂ ωнιℓє ρяσмσтιиg.")
        return

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "Demote", callback_data="demote_({})".format(user_member.user.id))
    ]])

    bot.sendMessage(
        chat.id,
        f"Fullpromoting a user in <b>{chat.title}</b>\n\n<b>User: {mention_html(user_member.user.id, user_member.user.first_name)}</b>\n<b>Promoter: {mention_html(user.id, user.first_name)}</b>",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#FULLPROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def demote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "Yσυ ∂σи'т ѕєєм тσ вє яєfєяяιиg тσ α υѕєя σя тнє ι∂ ѕρє¢ιfιє∂ ιѕ ιи¢σяяє¢т...",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "creator":
        message.reply_text("Tнιѕ ρєяѕσи ¢яєαтє∂ тнє ¢нαт, нσω ωσυℓ∂ ι ∂ємσтє тнєм?")
        return

    if not user_member.status == "administrator":
        message.reply_text("Cαи'т ∂ємσтє ωнαт ωαѕи'т ρяσмσтє∂!")
        return

    if user_id == bot.id:
        message.reply_text("I ¢αи'т ρяσмσтє муѕєℓf! gєт αи α∂мιи тσ ∂σ ιт fσя мє..")
        return

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_voice_chats=False,
        )

        bot.sendMessage(
            chat.id,
            f"Sucessfully demoted a admins in <b>{chat.title}</b>\n\nAdmin: <b>{mention_html(user_member.user.id, user_member.user.first_name)}</b>\nDemoter: {mention_html(user.id, user.first_name)}",
            parse_mode=ParseMode.HTML,
        )

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#DEMOTED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        message.reply_text(
            "Cσυℓ∂ иσт ∂ємσтє. ι мιgнт иσт вє α∂мιи, σя тнє α∂мιи ѕтαтυѕ ωαѕ αρρσιитє∂ ву αиιтнєя"
            " user, so I can't act upon them!",
        )
        return


@user_admin
def refresh_admin(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text("✅ A∂мιи ¢α¢нє яєfяєѕнє∂!")


@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text(
            "Yσυ ∂σи'т ѕєєм тσ вє яєfєяяιиg тσ α υѕєя σя тнє ι∂ ѕρє¢ιfιє∂ ιѕ ιи¢σяяє¢т...",
        )
        return

    if user_member.status == "creator":
        message.reply_text(
            "Tнιѕ ρєяѕσи ¢яєαтє∂ тнє ¢нαт, нσω ¢αи ι ѕєт ¢υѕтσм тιтℓє fσя нιм?",
        )
        return

    if user_member.status != "administrator":
        message.reply_text(
            "Can't set title for non-admins!\nPromote them first to set custom title!",
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "I can't set my own title myself! Get the one who made me admin to do it for me.",
        )
        return

    if not title:
        message.reply_text("Setting blank title doesn't do anything!")
        return

    if len(title) > 16:
        message.reply_text(
            "The title length is longer than 16 characters.\nTruncating it to 16 characters.",
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text(
            "Either they aren't promoted by me or you set a title text that is impossible to set."
        )
        return

    bot.sendMessage(
        chat.id,
        f"ѕυ¢¢єѕѕfυℓℓу ѕєт тιтℓє fσя <code>{user_member.user.first_name or user_id}</code> "
        f"to <code>{html.escape(title[:16])}</code>!",
        parse_mode=ParseMode.HTML,
    )


@bot_admin
@can_pin
@user_admin
@loggable
def pin(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    user = update.effective_user
    chat = update.effective_chat
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message is None:
        msg.reply_text("Rєρℓу тσ α мєѕѕαgє тσ ριи ιт!")
        return

    is_silent = True
    if len(args) >= 1:
        is_silent = (
            args[0].lower() != "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
            msg.reply_text(
                f"I have pinned a message.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "👉 Gσ тσ мєѕѕαgє", url=f"{message_link}")
                        ]
                    ]
                ), 
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"MESSAGE-PINNED-SUCCESSFULLY\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message


@bot_admin
@can_pin
@user_admin
@loggable
def unpin(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id
    unpinner = chat.get_member(user.id)

    if (
        not (unpinner.can_pin_messages or unpinner.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text("Yσυ ∂σит нανє иє¢єѕѕαяу яιgнтѕ тσ ∂σ тнαт!")
        return

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message and is_group:
        try:
            context.bot.unpinChatMessage(
                chat.id, prev_message.message_id
            )
            msg.reply_text(
                f"Unpinned <a href='{message_link}'>this message</a>.",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

    if not prev_message and is_group:
        try:
            context.bot.unpinChatMessage(chat.id)
            msg.reply_text(
                "Unpinned the last pinned message."
            )
        except BadRequest as excp:
            if excp.message == "Message to unpin not found":
               msg.reply_text(
                   "I ¢αи'т ѕєє ριииє∂ мєѕѕαgє, мαувє αℓяєα∂у υиℓιиє∂, σя ριи мєѕѕαgє тσ σℓ∂ 🙂"
               )
            else:
                raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"MESSAGE-UNPINNED-SUCCESSFULLY\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log_message


@bot_admin
def pinned(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    msg = update.effective_message
    msg_id = (
        update.effective_message.reply_to_message.message_id
        if update.effective_message.reply_to_message
        else update.effective_message.message_id
    )

    chat = bot.getChat(chat_id=msg.chat.id)
    if chat.pinned_message:
        pinned_id = chat.pinned_message.message_id
        if msg.chat.username:
            link_chat_id = msg.chat.username
            message_link = f"https://t.me/{link_chat_id}/{pinned_id}"
        elif (str(msg.chat.id)).startswith("-100"):
            link_chat_id = (str(msg.chat.id)).replace("-100", "")
            message_link = f"https://t.me/c/{link_chat_id}/{pinned_id}"

        msg.reply_text(
            f'🔽 Pinned on {html.escape(chat.title)}.',
            reply_to_message_id=msg_id,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="👉 gσ тσ мєѕѕαgє", url=f"https://t.me/{link_chat_id}/{pinned_id}")]]
            ),
        )

    else:
        msg.reply_text(
            f"There is no pinned message in <b>{html.escape(chat.title)}!</b>",
            parse_mode=ParseMode.HTML,
        )


@bot_admin
@user_admin
@connection_status
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type in [chat.SUPERGROUP, chat.CHANNEL]:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(
                "I ∂σи'т нανє α¢¢єѕѕ тσ тнє ιиνιтє ℓιик, тяу ¢нαиgιиg му ρєямιѕѕισиѕ!",
            )
    else:
        update.effective_message.reply_text(
            "I ¢αи σиℓу gινє уσυ ιиνιтє ℓιикѕ fσя ѕυρєяgяσυρ σя ¢нαииєℓѕ, ѕσяяу!!",
        )


@connection_status
def adminlist(update, context):
    chat = update.effective_chat  # type: Optional[Chat] -> unused variable
    user = update.effective_user  # type: Optional[User]
    args = context.args  # -> unused variable
    bot = context.bot

    if update.effective_message.chat.type == "private":
        send_message(update.effective_message, "Tнιѕ ¢σммαи∂ σиℓу ωσякѕ ιи gяσυρѕ.")
        return

    chat = update.effective_chat
    chat_id = update.effective_chat.id
    chat_name = update.effective_message.chat.title  # -> unused variable

    try:
        msg = update.effective_message.reply_text(
            "Fєт¢нιиg gяσυρ α∂мιиѕ...",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest:
        msg = update.effective_message.reply_text(
            "Fєт¢нιиg gяσυρ α∂мιиѕ...",
            quote=False,
            parse_mode=ParseMode.HTML,
        )

    administrators = bot.getChatAdministrators(chat_id)
    text = "A∂мιиѕ ιи <b>{}</b>:".format(html.escape(update.effective_chat.title))

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ ∂єℓєтє∂ α¢¢συит"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " + (user.last_name or "")),
                ),
            )

        if user.is_bot:
            administrators.remove(admin)
            continue

        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "creator":
            text += "\n 🌏 Creator:"
            text += "\n<code> • </code>{}\n".format(name)

            if custom_title:
                text += f"<code> ┗━ {html.escape(custom_title)}</code>\n"

    text += "\n🌟 A∂мιиѕ:"

    custom_admin_list = {}
    normal_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ ∂єℓєтє∂ α¢¢συит"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " + (user.last_name or "")),
                ),
            )
        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "administrator":
            if custom_title:
                try:
                    custom_admin_list[custom_title].append(name)
                except KeyError:
                    custom_admin_list.update({custom_title: [name]})
            else:
                normal_admin_list.append(name)

    for admin in normal_admin_list:
        text += "\n<code> • </code>{}".format(admin)

    for admin_group in custom_admin_list.copy():
        if len(custom_admin_list[admin_group]) == 1:
            text += "\n<code> • </code>{} | <code>{}</code>".format(
                custom_admin_list[admin_group][0],
                html.escape(admin_group),
            )
            custom_admin_list.pop(admin_group)

    text += "\n"
    for admin_group, value in custom_admin_list.items():
        text += "\n🚨 <code>{}</code>".format(admin_group)
        for admin in value:
            text += "\n<code> • </code>{}".format(admin)
        text += "\n"

    try:
        msg.edit_text(text, parse_mode=ParseMode.HTML)
    except BadRequest:  # if original message is deleted
        return


@bot_admin
@can_promote
@user_admin
@loggable
def button(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    bot: Optional[Bot] = context.bot
    match = re.match(r"demote_\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        member = chat.get_member(user_id)
        bot_member = chat.get_member(bot.id)
        bot_permissions = promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_voice_chats=bot_member.can_manage_voice_chats,
        )                
        demoted = bot.promoteChatMember(
                      chat.id,
                      user_id,
                      can_change_info=False,
                      can_post_messages=False,
                      can_edit_messages=False,
                      can_delete_messages=False,
                      can_invite_users=False,
                      can_restrict_members=False,
                      can_pin_messages=False,
                      can_promote_members=False,
                      can_manage_voice_chats=False,
        )
        if demoted:
        	update.effective_message.edit_text(
        	    f"Admin {mention_html(user.id, user.first_name)} Dємσтє∂ {mention_html(member.user.id, member.user.first_name)}!",
        	    parse_mode=ParseMode.HTML,
        	)
        	query.answer("Dємσтє∂!")
        	return (
                    f"<b>{html.escape(chat.title)}:</b>\n" 
                    f"#DEMOTE\n" 
                    f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                    f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
                )
    else:
        update.effective_message.edit_text(
            "Tнιѕ υѕєя ιѕ иσт ρяσмσтє∂ σя нαѕ ℓєfт тнє gяσυρ!"
        )
        return ""

  
def helps(chat):
    return gs(chat, "admin_help")

SET_DESC_HANDLER = CommandHandler("setdesc", set_desc, filters=Filters.chat_type.groups, run_async=True)
SET_STICKER_HANDLER = CommandHandler("setsticker", set_sticker, filters=Filters.chat_type.groups, run_async=True)
SETCHATPIC_HANDLER = CommandHandler("setgpic", setchatpic, filters=Filters.chat_type.groups, run_async=True)
RMCHATPIC_HANDLER = CommandHandler("delgpic", rmchatpic, filters=Filters.chat_type.groups, run_async=True)
SETCHAT_TITLE_HANDLER = CommandHandler("setgtitle", setchat_title, filters=Filters.chat_type.groups, run_async=True)

ADMINLIST_HANDLER = DisableAbleCommandHandler("admins", adminlist, run_async=True)

PIN_HANDLER = CommandHandler("pin", pin, filters=Filters.chat_type.groups, run_async=True)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=Filters.chat_type.groups, run_async=True)
PINNED_HANDLER = CommandHandler("pinned", pinned, filters=Filters.chat_type.groups, run_async=True)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite, run_async=True)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote, run_async=True)
FULLPROMOTE_HANDLER = DisableAbleCommandHandler("fullpromote", fullpromote, run_async=True)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote, run_async=True)

SET_TITLE_HANDLER = CommandHandler("title", set_title, run_async=True)
ADMIN_REFRESH_HANDLER = CommandHandler("admincache", refresh_admin, filters=Filters.chat_type.groups, run_async=True)

dispatcher.add_handler(SET_DESC_HANDLER)
dispatcher.add_handler(SET_STICKER_HANDLER)
dispatcher.add_handler(SETCHATPIC_HANDLER)
dispatcher.add_handler(RMCHATPIC_HANDLER)
dispatcher.add_handler(SETCHAT_TITLE_HANDLER)
dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(PINNED_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(FULLPROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(ADMIN_REFRESH_HANDLER)

__mod_name__ = "Admins"
__command_list__ = [
    "setdesc"
    "setsticker"
    "setgpic"
    "delgpic"
    "setgtitle"
    "adminlist",
    "admins", 
    "invitelink", 
    "promote", 
    "fullpromote",
    "lowpromote",
    "demote", 
    "admincache"
]
__handlers__ = [
    SET_DESC_HANDLER,
    SET_STICKER_HANDLER,
    SETCHATPIC_HANDLER,
    RMCHATPIC_HANDLER,
    SETCHAT_TITLE_HANDLER,
    ADMINLIST_HANDLER,
    PIN_HANDLER,
    UNPIN_HANDLER,
    PINNED_HANDLER,
    INVITE_HANDLER,
    PROMOTE_HANDLER,
    FULLPROMOTE_HANDLER,
    DEMOTE_HANDLER,
    SET_TITLE_HANDLER,
    ADMIN_REFRESH_HANDLER,
]
