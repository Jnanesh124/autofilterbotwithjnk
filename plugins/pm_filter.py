# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os, logging, string, asyncio, time, re, ast, random, math, pytz, pyrogram
from datetime import datetime, timedelta, date, time
from Script import script
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo, Message
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from utils import get_size, is_subscribed, pub_is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink, get_tutorial, send_all, get_cap
from database.users_chats_db import db
from database.ia_filterdb import col, sec_col, db as vjdb, sec_db, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import del_all, find_filter, get_filters
from database.connections_mdb import mydb, active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from database.gfilters_mdb import find_gfilter, get_gfilters, del_allg
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size

logger = logging.getLogger(__name__)
logger.setLevel(ERROR)
lock = asyncio.Lock()

BUTTON = {}
BUTTONS = {}
FRESH = {}
BUTTONS0 = {}
BUTTONS1 = {}
BUTTONS2 = {}
SPELL_CHECK = {}

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if message.chat.id != SUPPORT_CHAT_ID:
        settings = await get_settings(message.chat.id)
        chatid = message.chat.id
        user_id = message.from_user.id if message.from_user else 0
        if settings['fsub'] != None:
            try:
                btn = await pub_is_subscribed(client, message, settings['fsub'])
                if btn:
                    btn.append([InlineKeyboardButton("Unmute Me 🔕", callback_data=f"unmuteme#{int(user_id)}")])
                    await client.restrict_chat_member(chatid, message.from_user.id, ChatPermissions(can_send_messages=False))
                    await message.reply_photo(photo=random.choice(PICS), caption=f"👋 Hello {message.from_user.mention},\n\nPlease join the channel then click on unmute me button. 😇", reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)
                    return
            except Exception as e:
                print(e)

        manual = await manual_filters(client, message)
        if manual == False:
            settings = await get_settings(message.chat.id)
            try:
                if settings['auto_ffilter']:
                    ai_search = True
                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                    await auto_filter(client, message.text, message, reply_msg, ai_search)
            except KeyError:
                grpid = await active_connection(str(message.from_user.id))
                await save_group_settings(grpid, 'auto_ffilter', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_ffilter']:
                    ai_search = True
                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                    await auto_filter(client, message.text, message, reply_msg, ai_search)
    else: #a better logic to avoid repeated lines of code in auto_filter function
        search = message.text
        temp_files, temp_offset, total_results = await get_search_results(chat_id=message.chat.id, query=search.lower(), offset=0, filter=True)
        if total_results == 0:
            return
        else:
            return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. \n\nTʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...\n\nJᴏɪɴ ᴀɴᴅ Sᴇᴀʀᴄʜ Hᴇʀᴇ - {GRP_LNK}</b>")

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if content.startswith("/") or content.startswith("#") or content.startswith(".") or content.startswith(",") or content.startswith("@") or content.startswith("https") or content.startswith("www.") or content.startswith("-") or content.startswith("t.me"): return  # ignore commands and hashtags
    if PM_SEARCH == True:
        ai_search = True
        reply_msg = await bot.send_message(message.from_user.id, f"<b><i>Searching For {content} 🔍</i></b>", reply_to_message_id=message.id)
        await auto_filter(bot, content, message, reply_msg, ai_search)

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = FRESH.get(key)
   # if not search:
      #  await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
       # return

    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    temp.GETALL[key] = files
    temp.SHORT[query.from_user.id] = query.message.chat.id
    settings = await get_settings(query.message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
    else:
        btn = []
        btn.insert(0, [
            InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
            InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
            InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
            InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
            InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])
    try:
        if settings['max_btn']:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'max_btn', True)
        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append(
                [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
            )
        elif off_set is None:
            btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
        else:
            btn.append(
                [
                    InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                    InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                    InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                ],
            )
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
   # if not movies:
     #   return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[(int(movie_))]
    movie = re.sub(r"[:\-]", " ", movie)
    movie = re.sub(r"\s+", " ", movie).strip()
    await query.answer(script.TOP_ALRT_MSG)
    gl = await global_filters(bot, query.message, text=movie)
    if gl == False:
        k = await manual_filters(bot, query.message, text=movie)
        if k == False:
            files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
            if files:
                k = (movie, files, offset, total_results)
                ai_search = True
                reply_msg = await query.message.edit_text(f"<b><i>Searching For {movie} 🔍</i></b>")
                await auto_filter(bot, movie, query, reply_msg, ai_search, k)
            else:
                reqstr1 = query.from_user.id if query.from_user else 0
                reqstr = await bot.get_users(reqstr1)
                if NO_RESULTS_MSG:
                    await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)))
                k = await query.message.edit(script.MVE_NT_FND)
                await asyncio.sleep(10)
                await k.delete()

# Year
@Client.on_callback_query(filters.regex(r"^years#"))
async def years_cb_handler(client: Client, query: CallbackQuery):

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    btn = []
    for i in range(0, len(YEARS)-1, 4):
        row = []
        for j in range(4):
            if i+j < len(YEARS):
                row.append(
                    InlineKeyboardButton(
                        text=YEARS[i+j].title(),
                        callback_data=f"fy#{YEARS[i+j].lower()}#{key}"
                    )
                )
        btn.append(row)

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="sᴇʟᴇᴄᴛ ʏᴏᴜʀ ʏᴇᴀʀ", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fy#homepage#{key}")])

    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass

@Client.on_callback_query(filters.regex(r"^fy#"))
async def filter_yearss_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    baal = lang in search
    if baal:
        search = search.replace(lang, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(req) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    if lang != "homepage":
        search = f"{search} {lang}"
    BUTTONS[key] = search

    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
    else:
        btn = []
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
                InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
                InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
                InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
                InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
            ]
        )

    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )

            else:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
        )
    if lang != "homepage":
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fy#homepage#{key}")])

    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()

# Episode

@Client.on_callback_query(filters.regex(r"^episodes#"))
async def episodes_cb_handler(client: Client, query: CallbackQuery):

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    btn = []
    for i in range(0, len(EPISODES)-1, 4):
        row = []
        for j in range(4):
            if i+j < len(EPISODES):
                row.append(
                    InlineKeyboardButton(
                        text=EPISODES[i+j].title(),
                        callback_data=f"fe#{EPISODES[i+j].lower()}#{key}"
                    )
                )
        btn.append(row)

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴇᴘɪsᴏᴅᴇ", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fe#homepage#{key}")])

    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass

@Client.on_callback_query(filters.regex(r"^fe#"))
async def filter_episodes_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    baal = lang in search
    if baal:
        search = search.replace(lang, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(req) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    if lang != "homepage":
        search = f"{search} {lang}"
    BUTTONS[key] = search

    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
    else:
        btn = []
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
                InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
                InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
                InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
                InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
            ]
        )

    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )

            else:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
        )
    if lang != "homepage":
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fe#homepage#{key}")])

    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()



#languages

@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    btn = []
    for i in range(0, len(LANGUAGES)-1, 2):
        btn.append([
            InlineKeyboardButton(
                text=LANGUAGES[i].title(),
                callback_data=f"fl#{LANGUAGES[i].lower()}#{key}"
            ),
            InlineKeyboardButton(
                text=LANGUAGES[i+1].title(),
                callback_data=f"fl#{LANGUAGES[i+1].lower()}#{key}"
            ),
        ])

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="👇 sᴇ𝗅𝖾𝖼𝗍 𝖸𝗈𝗎𝗋 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾𝗌 👇", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fl#homepage#{key}")])

    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass

@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    baal = lang in search
    if baal:
        search = search.replace(lang, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(req) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    if lang != "homepage":
        search = f"{search} {lang}"
    BUTTONS[key] = search

    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
    else:
        btn = []
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
                InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
                InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
                InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
                InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])

    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )

            else:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
        )
    if lang != "homepage":
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fl#homepage#{key}")])

    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()



@Client.on_callback_query(filters.regex(r"^seasons#"))
async def seasons_cb_handler(client: Client, query: CallbackQuery):

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass

    _, key = query.data.split("#")
    search = FRESH.get(key)
    BUTTONS[key] = None
    try:
        search = search.replace(' ', '_')
    except:
        pass
    btn = []
    for i in range(0, len(SEASONS)-1, 2):
        btn.append([
            InlineKeyboardButton(
                text=SEASONS[i].title(),
                callback_data=f"fs#{SEASONS[i].lower()}#{key}"
            ),
            InlineKeyboardButton(
                text=SEASONS[i+1].title(),
                callback_data=f"fs#{SEASONS[i+1].lower()}#{key}"
            ),
        ])

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="👇 𝖲𝖾𝗅𝖾𝖼𝗍 Season 👇", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ​↭", callback_data=f"next_{req}_{key}_{offset}")])

    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass

@Client.on_callback_query(filters.regex(r"^fs#"))
async def filter_seasons_cb_handler(client: Client, query: CallbackQuery):
    _, seas, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    sea = ""
    season_search = ["s01","s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "s10", "season 01","season 02","season 03","season 04","season 05","season 06","season 07","season 08","season 09","season 10", "season 1","season 2","season 3","season 4","season 5","season 6","season 7","season 8","season 9"]
    for x in range (len(season_search)):
        if season_search[x] in search:
            sea = season_search[x]
            break
    if sea:
        search = search.replace(sea, "")
    else:
        search = search

    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(req) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass

    searchagn = search
    search1 = search
    search2 = search
    search = f"{search} {seas}"
    BUTTONS0[key] = search

    files, _, _ = await get_search_results(chat_id, search, max_results=10)
    files = [file for file in files if re.search(seas, file["file_name"], re.IGNORECASE)]

    seas1 = "s01" if seas == "season 1" else "s02" if seas == "season 2" else "s03" if seas == "season 3" else "s04" if seas == "season 4" else "s05" if seas == "season 5" else "s06" if seas == "season 6" else "s07" if seas == "season 7" else "s08" if seas == "season 8" else "s09" if seas == "season 9" else "s10" if seas == "season 10" else ""
    search1 = f"{search1} {seas1}"
    BUTTONS1[key] = search1
    files1, _, _ = await get_search_results(chat_id, search1, max_results=10)
    files1 = [file for file in files1 if re.search(seas1, file["file_name"], re.IGNORECASE)]

    if files1:
        files.extend(files1)

    seas2 = "season 01" if seas == "season 1" else "season 02" if seas == "season 2" else "season 03" if seas == "season 3" else "season 04" if seas == "season 4" else "season 05" if seas == "season 5" else "season 06" if seas == "season 6" else "season 07" if seas == "season 7" else "season 08" if seas == "season 8" else "season 09" if seas == "season 9" else "s010"
    search2 = f"{search2} {seas2}"
    BUTTONS2[key] = search2
    files2, _, _ = await get_search_results(chat_id, search2, max_results=10)
    files2 = [file for file in files2 if re.search(seas2, file["file_name"], re.IGNORECASE)]

    if files2:
        files.extend(files2)

    if not files:
        await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
                InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
                InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
                InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
                InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])
    else:
        btn = []
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
                InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
                InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
                InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
                InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])
    if lang != "homepage":
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"next_{req}_{key}_{offset}")])

    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        total_results = len(files)
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass

@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=False,
            )
    except:
        pass
    _, key = query.data.split("#")
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    btn = []
    for i in range(0, len(QUALITIES)-1, 2):
        btn.append([
            InlineKeyboardButton(
                text=QUALITIES[i].title(),
                callback_data=f"fl#{QUALITIES[i].lower()}#{key}"
            ),
            InlineKeyboardButton(
                text=QUALITIES[i+1].title(),
                callback_data=f"fl#{QUALITIES[i+1].lower()}#{key}"
            ),
        ])

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="⇊ ꜱᴇʟᴇᴄᴛ ʏᴏᴜʀ ǫᴜᴀʟɪᴛʏ ⇊", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fl#homepage#{key}")])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_qualities_cb_handler(client: Client, query: CallbackQuery):
    _, qual, key = query.data.split("#")
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    baal = qual in search
    if baal:
        search = search.replace(qual, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(req) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=False,
            )
    except:
        pass
    searchagain = search
    if lang != "homepage":
        search = f"{search} {qual}"
    BUTTONS[key] = search

    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    # files = [file for file in files if re.search(lang, file["file_name"], re.IGNORECASE)]
    if not files:
        await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
            InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
            InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
            InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
            InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])
    else:
        btn = []
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
            InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
            InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
            InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
            InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])

    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⇛",callback_data=f"next_{req}_{key}_{offset}")]
                )

            else:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⇛",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⇛",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="😶 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ 😶",callback_data="pages")]
        )
    if lang != "homepage":
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"next_{req}_{key}_{offset}")])

    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        total_results = len(files)
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass

@Client.on_callback_query(filters.regex(r"^pages"))
async def pages_cb_handler(client: Client, query: CallbackQuery):
    await query.answer()

@Client.on_callback_query(filters.regex(r"^manage_ignore"))
async def manage_ignore_words(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")

    # Check if the user is an admin
    user_id = query.from_user.id if query.from_user else None
    chat_id = query.message.chat.id

    try:
        member = await client.get_chat_member(chat_id, user_id)
        is_admin = member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] or user_id in ADMINS
    except Exception:
        is_admin = False

    if not is_admin:
        await query.answer("You don't have permission to access this feature.", show_alert=True)
        return

    ignore_words = await db.get_ignore_words(chat_id)

    if not ignore_words:
        message_text = "No ignore words found for this chat."
        buttons = [[InlineKeyboardButton("Add Ignore Word", callback_data=f"add_ignore_word_prompt#{key}")]]
    else:
        message_text = "Here are your ignore words:\n\n"
        for i, word in enumerate(ignore_words):
            message_text += f"{i+1}. `{word}`\n"
        buttons = [
            [InlineKeyboardButton("Add Ignore Word", callback_data=f"add_ignore_word_prompt#{key}")],
            [InlineKeyboardButton("Remove Ignore Word", callback_data=f"remove_ignore_word_prompt#{key}")]
        ]

    buttons.append([InlineKeyboardButton("Back", callback_data=f"back_to_settings#{key}")]) # Assuming a callback for back to settings

    await query.message.edit_text(
        text=message_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )
    await query.answer()

@Client.on_callback_query(filters.regex(r"^add_ignore_word_prompt"))
async def add_ignore_word_prompt(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")
    await query.message.edit_text(
        text="Enter the word you want to add to ignore list:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data=f"manage_ignore#{key}")]]),
        parse_mode=enums.ParseMode.MARKDOWN
    )
    temp.temp_data[query.message.chat.id] = {"action": "add_ignore_word", "key": key} # Store action and key for next message

@Client.on_callback_query(filters.regex(r"^remove_ignore_word_prompt"))
async def remove_ignore_word_prompt(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")
    ignore_words = await db.get_ignore_words(query.message.chat.id)

    if not ignore_words:
        await query.answer("No ignore words to remove.", show_alert=True)
        return

    message_text = "Enter the word you want to remove from ignore list:\n\n"
    for i, word in enumerate(ignore_words):
        message_text += f"{i+1}. `{word}`\n"

    await query.message.edit_text(
        text=message_text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data=f"manage_ignore#{key}")]]),
        parse_mode=enums.ParseMode.MARKDOWN
    )
    temp.temp_data[query.message.chat.id] = {"action": "remove_ignore_word", "key": key} # Store action and key for next message

@Client.on_message(filters.private & filters.text)
async def handle_temp_data(client: Client, message: Message):
    if message.chat.id in temp.temp_data:
        data = temp.temp_data[message.chat.id]
        action = data.get("action")
        key = data.get("key")

        if action == "add_ignore_word":
            word = message.text.strip()
            if word:
                await db.add_ignore_word(message.chat.id, word)
                await message.reply_text(f"'{word}' added to ignore list.")
            else:
                await message.reply_text("Invalid input. Please provide a word.")

            # Clean up temp data and go back to manage ignore words
            del temp.temp_data[message.chat.id]
            ignore_words = await db.get_ignore_words(message.chat.id)
            message_text = "Ignore words management:\n\n"
            if not ignore_words:
                message_text = "No ignore words found for this chat."
            else:
                for i, word in enumerate(ignore_words):
                    message_text += f"{i+1}. `{word}`\n"

            buttons = [
                [InlineKeyboardButton("Add Ignore Word", callback_data=f"add_ignore_word_prompt#{key}")],
                [InlineKeyboardButton("Remove Ignore Word", callback_data=f"remove_ignore_word_prompt#{key}")]
            ]
            buttons.append([InlineKeyboardButton("Back", callback_data=f"back_to_settings#{key}")])
            await message.reply_text(
                text=message_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN
            )

        elif action == "remove_ignore_word":
            word_to_remove = message.text.strip()
            if word_to_remove:
                removed = await db.remove_ignore_word(message.chat.id, word_to_remove)
                if removed:
                    await message.reply_text(f"'{word_to_remove}' removed from ignore list.")
                else:
                    await message.reply_text(f"'{word_to_remove}' not found in ignore list.")
            else:
                await message.reply_text("Invalid input. Please provide a word.")

            # Clean up temp data and go back to manage ignore words
            del temp.temp_data[message.chat.id]
            ignore_words = await db.get_ignore_words(message.chat.id)
            message_text = "Ignore words management:\n\n"
            if not ignore_words:
                message_text = "No ignore words found for this chat."
            else:
                for i, word in enumerate(ignore_words):
                    message_text += f"{i+1}. `{word}`\n"

            buttons = [
                [InlineKeyboardButton("Add Ignore Word", callback_data=f"add_ignore_word_prompt#{key}")],
                [InlineKeyboardButton("Remove Ignore Word", callback_data=f"remove_ignore_word_prompt#{key}")]
            ]
            buttons.append([InlineKeyboardButton("Back", callback_data=f"back_to_settings#{key}")])
            await message.reply_text(
                text=message_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN
            )

@Client.on_callback_query(filters.regex(r"^back_to_settings"))
async def back_to_settings(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")

    # Re-display the manage ignore words menu
    ignore_words = await db.get_ignore_words(query.message.chat.id)

    if not ignore_words:
        message_text = "No ignore words found for this chat."
    else:
        message_text = "Here are your ignore words:\n\n"
        for i, word in enumerate(ignore_words):
            message_text += f"{i+1}. `{word}`\n"

    buttons = [
        [InlineKeyboardButton("Add Ignore Word", callback_data=f"add_ignore_word_prompt#{key}")],
        [InlineKeyboardButton("Remove Ignore Word", callback_data=f"remove_ignore_word_prompt#{key}")]
    ]
    buttons.append([InlineKeyboardButton("Back", callback_data=f"back_to_settings#{key}")])

    await query.message.edit_text(
        text=message_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )
    await query.answer()

@Client.on_callback_query(filters.regex(r"^del"))
async def delete_file(client: Client, query: CallbackQuery):
    ident, file_id = query.data.split("#")
    files_ = await get_file_details(file_id)
    if not files_:
        return await query.answer('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
    files = files_
    title = files['file_name']
    size = get_size(files['file_size'])
    f_caption = files['caption']
    settings = await get_settings(query.message.chat.id)
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                   file_size='' if size is None else size,
                                                   file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
        f_caption = f_caption
    if f_caption is None:
        f_caption = f"{files['file_name']}"
    await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")

@Client.on_callback_query(filters.regex(r"^checksub"))
async def check_subscription(client: Client, query: CallbackQuery):
    if AUTH_CHANNEL and not await is_subscribed(client, query):
        await query.answer("Jᴏɪɴ ᴏᴜʀ Bᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ ᴍᴀʜɴ! 😒", show_alert=True)
        return
    ident, kk, file_id = query.data.split("#")
    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={kk}_{file_id}")

@Client.on_callback_query(filters.regex(r"^pages"))
async def pages_callback(client: Client, query: CallbackQuery):
    await query.answer()

@Client.on_callback_query(filters.regex(r"^send_fsall"))
async def send_all_files_callback(client: Client, query: CallbackQuery):
    temp_var, ident, key, offset = query.data.split("#")
    search = BUTTON0.get(key)
   # if not search:
    #    await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
    #    return
    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
    await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
    search = BUTTONS1.get(key)
    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
    await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
    search = BUTTONS2.get(key)
    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
    await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
    await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^send_fall"))
async def send_all_files_callback_fallback(client: Client, query: CallbackQuery):
    temp_var, ident, key, offset = query.data.split("#")
    search = FRESH.get(key)
 #   if not search:
   #     await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
   #     return
    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
    await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
    await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^killfilesdq"))
async def kill_files_dq_callback(client: Client, query: CallbackQuery):
    ident, keyword = query.data.split("#")
    #await query.message.edit_text(f"<b>Fetching Files for your query {keyword} on DB... Please wait...</b>")
    files, total = await get_bad_files(keyword)
    await query.message.edit_text("<b>File deletion process will start in 5 seconds !</b>")
    await asyncio.sleep(5)
    deleted = 0
    async with lock:
        try:
            for file in files:
                file_ids = file["file_id"]
                file_name = file["file_name"]
                result = col.delete_one({
                    'file_id': file_ids,
                })
                if not result.deleted_count:
                    result = sec_col.delete_one({
                        'file_id': file_ids,
                    })
                if result.deleted_count:
                    logger.info(f'File Found for your query {keyword}! Successfully deleted {file_name} from database.')
                deleted += 1
                if deleted % 50 == 0:
                    await query.message.edit_text(f"<b>Process started for deleting files from DB. Successfully deleted {str(deleted)} files from DB for your query {keyword} !\n\nPlease wait...</b>")
        except Exception as e:
            logger.exception(e)
            await query.message.edit_text(f'Error: {e}')
        else:
            await query.message.edit_text(f"<b>Process Completed for file deletion !\n\nSuccessfully deleted {str(deleted)} files from database for your query {keyword}.</b>")

@Client.on_callback_query(filters.regex(r"^opnsetgrp"))
async def open_settings_group_callback(client: Client, query: CallbackQuery):
    ident, grp_id = query.data.split("#")
    userid = query.from_user.id if query.from_user else None
    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        await query.answer("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True)
        return
    title = query.message.chat.title
    settings = await get_settings(grp_id)
    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton('Rᴇsᴜʟᴛ Pᴀɢᴇ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                InlineKeyboardButton('Bᴜᴛᴛᴏɴ' if settings["button"] else 'Tᴇxᴛ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                     callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                     callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                     callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                InlineKeyboardButton('5 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                     callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                                     callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                     callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                     callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                     callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('SʜᴏʀᴛLɪɴᴋ',
                                     callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                                     callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Iɢɴᴏʀᴇ Wᴏʀᴅs',
                                     callback_data=f'manage_ignore#{grp_id}'),
                InlineKeyboardButton('Mᴀɴᴀɢᴇ',
                                     callback_data=f'manage_ignore#{grp_id}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
        await query.message.edit_reply_markup(reply_markup)

@Client.on_callback_query(filters.regex(r"^opnsetpm"))
async def open_settings_pm_callback(client: Client, query: CallbackQuery):
    ident, grp_id = query.data.split("#")
    userid = query.from_user.id if query.from_user else None
    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        await query.answer("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True)
        return
    title = query.message.chat.title
    settings = await get_settings(grp_id)
    btn2 = [[
             InlineKeyboardButton("Cʜᴇᴄᴋ PM", url=f"telegram.me/{temp.U_NAME}")
           ]]
    reply_markup = InlineKeyboardMarkup(btn2)
    await query.message.edit_text(f"<b>Yᴏᴜʀ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ ғᴏʀ {title} ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ʏᴏᴜʀ PM</b>")
    await query.message.edit_reply_markup(reply_markup)
    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton('Rᴇsᴜʟᴛ Pᴀɢᴇ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                InlineKeyboardButton('Bᴜᴛᴛᴏɴ' if settings["button"] else 'Tᴇxᴛ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                     callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                     callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                     callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                InlineKeyboardButton('5 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                     callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Aᴜᴛᴏ-FɪʟᴛᴇR',
                                     callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                     callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                     callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                     callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('SʜᴏʀᴛLɪɴᴋ',
                                     callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                                     callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            chat_id=userid,
            text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=query.message.id
        )

@Client.on_callback_query(filters.regex(r"^show_option"))
async def show_option_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    btn = [[
            InlineKeyboardButton("Uɴᴀᴠᴀɪʟᴀʙʟᴇ", callback_data=f"unalert#{from_user}"),
            InlineKeyboardButton("Uᴘʟᴏᴀᴅᴇᴅ", callback_data=f"upalert#{from_user}")
          ],[
            InlineKeyboardButton("Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ", callback_data=f"alalert#{from_user}")
          ]]
    btn2 = [[
             InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
           ]]
    if query.from_user.id in ADMINS:
        user = await client.get_users(from_user)
        reply_markup = InlineKeyboardMarkup(btn)
        await query.message.edit_reply_markup(reply_markup)
        await query.answer("Hᴇʀᴇ ᴀʀᴇ ᴛʜᴇ ᴏᴘᴛɪᴏɴs !")
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^unavailable"))
async def unavailable_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    btn = [[
            InlineKeyboardButton("⚠️ Uɴᴀᴠᴀɪʟᴀʙʟᴇ ⚠️", callback_data=f"unalert#{from_user}")
          ]]
    btn2 = [[
             InlineKeyboardButton('Jᴏɪɴ CʜᴀɴɴᴇL', url=link.invite_link),
             InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
           ],[
             InlineKeyboardButton("Rᴇᴏ̨ᴜᴇsᴛ Gʀᴏᴜᴘ Lɪɴᴋ", url="https://t.me/vj_bots")
           ]]
    if query.from_user.id in ADMINS:
        user = await client.get_users(from_user)
        reply_markup = InlineKeyboardMarkup(btn)
        content = query.message.text
        await query.message.edit_text(f"<b><strike>{content}</strike></b>")
        await query.message.edit_reply_markup(reply_markup)
        await query.answer("Sᴇᴛ ᴛᴏ Uɴᴀᴠᴀɪʟᴀʙʟᴇ !")
        try:
            await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        except UserIsBlocked:
            await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^uploaded"))
async def uploaded_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    btn = [[
            InlineKeyboardButton("✅ Uᴘʟᴏᴀᴅᴇᴅ ✅", callback_data=f"upalert#{from_user}")
          ]]
    btn2 = [[
             InlineKeyboardButton('Jᴏɪɴ CʜᴀɴɴᴇL', url=link.invite_link),
             InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
           ],[
             InlineKeyboardButton("Rᴇᴏ̨ᴜᴇsᴛ Gʀᴏᴜᴘ Lɪɴᴋ", url="https://t.me/vj_bots")
           ]]
    if query.from_user.id in ADMINS:
        user = await client.get_users(from_user)
        reply_markup = InlineKeyboardMarkup(btn)
        content = query.message.text
        await query.message.edit_text(f"<b><strike>{content}</strike></b>")
        await query.message.edit_reply_markup(reply_markup)
        await query.answer("Sᴇᴛ ᴛᴏ Uᴘʟᴏᴀᴅᴇᴅ !")
        try:
            await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        except UserIsBlocked:
            await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^already_available"))
async def already_available_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    btn = [[
        InlineKeyboardButton("🟢 Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ 🟢", callback_data=f"alalert#{from_user}")
    ]]
    btn2 = [[
        InlineKeyboardButton('Jᴏɪɴ CʜᴀɴɴᴇL', url=link.invite_link),
        InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
    ],[
        InlineKeyboardButton("Rᴇᴏ̨ᴜᴇsᴛ Gʀᴏᴜᴘ Lɪɴᴋ", url="https://t.me/vj_bots")
    ]]
    if query.from_user.id in ADMINS:
        user = await client.get_users(from_user)
        reply_markup = InlineKeyboardMarkup(btn)
        content = query.message.text
        await query.message.edit_text(f"<b><strike>{content}</strike></b>")
        await query.message.edit_reply_markup(reply_markup)
        await query.answer("Sᴇᴛ ᴛᴏ Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !")
        try:
            await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        except UserIsBlocked:
            await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^alalert"))
async def alalert_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    if int(query.from_user.id) == int(from_user):
        user = await client.get_users(from_user)
        await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !", show_alert=True)
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^upalert"))
async def upalert_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    if int(query.from_user.id) == int(from_user):
        user = await client.get_users(from_user)
        await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇǫᴜᴇsᴛ ɪs Uᴘʟᴏᴀᴅᴇᴅ !", show_alert=True)
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^unalert"))
async def unalert_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    if int(query.from_user.id) == int(from_user):
        user = await client.get_users(from_user)
        await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇǫᴜᴇsᴛ ɪs Uɴᴀᴠᴀɪʟᴀʙʟᴇ !", show_alert=True)
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^generate_stream_link"))
async def generate_stream_link_callback(client: Client, query: CallbackQuery):
    _, file_id = query.data.split(":")
    try:
        log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=file_id)
        fileName = {quote_plus(get_name(log_msg))}
        stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        button = [[
            InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download),
            InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream)
        ],[
            InlineKeyboardButton('• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •', web_app=WebAppInfo(url=stream))
        ]]
        await query.message.edit_reply_markup(InlineKeyboardMarkup(button))
    except Exception as e:
        print(e)
        await query.answer(f"something went wrong\n\n{e}", show_alert=True)
        return

@Client.on_callback_query(filters.regex(r"^reqinfo"))
async def reqinfo_callback(client: Client, query: CallbackQuery):
    await query.answer(text=script.REQINFO, show_alert=True)

@Client.on_callback_query(filters.regex(r"^select"))
async def select_callback(client: Client, query: CallbackQuery):
    await query.answer(text=script.SELECT, show_alert=True)

@Client.on_callback_query(filters.regex(r"^sinfo"))
async def sinfo_callback(client: Client, query: CallbackQuery):
    await query.answer(text=script.SINFO, show_alert=True)

@Client.on_callback_query(filters.regex(r"^start"))
async def start_callback(client: Client, query: CallbackQuery):
    if PREMIUM_AND_REFERAL_MODE == True:
        buttons = [[
            InlineKeyboardButton('⤬ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ],[
            InlineKeyboardButton('ᴇᴀʀɴ ᴍᴏɴᴇʏ', callback_data="shortlink_info"),
            InlineKeyboardButton('ᴍᴏᴠɪᴇ ɢʀᴏᴜᴘ', url=GRP_LNK)
        ],[
            InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about')
        ],[
            InlineKeyboardButton('ᴘʀᴇᴍɪᴜᴍ ᴀɴᴅ ʀᴇғᴇʀʀᴀʟ', callback_data='subscription')
        ],[
            InlineKeyboardButton('ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url=CHNL_LNK)
        ]]
    else:
        buttons = [[
            InlineKeyboardButton('⤬ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ],[
            InlineKeyboardButton('ᴇᴀʀɴ ᴍᴏɴᴇʏ', callback_data="shortlink_info"),
            InlineKeyboardButton('ᴍᴏᴠɪᴇ ɢʀᴏᴜᴘ', url=GRP_LNK)
        ],[
            InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about')
        ],[
            InlineKeyboardButton('ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url=CHNL_LNK)
        ]]
    if CLONE_MODE == True:
        buttons.append([InlineKeyboardButton('ᴄʀᴇᴀᴛᴇ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', callback_data='clone')])
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    await query.message.edit_text(
        text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )
    await query.answer(MSG_ALRT)

@Client.on_callback_query(filters.regex(r"^clone"))
async def clone_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='start')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.CLONE_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^filters"))
async def filters_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('Mᴀɴᴜᴀʟ FIʟᴛᴇR', callback_data='manuelfilter'),
        InlineKeyboardButton('Aᴜᴛᴏ FIʟᴛᴇR', callback_data='autofilter')
    ],[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help'),
        InlineKeyboardButton('Gʟᴏʙᴀʟ FɪʟᴛᴇRs', callback_data='global_filters')
    ]]

    reply_markup = InlineKeyboardMarkup(buttons)
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    await query.message.edit_text(
        text=script.ALL_FILTERS.format(query.from_user.mention),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^global_filters"))
async def global_filters_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='filters')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.GFILTER_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^help"))
async def help_callback(client: Client, query: CallbackQuery):
    buttons = [[
         InlineKeyboardButton('⚙️ ᴀᴅᴍɪɴ ᴏɴʟʏ 🔧', callback_data='admin'),
     ], [
         InlineKeyboardButton('ʀᴇɴᴀᴍᴇ', callback_data='r_txt'),
         InlineKeyboardButton('sᴛʀᴇᴀᴍ/ᴅᴏᴡɴʟᴏᴀᴅ', callback_data='s_txt')
     ], [
         InlineKeyboardButton('ꜰɪʟᴇ ꜱᴛᴏʀᴇ', callback_data='store_file'),
         InlineKeyboardButton('ᴛᴇʟᴇɢʀᴀᴘʜ', callback_data='tele')
     ], [
         InlineKeyboardButton('ᴄᴏɴɴᴇᴄᴛɪᴏɴꜱ', callback_data='coct'),
         InlineKeyboardButton('ꜰɪʟᴛᴇʀꜱ', callback_data='filters')
     ], [
         InlineKeyboardButton('ʏᴛ-ᴅʟ', callback_data='ytdl'),
         InlineKeyboardButton('ꜱʜᴀʀᴇ ᴛᴇxᴛ', callback_data='share')
     ], [
         InlineKeyboardButton('ꜱᴏɴɢ', callback_data='song'),
         InlineKeyboardButton('ᴇᴀʀɴ ᴍᴏɴᴇʏ', callback_data='shortlink_info')
     ], [
         InlineKeyboardButton('ꜱᴛɪᴄᴋᴇʀ-ɪᴅ', callback_data='sticker'),
         InlineKeyboardButton('ᴊ-ꜱᴏɴ', callback_data='json')
     ], [
         InlineKeyboardButton('🏠 𝙷𝙾𝙼𝙴 🏠', callback_data='start')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    await query.message.edit_text(
        text=script.HELP_TXT.format(query.from_user.mention),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^about"))
async def about_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
        InlineKeyboardButton('Sᴏᴜʀᴄᴇ Cᴏᴅᴇ', url="https://github.com/VJBots/VJ-FILTER-BOT")
    ],[
        InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
        InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close_data')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.ABOUT_TXT.format(temp.U_NAME, temp.B_NAME, OWNER_LNK),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^subscription"))
async def subscription_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='start')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.SUBSCRIPTION_TXT.format(REFERAL_PREMEIUM_TIME, temp.U_NAME, query.from_user.id, REFERAL_COUNT),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^manuelfilter"))
async def manuelfilter_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='filters'),
        InlineKeyboardButton('Bᴜᴛᴛᴏɴs', callback_data='button')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.MANUELFILTER_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^button"))
async def button_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='manuelfilter')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.BUTTON_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^autofilter"))
async def autofilter_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='filters')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.AUTOFILTER_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^coct"))
async def coct_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.CONNECTION_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^admin"))
async def admin_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help'),
        InlineKeyboardButton('ᴇxᴛʀᴀ', callback_data='extra')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.ADMIN_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^store_file"))
async def store_file_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.FILE_STORE_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^r_txt"))
async def r_txt_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.RENAME_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^s_txt"))
async def s_txt_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.STREAM_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^extra"))
async def extra_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='admin')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.EXTRAMOD_TXT.format(OWNER_LNK, CHNL_LNK),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^stats"))
async def stats_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help'),
        InlineKeyboardButton('⟲ Rᴇғʀᴇsʜ', callback_data='rfrsh')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    filesp = col.count_documents({})
    totalsec = sec_col.count_documents({})
    stats = vjdb.command('dbStats')
    used_dbSize = (stats['dataSize']/(1024*1024))+(stats['indexSize']/(1024*1024))
    free_dbSize = 512-used_dbSize
    stats2 = sec_db.command('dbStats')
    used_dbSize2 = (stats2['dataSize']/(1024*1024))+(stats2['indexSize']/(1024*1024))
    free_dbSize2 = 512-used_dbSize2
    stats3 = mydb.command('dbStats')
    used_dbSize3 = (stats3['dataSize']/(1024*1024))+(stats3['indexSize']/(1024*1024))
    free_dbSize3 = 512-used_dbSize3
    await query.message.edit_text(
        text=script.STATUS_TXT.format((int(filesp)+int(totalsec)), total_users, totl_chats, filesp, round(used_dbSize, 2), round(free_dbSize, 2), totalsec, round(used_dbSize2, 2), round(free_dbSize2, 2), round(used_dbSize3, 2), round(free_dbSize3, 2)),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^rfrsh"))
async def rfrsh_callback(client: Client, query: CallbackQuery):
    await query.answer("Fetching MongoDb DataBase")
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help'),
        InlineKeyboardButton('⟲ Rᴇғʀᴇsʜ', callback_data='rfrsh')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    filesp = col.count_documents({})
    totalsec = sec_col.count_documents({})
    stats = vjdb.command('dbStats')
    used_dbSize = (stats['dataSize']/(1024*1024))+(stats['indexSize']/(1024*1024))
    free_dbSize = 512-used_dbSize
    stats2 = sec_db.command('dbStats')
    used_dbSize2 = (stats2['dataSize']/(1024*1024))+(stats2['indexSize']/(1024*1024))
    free_dbSize2 = 512-used_dbSize2
    stats3 = mydb.command('dbStats')
    used_dbSize3 = (stats3['dataSize']/(1024*1024))+(stats3['indexSize']/(1024*1024))
    free_dbSize3 = 512-used_dbSize3
    await query.message.edit_text(
        text=script.STATUS_TXT.format((int(filesp)+int(totalsec)), total_users, totl_chats, filesp, round(used_dbSize, 2), round(free_dbSize, 2), totalsec, round(used_dbSize2, 2), round(free_dbSize2, 2), round(used_dbSize3, 2), round(free_dbSize3, 2)),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^shortlink_info"))
async def shortlink_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("👇Select Your Language 👇", callback_data="laninfo")
    ],[
        InlineKeyboardButton("Tamil", callback_data="tamil_info"),
        InlineKeyboardButton("English", callback_data="english_info"),
        InlineKeyboardButton("Hindi", callback_data="hindi_info")
    ],[
        InlineKeyboardButton("Malayalam", callback_data="malayalam_info"),
        InlineKeyboardButton("Urdu", callback_data="urdu_info"),
        InlineKeyboardButton("Bangla", callback_data="bangladesh_info")
    ],[
        InlineKeyboardButton("Telugu", callback_data="telugu_info"),
        InlineKeyboardButton("Kannada", callback_data="kannada_info"),
        InlineKeyboardButton("Gujarati", callback_data="gujarati_info")
    ],[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.SHORTLINK_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^tele"))
async def tele_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="help"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.TELE_TXT),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^ytdl"))
async def ytdl_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text="● ◌ ◌"
    )
    await query.message.edit_text(
        text="● ● ◌"
    )
    await query.message.edit_text(
        text="● ● ●"
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    await query.message.edit_text(
        text=script.YTDL_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^share"))
async def share_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="help"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.SHARE_TXT),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^song"))
async def song_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="help"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.SONG_TXT),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^json"))
async def json_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text="● ◌ ◌"
    )
    await query.message.edit_text(
        text="● ● ◌"
    )
    await query.message.edit_text(
        text="● ● ●"
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    await query.message.edit_text(
        text=script.JSON_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^sticker"))
async def sticker_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="help"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.STICKER_TXT),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^tamil_info"))
async def tamil_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.TAMIL_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^english_info"))
async def english_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.ENGLISH_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^hindi_info"))
async def hindi_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.HINDI_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^telugu_info"))
async def telugu_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.TELUGU_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^malayalam_info"))
async def malayalam_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.MALAYALAM_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^urdu_info"))
async def urdu_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.URDU_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^bangladesh_info"))
async def bangladesh_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.BANGLADESH_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^kannada_info"))
async def kannada_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.KANNADA_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^gujarati_info"))
async def gujarati_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.GUJARATI_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^setgs"))
async def setgs_callback(client: Client, query: CallbackQuery):
    ident, set_type, status, grp_id = query.data.split("#")
    grpid = await active_connection(str(query.from_user.id))

    if str(grp_id) != str(grpid):
        await query.message.edit("Yᴏᴜʀ Aᴄᴛɪᴠᴇ Cᴏɴɴᴇᴄᴛɪᴏɴ Hᴀs Bᴇᴇɴ Cʜᴀɴɢᴇᴅ. Gᴏ Tᴏ /connections ᴀɴᴅ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴ.")
        return await query.answer(MSG_ALRT)

    if status == "True":
        await save_group_settings(grpid, set_type, False)
    else:
        settings = await get_settings(grpid)
        if set_type == "is_shortlink" and not settings['shortlink']:
            return await query.answer(text = "First Add Your Shortlink Url And Api By /shortlink Command, Then Turn Me On.", show_alert = True)
        await save_group_settings(grpid, set_type, True)

    settings = await get_settings(grpid)

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton('Rᴇsᴜʟᴛ Pᴀɢᴇ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                InlineKeyboardButton('Bᴜᴛᴛᴏɴ' if settings["button"] else 'Tᴇxᴛ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                     callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                     callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                     callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                InlineKeyboardButton('5 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                     callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Aᴜᴛᴏ-FɪʟᴛᴇR',
                                     callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                     callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                     callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                     callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('SʜᴏʀᴛLɪɴᴋ',
                                     callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                                     callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_reply_markup(reply_markup)
    await query.answer(MSG_ALRT)

async def auto_filter(client, name, msg, reply_msg, ai_search, spoll=False):
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if not spoll:
        message = msg
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
            search = name
            search = search.lower()
            find = search.split(" ")
            search = ""
            removes = ["in","upload", "series", "full", "horror", "thriller", "mystery", "print", "file"]
            for x in find:
                if x in removes:
                    continue
                else:
                    search = search + x + " "
            search = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|bro|bruh|broh|helo|that|find|dubbed|link|venum|iruka|pannunga|pannungga|anuppunga|anupunga|anuppungga|anupungga|film|undo|kitti|kitty|tharu|kittumo|kittum|movie|any(one)|with\ssubtitle(s)?)", "", search, flags=re.IGNORECASE)
            search = re.sub(r"\s+", " ", search).strip()
            search = search.replace("-", " ")
            search = search.replace(":", "")
            search = search.replace(".", "")
            files, offset, total_results = await get_search_results(message.chat.id ,search, offset=0, filter=True)
            settings = await get_settings(message.chat.id)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(client, name, msg, reply_msg, ai_search)
                else:
                    return await reply_msg.edit_text(f"**⚠️ No File Found For Your Query - {name}**\n**Make Sure Spelling Is Correct.**")
        else:
            return
    else:
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
        settings = await get_settings(message.chat.id)
        await msg.message.delete()
    pre = 'filep' if settings['file_secure'] else 'file'
    key = f"{message.chat.id}-{message.id}"
    req = message.from_user.id if message.from_user else 0
    FRESH[key] = search
    temp.GETALL[key] = files
    temp.SHORT[message.from_user.id] = message.chat.id
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
    else:
        btn = []
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
            InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
            InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
            InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
            InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])
    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
            else:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0])['file_name']) if settings["imdb"] else None
    cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
    remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
    TEMPLATE = script.IMDB_TEMPLATE_TXT
    if imdb:
        cap = TEMPLATE.format(
            qurey=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
        temp.IMDB_CAP[message.from_user.id] = cap
        if not settings["button"]:
            cap+="<b>\n\n<u>🍿 Your Movie Files 👇</u></b>\n"
            for file in files:
                cap += f"<b>\n📁 <a href='https://telegram.me/{temp.U_NAME}?start=files_{file['file_id']}'>[{get_size(file['file_size'])}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))}\n</a></b>"
    else:
        if settings["button"]:
            cap = f"<b>🎬 Movie Name :- {search}\n📨 Rᴇǫᴜᴇsᴛᴇᴅ Bʏ :- {message.from_user.mention}\n⏰ ʀᴇsᴜʟᴛ sʜᴏᴡ ɪɴ :- {remaining_seconds} sᴇᴄᴏɴᴅs\n\n</b>"
        else:
            cap = f"<b>🎬 Movie Name :- {search}\n📨 Rᴇǫᴜᴇsᴛᴇᴅ Bʏ :- {message.from_user.mention}\n⏰ ʀᴇsᴜʟᴛ sʜᴏᴡ ɪɴ :- {remaining_seconds} sᴇᴄᴏɴᴅs\n\n</b>"
            cap+="<b><u>🍿 Your Movie Files 👇</u></b>\n\n"
            for file in files:
                cap += f"<b>📁 <a href='https://telegram.me/{temp.U_NAME}?start=files_{file['file_id']}'>[{get_size(file['file_size'])}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))}\n\n</a></b>"

    if imdb and imdb.get('poster'):
        try:
            hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            await reply_msg.delete()
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await hehe.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await hehe.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaWebpageMedia):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            hmm = await message.reply_photo(photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            await reply_msg.delete()
            try:
               if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await hmm.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await hmm.delete()
        except Exception as e:
            logger.exception(e)
            fek = await reply_msg.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn))
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await fek.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await fek.delete()
    else:
        try:
            fuk = await reply_msg.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await fuk.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await fuk.delete()
        except Exception as e:
            logger.exception(e)
            try:
                await reply_msg.delete()
            except:
                pass


async def advantage_spell_chok(client, name, msg, reply_msg, vj_search):
    mv_id = msg.id
    mv_rqst = name
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    settings = await get_settings(msg.chat.id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception as e:
        logger.exception(e)
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await reply_msg.edit_text(text=script.I_CUDNT.format(mv_rqst), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist = []
    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await reply_msg.edit_text(text=script.I_CUDNT.format(mv_rqst), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist += [movie.get('title') for movie in movies]
    movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]
    SPELL_CHECK[mv_id] = movielist
    if AI_SPELL_CHECK == True and vj_search == True:
        vj_search_new = False
        vj_ai_msg = await reply_msg.edit_text("<b><i>I Am Trying To Find Your Movie With Your Wrong Spelling.</i></b>")
        movienamelist = []
        movienamelist += [movie.get('title') for movie in movies]
        for techvj in movienamelist:
            try:
                mv_rqst = mv_rqst.capitalize()
            except:
                pass
            if mv_rqst.startswith(techvj[0]):
                await auto_filter(client, techvj, msg, reply_msg, vj_search_new)
                break
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await reply_msg.edit_text(text=script.I_CUDNT.format(mv_rqst), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(30)
        await k.delete()
        return
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=movie_name.strip(),
                    callback_data=f"spol#{reqstr1}#{k}",
                )
            ]
            for k, movie_name in enumerate(movielist)
        ]
        btn.append([InlineKeyboardButton("Close", callback_data=f'spol#{reqstr1}#close_spellcheck')])
        spell_check_del = await reply_msg.edit_text(
            text=script.CUDNT_FND.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(btn)
        )
        try:
            if settings['auto_delete']:
                await asyncio.sleep(600)
                await spell_check_del.delete()
        except KeyError:
            grpid = await active_connection(str(msg.from_user.id))
            await save_group_settings(grpid, 'auto_delete', True)
            settings = await get_settings(msg.chat.id)
            if settings['auto_delete']:
                await asyncio.sleep(600)
                await spell_check_del.delete()

async def manual_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)

                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            protect_content=True if settings["file_secure"] else False,
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                ai_search = True
                                reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                await auto_filter(client, message.text, message, reply_msg, ai_search)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                ai_search = True
                                reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                await auto_filter(client, message.text, message, reply_msg, ai_search)
                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                ai_search = True
                                reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                await auto_filter(client, message.text, message, reply_msg, ai_search)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                ai_search = True
                                reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                await auto_filter(client, message.text, message, reply_msg, ai_search)

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

async def global_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        ai_search = True
                                        reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                        await auto_filter(client, message.text, message, reply_msg, ai_search)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        ai_search = True
                                        reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                        await auto_filter(client, message.text, message, reply_msg, ai_search)
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()

                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        ai_search = True
                                        reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                        await auto_filter(client, message.text, message, reply_msg, ai_search)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        ai_search = True
                                        reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                        await auto_filter(client, message.text, message, reply_msg, ai_search)
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()

                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)
                        else:
                            try:
                                if settings['auto_delete']:
                                    await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await joelkb.delete()


                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os, logging, string, asyncio, time, re, ast, random, math, pytz, pyrogram
from datetime import datetime, timedelta, date, time
from Script import script
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo, Message
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from utils import get_size, is_subscribed, pub_is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink, get_tutorial, send_all, get_cap
from database.users_chats_db import db
from database.ia_filterdb import col, sec_col, db as vjdb, sec_db, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import del_all, find_filter, get_filters
from database.connections_mdb import mydb, active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from database.gfilters_mdb import find_gfilter, get_gfilters, del_allg
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size

logger = logging.getLogger(__name__)
logger.setLevel(ERROR)
lock = asyncio.Lock()

BUTTON = {}
BUTTONS = {}
FRESH = {}
BUTTONS0 = {}
BUTTONS1 = {}
BUTTONS2 = {}
SPELL_CHECK = {}

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if message.chat.id != SUPPORT_CHAT_ID:
        settings = await get_settings(message.chat.id)
        chatid = message.chat.id
        user_id = message.from_user.id if message.from_user else 0
        if settings['fsub'] != None:
            try:
                btn = await pub_is_subscribed(client, message, settings['fsub'])
                if btn:
                    btn.append([InlineKeyboardButton("Unmute Me 🔕", callback_data=f"unmuteme#{int(user_id)}")])
                    await client.restrict_chat_member(chatid, message.from_user.id, ChatPermissions(can_send_messages=False))
                    await message.reply_photo(photo=random.choice(PICS), caption=f"👋 Hello {message.from_user.mention},\n\nPlease join the channel then click on unmute me button. 😇", reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)
                    return
            except Exception as e:
                print(e)

        manual = await manual_filters(client, message)
        if manual == False:
            settings = await get_settings(message.chat.id)
            try:
                if settings['auto_ffilter']:
                    ai_search = True
                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                    await auto_filter(client, message.text, message, reply_msg, ai_search)
            except KeyError:
                grpid = await active_connection(str(message.from_user.id))
                await save_group_settings(grpid, 'auto_ffilter', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_ffilter']:
                    ai_search = True
                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                    await auto_filter(client, message.text, message, reply_msg, ai_search)
    else: #a better logic to avoid repeated lines of code in auto_filter function
        search = message.text
        temp_files, temp_offset, total_results = await get_search_results(chat_id=message.chat.id, query=search.lower(), offset=0, filter=True)
        if total_results == 0:
            return
        else:
            return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. \n\nTʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...\n\nJᴏɪɴ ᴀɴᴅ Sᴇᴀʀᴄʜ Hᴇʀᴇ - {GRP_LNK}</b>")

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if content.startswith("/") or content.startswith("#") or content.startswith(".") or content.startswith(",") or content.startswith("@") or content.startswith("https") or content.startswith("www.") or content.startswith("-") or content.startswith("t.me"): return  # ignore commands and hashtags
    if PM_SEARCH == True:
        ai_search = True
        reply_msg = await bot.send_message(message.from_user.id, f"<b><i>Searching For {content} 🔍</i></b>", reply_to_message_id=message.id)
        await auto_filter(bot, content, message, reply_msg, ai_search)

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = FRESH.get(key)
   # if not search:
      #  await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
       # return

    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    temp.GETALL[key] = files
    temp.SHORT[query.from_user.id] = query.message.chat.id
    settings = await get_settings(query.message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
    else:
        btn = []
        btn.insert(0, [
            InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
            InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
            InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
            InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
            InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])
    try:
        if settings['max_btn']:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'max_btn', True)
        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append(
                [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
            )
        elif off_set is None:
            btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
        else:
            btn.append(
                [
                    InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                    InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                    InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                ],
            )
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
   # if not movies:
     #   return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[(int(movie_))]
    movie = re.sub(r"[:\-]", " ", movie)
    movie = re.sub(r"\s+", " ", movie).strip()
    await query.answer(script.TOP_ALRT_MSG)
    gl = await global_filters(bot, query.message, text=movie)
    if gl == False:
        k = await manual_filters(bot, query.message, text=movie)
        if k == False:
            files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
            if files:
                k = (movie, files, offset, total_results)
                ai_search = True
                reply_msg = await query.message.edit_text(f"<b><i>Searching For {movie} 🔍</i></b>")
                await auto_filter(bot, movie, query, reply_msg, ai_search, k)
            else:
                reqstr1 = query.from_user.id if query.from_user else 0
                reqstr = await bot.get_users(reqstr1)
                if NO_RESULTS_MSG:
                    await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)))
                k = await query.message.edit(script.MVE_NT_FND)
                await asyncio.sleep(10)
                await k.delete()

# Year
@Client.on_callback_query(filters.regex(r"^years#"))
async def years_cb_handler(client: Client, query: CallbackQuery):

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    btn = []
    for i in range(0, len(YEARS)-1, 4):
        row = []
        for j in range(4):
            if i+j < len(YEARS):
                row.append(
                    InlineKeyboardButton(
                        text=YEARS[i+j].title(),
                        callback_data=f"fy#{YEARS[i+j].lower()}#{key}"
                    )
                )
        btn.append(row)

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="sᴇʟᴇᴄᴛ ʏᴏᴜʀ ʏᴇᴀʀ", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fy#homepage#{key}")])

    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass

@Client.on_callback_query(filters.regex(r"^fy#"))
async def filter_yearss_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    baal = lang in search
    if baal:
        search = search.replace(lang, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(req) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    if lang != "homepage":
        search = f"{search} {lang}"
    BUTTONS[key] = search

    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
    else:
        btn = []
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
                InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
                InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
                InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
                InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
            ]
        )

    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )

            else:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
        )
    if lang != "homepage":
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fy#homepage#{key}")])

    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()

# Episode

@Client.on_callback_query(filters.regex(r"^episodes#"))
async def episodes_cb_handler(client: Client, query: CallbackQuery):

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    btn = []
    for i in range(0, len(EPISODES)-1, 4):
        row = []
        for j in range(4):
            if i+j < len(EPISODES):
                row.append(
                    InlineKeyboardButton(
                        text=EPISODES[i+j].title(),
                        callback_data=f"fe#{EPISODES[i+j].lower()}#{key}"
                    )
                )
        btn.append(row)

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴇᴘɪsᴏᴅᴇ", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fe#homepage#{key}")])

    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass

@Client.on_callback_query(filters.regex(r"^fe#"))
async def filter_episodes_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    baal = lang in search
    if baal:
        search = search.replace(lang, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(req) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    if lang != "homepage":
        search = f"{search} {lang}"
    BUTTONS[key] = search

    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
    else:
        btn = []
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
                InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
                InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
                InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
                InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
            ]
        )

    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )

            else:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
        )
    if lang != "homepage":
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fe#homepage#{key}")])

    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()



#languages

@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    btn = []
    for i in range(0, len(LANGUAGES)-1, 2):
        btn.append([
            InlineKeyboardButton(
                text=LANGUAGES[i].title(),
                callback_data=f"fl#{LANGUAGES[i].lower()}#{key}"
            ),
            InlineKeyboardButton(
                text=LANGUAGES[i+1].title(),
                callback_data=f"fl#{LANGUAGES[i+1].lower()}#{key}"
            ),
        ])

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="👇 sᴇ𝗅𝖾𝖼𝗍 𝖸𝗈𝗎𝗋 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾𝗌 👇", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fl#homepage#{key}")])

    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass

@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    baal = lang in search
    if baal:
        search = search.replace(lang, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(req) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    if lang != "homepage":
        search = f"{search} {lang}"
    BUTTONS[key] = search

    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
    else:
        btn = []
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
                InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
                InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
                InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
                InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])

    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )

            else:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
        )
    if lang != "homepage":
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fl#homepage#{key}")])

    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()



@Client.on_callback_query(filters.regex(r"^seasons#"))
async def seasons_cb_handler(client: Client, query: CallbackQuery):

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass

    _, key = query.data.split("#")
    search = FRESH.get(key)
    BUTTONS[key] = None
    try:
        search = search.replace(' ', '_')
    except:
        pass
    btn = []
    for i in range(0, len(SEASONS)-1, 2):
        btn.append([
            InlineKeyboardButton(
                text=SEASONS[i].title(),
                callback_data=f"fs#{SEASONS[i].lower()}#{key}"
            ),
            InlineKeyboardButton(
                text=SEASONS[i+1].title(),
                callback_data=f"fs#{SEASONS[i+1].lower()}#{key}"
            ),
        ])

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="👇 𝖲𝖾𝗅𝖾𝖼𝗍 Season 👇", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ​↭", callback_data=f"next_{req}_{key}_{offset}")])

    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass

@Client.on_callback_query(filters.regex(r"^fs#"))
async def filter_seasons_cb_handler(client: Client, query: CallbackQuery):
    _, seas, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    sea = ""
    season_search = ["s01","s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "s10", "season 01","season 02","season 03","season 04","season 05","season 06","season 07","season 08","season 09","season 10", "season 1","season 2","season 3","season 4","season 5","season 6","season 7","season 8","season 9"]
    for x in range (len(season_search)):
        if season_search[x] in search:
            sea = season_search[x]
            break
    if sea:
        search = search.replace(sea, "")
    else:
        search = search

    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(req) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass

    searchagn = search
    search1 = search
    search2 = search
    search = f"{search} {seas}"
    BUTTONS0[key] = search

    files, _, _ = await get_search_results(chat_id, search, max_results=10)
    files = [file for file in files if re.search(seas, file["file_name"], re.IGNORECASE)]

    seas1 = "s01" if seas == "season 1" else "s02" if seas == "season 2" else "s03" if seas == "season 3" else "s04" if seas == "season 4" else "s05" if seas == "season 5" else "s06" if seas == "season 6" else "s07" if seas == "season 7" else "s08" if seas == "season 8" else "s09" if seas == "season 9" else "s10" if seas == "season 10" else ""
    search1 = f"{search1} {seas1}"
    BUTTONS1[key] = search1
    files1, _, _ = await get_search_results(chat_id, search1, max_results=10)
    files1 = [file for file in files1 if re.search(seas1, file["file_name"], re.IGNORECASE)]

    if files1:
        files.extend(files1)

    seas2 = "season 01" if seas == "season 1" else "season 02" if seas == "season 2" else "season 03" if seas == "season 3" else "season 04" if seas == "season 4" else "season 05" if seas == "season 5" else "season 06" if seas == "season 6" else "season 07" if seas == "season 7" else "season 08" if seas == "season 8" else "season 09" if seas == "season 9" else "s010"
    search2 = f"{search2} {seas2}"
    BUTTONS2[key] = search2
    files2, _, _ = await get_search_results(chat_id, search2, max_results=10)
    files2 = [file for file in files2 if re.search(seas2, file["file_name"], re.IGNORECASE)]

    if files2:
        files.extend(files2)

    if not files:
        await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
                InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
                InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
                InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
                InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])
    else:
        btn = []
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
                InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
                InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
                InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
                InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])
    if lang != "homepage":
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"next_{req}_{key}_{offset}")])

    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        total_results = len(files)
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass

@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=False,
            )
    except:
        pass
    _, key = query.data.split("#")
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    btn = []
    for i in range(0, len(QUALITIES)-1, 2):
        btn.append([
            InlineKeyboardButton(
                text=QUALITIES[i].title(),
                callback_data=f"fl#{QUALITIES[i].lower()}#{key}"
            ),
            InlineKeyboardButton(
                text=QUALITIES[i+1].title(),
                callback_data=f"fl#{QUALITIES[i+1].lower()}#{key}"
            ),
        ])

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="⇊ ꜱᴇʟᴇᴄᴛ ʏᴏᴜʀ ǫᴜᴀʟɪᴛʏ ⇊", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fl#homepage#{key}")])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_qualities_cb_handler(client: Client, query: CallbackQuery):
    _, qual, key = query.data.split("#")
    search = FRESH.get(key)
    try:
        search = search.replace(' ', '_')
    except:
        pass
    baal = qual in search
    if baal:
        search = search.replace(qual, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(req) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=False,
            )
    except:
        pass
    searchagain = search
    if lang != "homepage":
        search = f"{search} {qual}"
    BUTTONS[key] = search

    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    # files = [file for file in files if re.search(lang, file["file_name"], re.IGNORECASE)]
    if not files:
        await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
            InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
            InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
            InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
            InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])
    else:
        btn = []
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
            InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
            InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
            InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
            InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])

    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⇛",callback_data=f"next_{req}_{key}_{offset}")]
                )

            else:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⇛",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⇛",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="😶 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ 😶",callback_data="pages")]
        )
    if lang != "homepage":
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"next_{req}_{key}_{offset}")])

    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        total_results = len(files)
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass

@Client.on_callback_query(filters.regex(r"^pages"))
async def pages_cb_handler(client: Client, query: CallbackQuery):
    await query.answer()

@Client.on_callback_query(filters.regex(r"^manage_ignore"))
async def manage_ignore_words(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")

    # Check if the user is an admin
    user_id = query.from_user.id if query.from_user else None
    chat_id = query.message.chat.id

    try:
        member = await client.get_chat_member(chat_id, user_id)
        is_admin = member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] or user_id in ADMINS
    except Exception:
        is_admin = False

    if not is_admin:
        await query.answer("You don't have permission to access this feature.", show_alert=True)
        return

    ignore_words = await db.get_ignore_words(chat_id)

    if not ignore_words:
        message_text = "No ignore words found for this chat."
        buttons = [[InlineKeyboardButton("Add Ignore Word", callback_data=f"add_ignore_word_prompt#{key}")]]
    else:
        message_text = "Here are your ignore words:\n\n"
        for i, word in enumerate(ignore_words):
            message_text += f"{i+1}. `{word}`\n"
        buttons = [
            [InlineKeyboardButton("Add Ignore Word", callback_data=f"add_ignore_word_prompt#{key}")],
            [InlineKeyboardButton("Remove Ignore Word", callback_data=f"remove_ignore_word_prompt#{key}")]
        ]

    buttons.append([InlineKeyboardButton("Back", callback_data=f"back_to_settings#{key}")]) # Assuming a callback for back to settings

    await query.message.edit_text(
        text=message_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )
    await query.answer()

@Client.on_callback_query(filters.regex(r"^add_ignore_word_prompt"))
async def add_ignore_word_prompt(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")
    await query.message.edit_text(
        text="Enter the word you want to add to ignore list:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data=f"manage_ignore#{key}")]]),
        parse_mode=enums.ParseMode.MARKDOWN
    )
    temp.temp_data[query.message.chat.id] = {"action": "add_ignore_word", "key": key} # Store action and key for next message

@Client.on_callback_query(filters.regex(r"^remove_ignore_word_prompt"))
async def remove_ignore_word_prompt(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")
    ignore_words = await db.get_ignore_words(query.message.chat.id)

    if not ignore_words:
        await query.answer("No ignore words to remove.", show_alert=True)
        return

    message_text = "Enter the word you want to remove from ignore list:\n\n"
    for i, word in enumerate(ignore_words):
        message_text += f"{i+1}. `{word}`\n"

    await query.message.edit_text(
        text=message_text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data=f"manage_ignore#{key}")]]),
        parse_mode=enums.ParseMode.MARKDOWN
    )
    temp.temp_data[query.message.chat.id] = {"action": "remove_ignore_word", "key": key} # Store action and key for next message

@Client.on_message(filters.private & filters.text)
async def handle_temp_data(client: Client, message: Message):
    if message.chat.id in temp.temp_data:
        data = temp.temp_data[message.chat.id]
        action = data.get("action")
        key = data.get("key")

        if action == "add_ignore_word":
            word = message.text.strip()
            if word:
                await db.add_ignore_word(message.chat.id, word)
                await message.reply_text(f"'{word}' added to ignore list.")
            else:
                await message.reply_text("Invalid input. Please provide a word.")

            # Clean up temp data and go back to manage ignore words
            del temp.temp_data[message.chat.id]
            ignore_words = await db.get_ignore_words(message.chat.id)
            message_text = "Ignore words management:\n\n"
            if not ignore_words:
                message_text = "No ignore words found for this chat."
            else:
                for i, word in enumerate(ignore_words):
                    message_text += f"{i+1}. `{word}`\n"

            buttons = [
                [InlineKeyboardButton("Add Ignore Word", callback_data=f"add_ignore_word_prompt#{key}")],
                [InlineKeyboardButton("Remove Ignore Word", callback_data=f"remove_ignore_word_prompt#{key}")]
            ]
            buttons.append([InlineKeyboardButton("Back", callback_data=f"back_to_settings#{key}")])
            await message.reply_text(
                text=message_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN
            )

        elif action == "remove_ignore_word":
            word_to_remove = message.text.strip()
            if word_to_remove:
                removed = await db.remove_ignore_word(message.chat.id, word_to_remove)
                if removed:
                    await message.reply_text(f"'{word_to_remove}' removed from ignore list.")
                else:
                    await message.reply_text(f"'{word_to_remove}' not found in ignore list.")
            else:
                await message.reply_text("Invalid input. Please provide a word.")

            # Clean up temp data and go back to manage ignore words
            del temp.temp_data[message.chat.id]
            ignore_words = await db.get_ignore_words(message.chat.id)
            message_text = "Ignore words management:\n\n"
            if not ignore_words:
                message_text = "No ignore words found for this chat."
            else:
                for i, word in enumerate(ignore_words):
                    message_text += f"{i+1}. `{word}`\n"

            buttons = [
                [InlineKeyboardButton("Add Ignore Word", callback_data=f"add_ignore_word_prompt#{key}")],
                [InlineKeyboardButton("Remove Ignore Word", callback_data=f"remove_ignore_word_prompt#{key}")]
            ]
            buttons.append([InlineKeyboardButton("Back", callback_data=f"back_to_settings#{key}")])
            await message.reply_text(
                text=message_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN
            )

@Client.on_callback_query(filters.regex(r"^back_to_settings"))
async def back_to_settings(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")

    # Re-display the manage ignore words menu
    ignore_words = await db.get_ignore_words(query.message.chat.id)

    if not ignore_words:
        message_text = "No ignore words found for this chat."
    else:
        message_text = "Here are your ignore words:\n\n"
        for i, word in enumerate(ignore_words):
            message_text += f"{i+1}. `{word}`\n"

    buttons = [
        [InlineKeyboardButton("Add Ignore Word", callback_data=f"add_ignore_word_prompt#{key}")],
        [InlineKeyboardButton("Remove Ignore Word", callback_data=f"remove_ignore_word_prompt#{key}")]
    ]
    buttons.append([InlineKeyboardButton("Back", callback_data=f"back_to_settings#{key}")])

    await query.message.edit_text(
        text=message_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )
    await query.answer()

@Client.on_callback_query(filters.regex(r"^del"))
async def delete_file(client: Client, query: CallbackQuery):
    ident, file_id = query.data.split("#")
    files_ = await get_file_details(file_id)
    if not files_:
        return await query.answer('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
    files = files_
    title = files['file_name']
    size = get_size(files['file_size'])
    f_caption = files['caption']
    settings = await get_settings(query.message.chat.id)
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                   file_size='' if size is None else size,
                                                   file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
        f_caption = f_caption
    if f_caption is None:
        f_caption = f"{files['file_name']}"
    await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")

@Client.on_callback_query(filters.regex(r"^checksub"))
async def check_subscription(client: Client, query: CallbackQuery):
    if AUTH_CHANNEL and not await is_subscribed(client, query):
        await query.answer("Jᴏɪɴ ᴏᴜʀ Bᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ ᴍᴀʜɴ! 😒", show_alert=True)
        return
    ident, kk, file_id = query.data.split("#")
    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={kk}_{file_id}")

@Client.on_callback_query(filters.regex(r"^pages"))
async def pages_callback(client: Client, query: CallbackQuery):
    await query.answer()

@Client.on_callback_query(filters.regex(r"^send_fsall"))
async def send_all_files_callback(client: Client, query: CallbackQuery):
    temp_var, ident, key, offset = query.data.split("#")
    search = BUTTON0.get(key)
   # if not search:
    #    await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
    #    return
    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
    await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
    search = BUTTONS1.get(key)
    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
    await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
    search = BUTTONS2.get(key)
    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
    await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
    await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^send_fall"))
async def send_all_files_callback_fallback(client: Client, query: CallbackQuery):
    temp_var, ident, key, offset = query.data.split("#")
    search = FRESH.get(key)
 #   if not search:
   #     await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
   #     return
    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
    await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
    await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^killfilesdq"))
async def kill_files_dq_callback(client: Client, query: CallbackQuery):
    ident, keyword = query.data.split("#")
    #await query.message.edit_text(f"<b>Fetching Files for your query {keyword} on DB... Please wait...</b>")
    files, total = await get_bad_files(keyword)
    await query.message.edit_text("<b>File deletion process will start in 5 seconds !</b>")
    await asyncio.sleep(5)
    deleted = 0
    async with lock:
        try:
            for file in files:
                file_ids = file["file_id"]
                file_name = file["file_name"]
                result = col.delete_one({
                    'file_id': file_ids,
                })
                if not result.deleted_count:
                    result = sec_col.delete_one({
                        'file_id': file_ids,
                    })
                if result.deleted_count:
                    logger.info(f'File Found for your query {keyword}! Successfully deleted {file_name} from database.')
                deleted += 1
                if deleted % 50 == 0:
                    await query.message.edit_text(f"<b>Process started for deleting files from DB. Successfully deleted {str(deleted)} files from DB for your query {keyword} !\n\nPlease wait...</b>")
        except Exception as e:
            logger.exception(e)
            await query.message.edit_text(f'Error: {e}')
        else:
            await query.message.edit_text(f"<b>Process Completed for file deletion !\n\nSuccessfully deleted {str(deleted)} files from database for your query {keyword}.</b>")

@Client.on_callback_query(filters.regex(r"^opnsetgrp"))
async def open_settings_group_callback(client: Client, query: CallbackQuery):
    ident, grp_id = query.data.split("#")
    userid = query.from_user.id if query.from_user else None
    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        await query.answer("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True)
        return
    title = query.message.chat.title
    settings = await get_settings(grp_id)
    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton('Rᴇsᴜʟᴛ Pᴀɢᴇ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                InlineKeyboardButton('Bᴜᴛᴛᴏɴ' if settings["button"] else 'Tᴇxᴛ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                     callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                     callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                     callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                InlineKeyboardButton('5 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                     callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Aᴜᴛᴏ-FɪʟᴛᴇR',
                                     callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                     callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                     callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                     callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('SʜᴏʀᴛLɪɴᴋ',
                                     callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                                     callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Iɢɴᴏʀᴇ Wᴏʀᴅs',
                                     callback_data=f'manage_ignore#{grp_id}'),
                InlineKeyboardButton('Mᴀɴᴀɢᴇ',
                                     callback_data=f'manage_ignore#{grp_id}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
        await query.message.edit_reply_markup(reply_markup)

@Client.on_callback_query(filters.regex(r"^opnsetpm"))
async def open_settings_pm_callback(client: Client, query: CallbackQuery):
    ident, grp_id = query.data.split("#")
    userid = query.from_user.id if query.from_user else None
    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        await query.answer("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True)
        return
    title = query.message.chat.title
    settings = await get_settings(grp_id)
    btn2 = [[
             InlineKeyboardButton("Cʜᴇᴄᴋ PM", url=f"telegram.me/{temp.U_NAME}")
           ]]
    reply_markup = InlineKeyboardMarkup(btn2)
    await query.message.edit_text(f"<b>Yᴏᴜʀ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ ғᴏʀ {title} ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ʏᴏᴜʀ PM</b>")
    await query.message.edit_reply_markup(reply_markup)
    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton('Rᴇsᴜʟᴛ Pᴀɢᴇ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                InlineKeyboardButton('Bᴜᴛᴛᴏɴ' if settings["button"] else 'Tᴇxᴛ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                     callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                     callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                     callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                InlineKeyboardButton('5 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                     callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Aᴜᴛᴏ-FɪʟᴛᴇR',
                                     callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                     callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                     callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                     callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('SʜᴏʀᴛLɪɴᴋ',
                                     callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                                     callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            chat_id=userid,
            text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=query.message.id
        )

@Client.on_callback_query(filters.regex(r"^show_option"))
async def show_option_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    btn = [[
            InlineKeyboardButton("Uɴᴀᴠᴀɪʟᴀʙʟᴇ", callback_data=f"unalert#{from_user}"),
            InlineKeyboardButton("Uᴘʟᴏᴀᴅᴇᴅ", callback_data=f"upalert#{from_user}")
          ],[
            InlineKeyboardButton("Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ", callback_data=f"alalert#{from_user}")
          ]]
    btn2 = [[
             InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
           ]]
    if query.from_user.id in ADMINS:
        user = await client.get_users(from_user)
        reply_markup = InlineKeyboardMarkup(btn)
        await query.message.edit_reply_markup(reply_markup)
        await query.answer("Hᴇʀᴇ ᴀʀᴇ ᴛʜᴇ ᴏᴘᴛɪᴏɴs !")
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^unavailable"))
async def unavailable_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    btn = [[
            InlineKeyboardButton("⚠️ Uɴᴀᴠᴀɪʟᴀʙʟᴇ ⚠️", callback_data=f"unalert#{from_user}")
          ]]
    btn2 = [[
             InlineKeyboardButton('Jᴏɪɴ CʜᴀɴɴᴇL', url=link.invite_link),
             InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
           ],[
             InlineKeyboardButton("Rᴇᴏ̨ᴜᴇsᴛ Gʀᴏᴜᴘ Lɪɴᴋ", url="https://t.me/vj_bots")
           ]]
    if query.from_user.id in ADMINS:
        user = await client.get_users(from_user)
        reply_markup = InlineKeyboardMarkup(btn)
        content = query.message.text
        await query.message.edit_text(f"<b><strike>{content}</strike></b>")
        await query.message.edit_reply_markup(reply_markup)
        await query.answer("Sᴇᴛ ᴛᴏ Uɴᴀᴠᴀɪʟᴀʙʟᴇ !")
        try:
            await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        except UserIsBlocked:
            await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^uploaded"))
async def uploaded_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    btn = [[
            InlineKeyboardButton("✅ Uᴘʟᴏᴀᴅᴇᴅ ✅", callback_data=f"upalert#{from_user}")
          ]]
    btn2 = [[
             InlineKeyboardButton('Jᴏɪɴ CʜᴀɴɴᴇL', url=link.invite_link),
             InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
           ],[
             InlineKeyboardButton("Rᴇᴏ̨ᴜᴇsᴛ Gʀᴏᴜᴘ Lɪɴᴋ", url="https://t.me/vj_bots")
           ]]
    if query.from_user.id in ADMINS:
        user = await client.get_users(from_user)
        reply_markup = InlineKeyboardMarkup(btn)
        content = query.message.text
        await query.message.edit_text(f"<b><strike>{content}</strike></b>")
        await query.message.edit_reply_markup(reply_markup)
        await query.answer("Sᴇᴛ ᴛᴏ Uᴘʟᴏᴀᴅᴇᴅ !")
        try:
            await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        except UserIsBlocked:
            await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^already_available"))
async def already_available_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    btn = [[
        InlineKeyboardButton("🟢 Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ 🟢", callback_data=f"alalert#{from_user}")
    ]]
    btn2 = [[
        InlineKeyboardButton('Jᴏɪɴ CʜᴀɴɴᴇL', url=link.invite_link),
        InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
    ],[
        InlineKeyboardButton("Rᴇᴏ̨ᴜᴇsᴛ Gʀᴏᴜᴘ Lɪɴᴋ", url="https://t.me/vj_bots")
    ]]
    if query.from_user.id in ADMINS:
        user = await client.get_users(from_user)
        reply_markup = InlineKeyboardMarkup(btn)
        content = query.message.text
        await query.message.edit_text(f"<b><strike>{content}</strike></b>")
        await query.message.edit_reply_markup(reply_markup)
        await query.answer("Sᴇᴛ ᴛᴏ Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !")
        try:
            await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        except UserIsBlocked:
            await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^alalert"))
async def alalert_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    if int(query.from_user.id) == int(from_user):
        user = await client.get_users(from_user)
        await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇǫᴜᴇsᴛ ɪs Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !", show_alert=True)
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^upalert"))
async def upalert_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    if int(query.from_user.id) == int(from_user):
        user = await client.get_users(from_user)
        await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇǫᴜᴇsᴛ ɪs Uᴘʟᴏᴀᴅᴇᴅ !", show_alert=True)
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^unalert"))
async def unalert_callback(client: Client, query: CallbackQuery):
    ident, from_user = query.data.split("#")
    if int(query.from_user.id) == int(from_user):
        user = await client.get_users(from_user)
        await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇǫᴜᴇsᴛ ɪs Uɴᴀᴠᴀɪʟᴀʙʟᴇ !", show_alert=True)
    else:
        await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

@Client.on_callback_query(filters.regex(r"^generate_stream_link"))
async def generate_stream_link_callback(client: Client, query: CallbackQuery):
    _, file_id = query.data.split(":")
    try:
        log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=file_id)
        fileName = {quote_plus(get_name(log_msg))}
        stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        button = [[
            InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download),
            InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream)
        ],[
            InlineKeyboardButton('• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •', web_app=WebAppInfo(url=stream))
        ]]
        await query.message.edit_reply_markup(InlineKeyboardMarkup(button))
    except Exception as e:
        print(e)
        await query.answer(f"something went wrong\n\n{e}", show_alert=True)
        return

@Client.on_callback_query(filters.regex(r"^reqinfo"))
async def reqinfo_callback(client: Client, query: CallbackQuery):
    await query.answer(text=script.REQINFO, show_alert=True)

@Client.on_callback_query(filters.regex(r"^select"))
async def select_callback(client: Client, query: CallbackQuery):
    await query.answer(text=script.SELECT, show_alert=True)

@Client.on_callback_query(filters.regex(r"^sinfo"))
async def sinfo_callback(client: Client, query: CallbackQuery):
    await query.answer(text=script.SINFO, show_alert=True)

@Client.on_callback_query(filters.regex(r"^start"))
async def start_callback(client: Client, query: CallbackQuery):
    if PREMIUM_AND_REFERAL_MODE == True:
        buttons = [[
            InlineKeyboardButton('⤬ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ],[
            InlineKeyboardButton('ᴇᴀʀɴ ᴍᴏɴᴇʏ', callback_data="shortlink_info"),
            InlineKeyboardButton('ᴍᴏᴠɪᴇ ɢʀᴏᴜᴘ', url=GRP_LNK)
        ],[
            InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about')
        ],[
            InlineKeyboardButton('ᴘʀᴇᴍɪᴜᴍ ᴀɴᴅ ʀᴇғᴇʀʀᴀʟ', callback_data='subscription')
        ],[
            InlineKeyboardButton('ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url=CHNL_LNK)
        ]]
    else:
        buttons = [[
            InlineKeyboardButton('⤬ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ],[
            InlineKeyboardButton('ᴇᴀʀɴ ᴍᴏɴᴇʏ', callback_data="shortlink_info"),
            InlineKeyboardButton('ᴍᴏᴠɪᴇ ɢʀᴏᴜᴘ', url=GRP_LNK)
        ],[
            InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about')
        ],[
            InlineKeyboardButton('ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url=CHNL_LNK)
        ]]
    if CLONE_MODE == True:
        buttons.append([InlineKeyboardButton('ᴄʀᴇᴀᴛᴇ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', callback_data='clone')])
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    await query.message.edit_text(
        text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )
    await query.answer(MSG_ALRT)

@Client.on_callback_query(filters.regex(r"^clone"))
async def clone_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='start')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.CLONE_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^filters"))
async def filters_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('Mᴀɴᴜᴀʟ FIʟᴛᴇR', callback_data='manuelfilter'),
        InlineKeyboardButton('Aᴜᴛᴏ FIʟᴛᴇR', callback_data='autofilter')
    ],[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help'),
        InlineKeyboardButton('Gʟᴏʙᴀʟ FɪʟᴛᴇRs', callback_data='global_filters')
    ]]

    reply_markup = InlineKeyboardMarkup(buttons)
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    await query.message.edit_text(
        text=script.ALL_FILTERS.format(query.from_user.mention),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^global_filters"))
async def global_filters_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='filters')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.GFILTER_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^help"))
async def help_callback(client: Client, query: CallbackQuery):
    buttons = [[
         InlineKeyboardButton('⚙️ ᴀᴅᴍɪɴ ᴏɴʟʏ 🔧', callback_data='admin'),
     ], [
         InlineKeyboardButton('ʀᴇɴᴀᴍᴇ', callback_data='r_txt'),
         InlineKeyboardButton('sᴛʀᴇᴀᴍ/ᴅᴏᴡɴʟᴏᴀᴅ', callback_data='s_txt')
     ], [
         InlineKeyboardButton('ꜰɪʟᴇ ꜱᴛᴏʀᴇ', callback_data='store_file'),
         InlineKeyboardButton('ᴛᴇʟᴇɢʀᴀᴘʜ', callback_data='tele')
     ], [
         InlineKeyboardButton('ᴄᴏɴɴᴇᴄᴛɪᴏɴꜱ', callback_data='coct'),
         InlineKeyboardButton('ꜰɪʟᴛᴇʀꜱ', callback_data='filters')
     ], [
         InlineKeyboardButton('ʏᴛ-ᴅʟ', callback_data='ytdl'),
         InlineKeyboardButton('ꜱʜᴀʀᴇ ᴛᴇxᴛ', callback_data='share')
     ], [
         InlineKeyboardButton('ꜱᴏɴɢ', callback_data='song'),
         InlineKeyboardButton('ᴇᴀʀɴ ᴍᴏɴᴇʏ', callback_data='shortlink_info')
     ], [
         InlineKeyboardButton('ꜱᴛɪᴄᴋᴇʀ-ɪᴅ', callback_data='sticker'),
         InlineKeyboardButton('ᴊ-ꜱᴏɴ', callback_data='json')
     ], [
         InlineKeyboardButton('🏠 𝙷𝙾𝙼𝙴 🏠', callback_data='start')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    await query.message.edit_text(
        text=script.HELP_TXT.format(query.from_user.mention),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^about"))
async def about_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
        InlineKeyboardButton('Sᴏᴜʀᴄᴇ Cᴏᴅᴇ', url="https://github.com/VJBots/VJ-FILTER-BOT")
    ],[
        InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
        InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close_data')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.ABOUT_TXT.format(temp.U_NAME, temp.B_NAME, OWNER_LNK),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^subscription"))
async def subscription_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='start')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.SUBSCRIPTION_TXT.format(REFERAL_PREMEIUM_TIME, temp.U_NAME, query.from_user.id, REFERAL_COUNT),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^manuelfilter"))
async def manuelfilter_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='filters'),
        InlineKeyboardButton('Bᴜᴛᴛᴏɴs', callback_data='button')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.MANUELFILTER_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^button"))
async def button_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='manuelfilter')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.BUTTON_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^autofilter"))
async def autofilter_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='filters')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.AUTOFILTER_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^coct"))
async def coct_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.CONNECTION_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^admin"))
async def admin_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help'),
        InlineKeyboardButton('ᴇxᴛʀᴀ', callback_data='extra')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.ADMIN_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^store_file"))
async def store_file_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.FILE_STORE_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^r_txt"))
async def r_txt_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.RENAME_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^s_txt"))
async def s_txt_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.STREAM_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^extra"))
async def extra_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='admin')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=script.EXTRAMOD_TXT.format(OWNER_LNK, CHNL_LNK),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^stats"))
async def stats_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help'),
        InlineKeyboardButton('⟲ Rᴇғʀᴇsʜ', callback_data='rfrsh')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    filesp = col.count_documents({})
    totalsec = sec_col.count_documents({})
    stats = vjdb.command('dbStats')
    used_dbSize = (stats['dataSize']/(1024*1024))+(stats['indexSize']/(1024*1024))
    free_dbSize = 512-used_dbSize
    stats2 = sec_db.command('dbStats')
    used_dbSize2 = (stats2['dataSize']/(1024*1024))+(stats2['indexSize']/(1024*1024))
    free_dbSize2 = 512-used_dbSize2
    stats3 = mydb.command('dbStats')
    used_dbSize3 = (stats3['dataSize']/(1024*1024))+(stats3['indexSize']/(1024*1024))
    free_dbSize3 = 512-used_dbSize3
    await query.message.edit_text(
        text=script.STATUS_TXT.format((int(filesp)+int(totalsec)), total_users, totl_chats, filesp, round(used_dbSize, 2), round(free_dbSize, 2), totalsec, round(used_dbSize2, 2), round(free_dbSize2, 2), round(used_dbSize3, 2), round(free_dbSize3, 2)),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^rfrsh"))
async def rfrsh_callback(client: Client, query: CallbackQuery):
    await query.answer("Fetching MongoDb DataBase")
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help'),
        InlineKeyboardButton('⟲ Rᴇғʀᴇsʜ', callback_data='rfrsh')
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    filesp = col.count_documents({})
    totalsec = sec_col.count_documents({})
    stats = vjdb.command('dbStats')
    used_dbSize = (stats['dataSize']/(1024*1024))+(stats['indexSize']/(1024*1024))
    free_dbSize = 512-used_dbSize
    stats2 = sec_db.command('dbStats')
    used_dbSize2 = (stats2['dataSize']/(1024*1024))+(stats2['indexSize']/(1024*1024))
    free_dbSize2 = 512-used_dbSize2
    stats3 = mydb.command('dbStats')
    used_dbSize3 = (stats3['dataSize']/(1024*1024))+(stats3['indexSize']/(1024*1024))
    free_dbSize3 = 512-used_dbSize3
    await query.message.edit_text(
        text=script.STATUS_TXT.format((int(filesp)+int(totalsec)), total_users, totl_chats, filesp, round(used_dbSize, 2), round(free_dbSize, 2), totalsec, round(used_dbSize2, 2), round(free_dbSize2, 2), round(used_dbSize3, 2), round(free_dbSize3, 2)),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^shortlink_info"))
async def shortlink_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("👇Select Your Language 👇", callback_data="laninfo")
    ],[
        InlineKeyboardButton("Tamil", callback_data="tamil_info"),
        InlineKeyboardButton("English", callback_data="english_info"),
        InlineKeyboardButton("Hindi", callback_data="hindi_info")
    ],[
        InlineKeyboardButton("Malayalam", callback_data="malayalam_info"),
        InlineKeyboardButton("Urdu", callback_data="urdu_info"),
        InlineKeyboardButton("Bangla", callback_data="bangladesh_info")
    ],[
        InlineKeyboardButton("Telugu", callback_data="telugu_info"),
        InlineKeyboardButton("Kannada", callback_data="kannada_info"),
        InlineKeyboardButton("Gujarati", callback_data="gujarati_info")
    ],[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.SHORTLINK_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^tele"))
async def tele_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="help"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.TELE_TXT),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^ytdl"))
async def ytdl_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text="● ◌ ◌"
    )
    await query.message.edit_text(
        text="● ● ◌"
    )
    await query.message.edit_text(
        text="● ● ●"
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    await query.message.edit_text(
        text=script.YTDL_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^share"))
async def share_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="help"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.SHARE_TXT),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^song"))
async def song_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="help"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.SONG_TXT),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^json"))
async def json_callback(client: Client, query: CallbackQuery):
    buttons = [[
        InlineKeyboardButton('⟡ Bᴀᴄᴋ', callback_data='help')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text="● ◌ ◌"
    )
    await query.message.edit_text(
        text="● ● ◌"
    )
    await query.message.edit_text(
        text="● ● ●"
    )
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    await query.message.edit_text(
        text=script.JSON_TXT,
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^sticker"))
async def sticker_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="help"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.STICKER_TXT),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^tamil_info"))
async def tamil_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.TAMIL_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^english_info"))
async def english_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.ENGLISH_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^hindi_info"))
async def hindi_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.HINDI_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^telugu_info"))
async def telugu_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.TELUGU_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^malayalam_info"))
async def malayalam_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.MALAYALAM_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^urdu_info"))
async def urdu_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.URDU_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^bangladesh_info"))
async def bangladesh_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.BANGLADESH_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^kannada_info"))
async def kannada_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.KANNADA_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^gujarati_info"))
async def gujarati_info_callback(client: Client, query: CallbackQuery):
    btn = [[
        InlineKeyboardButton("⟡ Bᴀᴄᴋ", callback_data="start"),
        InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/KingVj01")
    ]]
    await client.edit_message_media(
        query.message.chat.id,
        query.message.id,
        InputMediaPhoto(random.choice(PICS))
    )
    reply_markup = InlineKeyboardMarkup(btn)
    await query.message.edit_text(
        text=(script.GUJARATI_INFO),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^setgs"))
async def setgs_callback(client: Client, query: CallbackQuery):
    ident, set_type, status, grp_id = query.data.split("#")
    grpid = await active_connection(str(query.from_user.id))

    if str(grp_id) != str(grpid):
        await query.message.edit("Yᴏᴜʀ Aᴄᴛɪᴠᴇ Cᴏɴɴᴇᴄᴛɪᴏɴ Hᴀs Bᴇᴇɴ Cʜᴀɴɢᴇᴅ. Gᴏ Tᴏ /connections ᴀɴᴅ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴ.")
        return await query.answer(MSG_ALRT)

    if status == "True":
        await save_group_settings(grpid, set_type, False)
    else:
        settings = await get_settings(grpid)
        if set_type == "is_shortlink" and not settings['shortlink']:
            return await query.answer(text = "First Add Your Shortlink Url And Api By /shortlink Command, Then Turn Me On.", show_alert = True)
        await save_group_settings(grpid, set_type, True)

    settings = await get_settings(grpid)

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton('Rᴇsᴜʟᴛ Pᴀɢᴇ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                InlineKeyboardButton('Bᴜᴛᴛᴏɴ' if settings["button"] else 'Tᴇxᴛ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                     callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                     callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                     callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                InlineKeyboardButton('5 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                     callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Aᴜᴛᴏ-FɪʟᴛᴇR',
                                     callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                     callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                     callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                     callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('SʜᴏʀᴛLɪɴᴋ',
                                     callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                                     callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_reply_markup(reply_markup)
    await query.answer(MSG_ALRT)

async def auto_filter(client, name, msg, reply_msg, ai_search, spoll=False):
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if not spoll:
        message = msg
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
            search = name
            search = search.lower()
            find = search.split(" ")
            search = ""
            removes = ["in","upload", "series", "full", "horror", "thriller", "mystery", "print", "file"]
            for x in find:
                if x in removes:
                    continue
                else:
                    search = search + x + " "
            search = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|bro|bruh|broh|helo|that|find|dubbed|link|venum|iruka|pannunga|pannungga|anuppunga|anupunga|anuppungga|anupungga|film|undo|kitti|kitty|tharu|kittumo|kittum|movie|any(one)|with\ssubtitle(s)?)", "", search, flags=re.IGNORECASE)
            search = re.sub(r"\s+", " ", search).strip()
            search = search.replace("-", " ")
            search = search.replace(":", "")
            search = search.replace(".", "")
            files, offset, total_results = await get_search_results(message.chat.id ,search, offset=0, filter=True)
            settings = await get_settings(message.chat.id)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(client, name, msg, reply_msg, ai_search)
                else:
                    return await reply_msg.edit_text(f"**⚠️ No File Found For Your Query - {name}**\n**Make Sure Spelling Is Correct.**")
        else:
            return
    else:
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
        settings = await get_settings(message.chat.id)
        await msg.message.delete()
    pre = 'filep' if settings['file_secure'] else 'file'
    key = f"{message.chat.id}-{message.id}"
    req = message.from_user.id if message.from_user else 0
    FRESH[key] = search
    temp.GETALL[key] = files
    temp.SHORT[message.from_user.id] = message.chat.id
    if settings["button"]:
        btn = []
        for file in files:
            # Clean the filename first
            clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))

            # Apply ignore words filter
            filtered_name = await filter_filename_with_ignore_words(clean_name)

            btn.append([
                InlineKeyboardButton(
                    text=f"[{get_size(file['file_size'])}] {filtered_name}", 
                    callback_data=f'{pre}#{file["file_id"]}'
                )
            ])
    else:
        btn = []
        btn.insert(0,
            [
                InlineKeyboardButton('adult ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+hLQh-FvQcL0xNWZl"),
            InlineKeyboardButton('all ott ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+kG8NP8YLiuk0YTE1"),
            InlineKeyboardButton('kannada ᴄʜᴀɴɴᴇʟ', url=f"https://t.me/+y9fMTjC6TLJhM1"),
            InlineKeyboardButton('online stream movies', url=f"https://t.me/+IK-TVp4mc8w3MTM1"),
            InlineKeyboardButton('free loots', url=f"https://t.me/JNKFREELOOTS")
        ])
    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
            else:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0])['file_name']) if settings["imdb"] else None
    cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
    remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
    TEMPLATE = script.IMDB_TEMPLATE_TXT
    if imdb:
        cap = TEMPLATE.format(
            qurey=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
        temp.IMDB_CAP[message.from_user.id] = cap
        if not settings["button"]:
            cap+="<b>\n\n<u>🍿 Your Movie Files 👇</u></b>\n"
            for file in files:
                cap += f"<b>\n📁 <a href='https://telegram.me/{temp.U_NAME}?start=files_{file['file_id']}'>[{get_size(file['file_size'])}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))}\n</a></b>"
    else:
        if settings["button"]:
            cap = f"<b>🎬 Movie Name :- {search}\n📨 Rᴇǫᴜᴇsᴛᴇᴅ Bʏ :- {message.from_user.mention}\n⏰ ʀᴇsᴜʟᴛ sʜᴏᴡ ɪɴ :- {remaining_seconds} sᴇᴄᴏɴᴅs\n\n</b>"
        else:
            cap = f"<b>🎬 Movie Name :- {search}\n📨 Rᴇǫᴜᴇsᴛᴇᴅ Bʏ :- {message.from_user.mention}\n⏰ ʀᴇsᴜʟᴛ sʜᴏᴡ ɪɴ :- {remaining_seconds} sᴇᴄᴏɴᴅs\n\n</b>"
            cap+="<b><u>🍿 Your Movie Files 👇</u></b>\n\n"
            for file in files:
                cap += f"<b>📁 <a href='https://telegram.me/{temp.U_NAME}?start=files_{file['file_id']}'>[{get_size(file['file_size'])}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@JNK_BACKUP') and not x.startswith('[@Filmy_Hub4u]') and not x.startswith('~') and not x.startswith('CineVood') and not x.startswith('skymovieshd') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))}\n\n</a></b>"

    if imdb and imdb.get('poster'):
        try:
            hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            await reply_msg.delete()
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await hehe.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await hehe.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaWebpageMedia):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            hmm = await message.reply_photo(photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            await reply_msg.delete()
            try:
               if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await hmm.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await hmm.delete()
        except Exception as e:
            logger.exception(e)
            fek = await reply_msg.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn))
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await fek.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await fek.delete()
    else:
        try:
            fuk = await reply_msg.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await fuk.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_delete']:
                    await asyncio.sleep(300)
                    await fuk.delete()
        except Exception as e:
            logger.exception(e)
            try:
                await reply_msg.delete()
            except:
                pass


async def advantage_spell_chok(client, name, msg, reply_msg, vj_search):
    mv_id = msg.id
    mv_rqst = name
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    settings = await get_settings(msg.chat.id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|bro|bruh|broh|helo|that|find|dubbed|link|venum|iruka|pannunga|pannungga|anuppunga|anupunga|anuppungga|anupungga|film|undo|kitti|kitty|tharu|kittumo|kittum|movie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception as e:
        logger.exception(e)
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await reply_msg.edit_text(text=script.I_CUDNT.format(mv_rqst), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist = []
    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await reply_msg.edit_text(text=script.I_CUDNT.format(mv_rqst), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist += [movie.get('title') for movie in movies]
    movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]
    SPELL_CHECK[mv_id] = movielist
    if AI_SPELL_CHECK == True and vj_search == True:
        vj_search_new = False
        vj_ai_msg = await reply_msg.edit_text("<b><i>I Am Trying To Find Your Movie With Your Wrong Spelling.</i></b>")
        movienamelist = []
        movienamelist += [movie.get('title') for movie in movies]
        for techvj in movienamelist:
            try:
                mv_rqst = mv_rqst.capitalize()
            except:
                pass
            if mv_rqst.startswith(techvj[0]):
                await auto_filter(client, techvj, msg, reply_msg, vj_search_new)
                break
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await reply_msg.edit_text(text=script.I_CUDNT.format(mv_rqst), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(30)
        await k.delete()
        return
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=movie_name.strip(),
                    callback_data=f"spol#{reqstr1}#{k}",
                )
            ]
            for k, movie_name in enumerate(movielist)
        ]
        btn.append([InlineKeyboardButton("Close", callback_data=f'spol#{reqstr1}#close_spellcheck')])
        spell_check_del = await reply_msg.edit_text(
            text=script.CUDNT_FND.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(btn)
        )
        try:
            if settings['auto_delete']:
                await asyncio.sleep(600)
                await spell_check_del.delete()
        except KeyError:
            grpid = await active_connection(str(msg.from_user.id))
            await save_group_settings(grpid, 'auto_delete', True)
            settings = await get_settings(msg.chat.id)
            if settings['auto_delete']:
                await asyncio.sleep(600)
                await spell_check_del.delete()

async def manual_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)

                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            protect_content=True if settings["file_secure"] else False,
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                ai_search = True
                                reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                await auto_filter(client, message.text, message, reply_msg, ai_search)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                ai_search = True
                                reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                await auto_filter(client, message.text, message, reply_msg, ai_search)
                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                ai_search = True
                                reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                await auto_filter(client, message.text, message, reply_msg, ai_search)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                ai_search = True
                                reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                await auto_filter(client, message.text, message, reply_msg, ai_search)

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

async def global_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        ai_search = True
                                        reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                        await auto_filter(client, message.text, message, reply_msg, ai_search)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        ai_search = True
                                        reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                        await auto_filter(client, message.text, message, reply_msg, ai_search)
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()

                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        ai_search = True
                                        reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                        await auto_filter(client, message.text, message, reply_msg, ai_search)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        ai_search = True
                                        reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                        await auto_filter(client, message.text, message, reply_msg, ai_search)
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()

                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    ai_search = True
                                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text} 🔍</i></b>")
                                    await auto_filter(client, message.text, message, reply_msg, ai_search)
                        else:
                            try:
                                if settings['auto_delete']:
                                    await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await joelkb.delete()


                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
