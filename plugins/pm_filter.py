
# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import re
import ast
import math
import time
import random
import logging
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_bad_files
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from database.gfilters_mdb import find_gfilter

logger = logging.getLogger(__name__)

BUTTONS = {}
SPELL_CHECK = {}

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    k = await manual_filters(client, message)
    if k == False:
        await auto_filter(client, message)

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    reply_msg = message
    ai_search = False
    
    if content.startswith("/") or content.startswith("#"):
        return
    
    # Check for connection
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, user)
        await bot.send_message(
            LOG_CHANNEL,
            script.LOG_TEXT_P.format(user, user_id),
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    
    if len(message.text) > 1:
        buttons = []
        reply_text = f"<b>Hey {user}, I'm Here To Provide Movies\n\nJust Send Me The Movie Name 🎬\n\n📌 Example : <code>Avengers</code>\n\n✅ Fast result use - instead of space\n📌 Example : <code>KGF-2</code></b>"
        await message.reply_text(text=reply_text, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)
        return
    
    await auto_filter(bot, content, message, reply_msg, ai_search)

async def auto_filter(client, txt, message, reply_msg=None, ai_search=False):
    chat_id = message.chat.id
    message_id = message.id
    user_id = message.from_user.id
    duplicate_files = []
    
    if not reply_msg:
        reply_msg = message
    
    if chat_id == user_id and not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            script.LOG_TEXT_P.format(message.from_user.first_name, user_id),
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    
    search = txt.strip()
    search = re.sub(r'[^\w\s]', ' ', search)
    search = ' '.join(search.split())
    
    # File search
    files, offset, total_results = await get_search_results(search.lower(), max_results=MAX_B_TN)
    
    if not files:
        if ai_search:
            return await advantage_spell_chok(client, search, message, reply_msg, ai_search)
        else:
            return await advantage_spell_chok(client, search, message, reply_msg, ai_search)
    
    # Build file details
    btn = []
    for file in files:
        file_id = file.file_id
        filename = f"📁 {get_size(file.file_size)} ◽ {file.file_name}"
        btn.append([InlineKeyboardButton(text=filename, callback_data=f'files#{file_id}')])
    
    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🔰 Pages 1/{math.ceil(int(total_results) / int(MAX_B_TN))}", callback_data="pages"),
             InlineKeyboardButton(text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🔰 Pages 1/1", callback_data="pages")]
        )
    
    if len(files) > 1:
        btn.insert(0, [
            InlineKeyboardButton("📥 Send All Files", callback_data=f"sendfiles#{search}")
        ])
    
    imdb = await get_poster(search, file=(files[0]).file_name) if files else None
    SPELL_CHECK[reply_msg.id] = search
    del_msg = f"\n\n<b>⚠️ This message will be auto deleted after {AUTO_DELETE} minutes</b>" if AUTO_DELETE else ""
    
    template = script.ALRT_TXT.format(
        query=search,
        title="",
        votes="",
        aka="",
        seasons="",
        box="",
        localized="",
        kind="",
        imdb="",
        story="",
        genres="",
        exe="",
        size="",
        result=len(files),
        del_msg=del_msg
    )
    
    if imdb:
        template = script.IMDB_TEMPLATE_TXT.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box=imdb['box'],
            localized=imdb['localized_title'],
            kind=imdb['kind'],
            imdb=imdb['imdb_id'],
            story=imdb['story'],
            genres=imdb['genres'],
            exe=imdb['type'],
            size=f"{get_size(files[0].file_size)} {files[0].file_name}",
            result=len(files),
            del_msg=del_msg
        )
    
    try:
        if imdb and imdb.get('poster'):
            try:
                hehe = await reply_msg.reply_photo(photo=imdb.get('poster'), caption=template, reply_markup=InlineKeyboardMarkup(btn))
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                pic = imdb.get('poster')
                poster = pic.replace('.jpg', "._V1_UX360.jpg")
                hehe = await reply_msg.reply_photo(photo=poster, caption=template, reply_markup=InlineKeyboardMarkup(btn))
            except Exception as e:
                logger.exception(e)
                hehe = await reply_msg.reply_text(template, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        else:
            hehe = await reply_msg.reply_text(template, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
    except Exception as e:
        logger.exception(e)
        return
    
    try:
        if AUTO_DELETE:
            await asyncio.sleep(AUTO_DELETE*60)
            await hehe.delete()
            await reply_msg.delete()
    except:
        pass

async def advantage_spell_chok(client, name, msg, reply_msg, ai_search):
    mv_rqst = name
    files, offset, total_results = await get_search_results(mv_rqst, max_results=10)
    if files:
        return await auto_filter(client, mv_rqst, msg, reply_msg, ai_search)
    
    suggestions = [
        re.sub(r"[.\-;'\"!&]", " ", txt) for txt in [
            mv_rqst, mv_rqst.replace(" ", "+"), mv_rqst.replace("+", " ")
        ]
    ]
    
    for txt in suggestions:
        files, offset, total_results = await get_search_results(txt, max_results=10)
        if files:
            return await auto_filter(client, txt, msg, reply_msg, ai_search)
    
    try:
        button = []
        g_s = await search_gagala(mv_rqst)
        button.append([InlineKeyboardButton(text=f"💡 {mv_rqst} 💡", url=g_s)])
        
        k = await reply_msg.edit_text(text=script.I_CUDNT.format(mv_rqst), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(15)
        await k.delete()
    except Exception as e:
        logger.exception(e)

async def manual_filters(client, message, text=False):
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
                            await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button)
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

async def global_filters(client, message, text=False):
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
                            await client.send_message(group_id, reply_text, disable_web_page_preview=True,
                                                      reply_to_message_id=reply_id)
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button)
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

async def get_search_results(query, file_type=None, max_results=10, offset=0):
    """Search for files in database"""
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return [], 0, 0
    
    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}
    
    if file_type:
        filter['file_type'] = file_type

    total_results = await Media.count_documents(filter)
    
    cursor = Media.find(filter)
    cursor.sort('_id', -1)
    cursor.skip(int(offset)).limit(int(max_results))
    files = await cursor.to_list(length=int(max_results))
    
    next_offset = int(offset) + int(max_results)
    if next_offset > total_results:
        next_offset = ''

    return files, next_offset, total_results

async def get_poster(query, bulk=False, id=False, file=None):
    """Get movie poster from IMDB"""
    if not IMDB:
        return None
    try:
        if bulk:
            return await search_posters(query)
        else:
            return await search_poster(query, id, file)
    except Exception as e:
        logger.exception(e)
        return None

async def search_posters(query):
    """Search for multiple movie posters"""
    # Implementation for bulk poster search
    return None

async def search_poster(query, id=False, file=None):
    """Search for single movie poster"""
    # Implementation for single poster search  
    return None

async def search_gagala(text):
    """Create Google search URL"""
    find = text.replace(" ", "+")
    return f"https://www.google.com/search?q={find}"

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("⚠️ This Is Not For You!", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.",show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, max_results=MAX_B_TN)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    if settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"📁 {get_size(file.file_size)} ◽ {file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - MAX_B_TN
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"📄 Pages {math.ceil(int(offset) / int(MAX_B_TN)) + 1} / {math.ceil(total / int(MAX_B_TN))}", callback_data="pages")]
        )
    elif off_set is None:
        btn.append([InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / int(MAX_B_TN)) + 1} / {math.ceil(total / int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / int(MAX_B_TN)) + 1} / {math.ceil(total / int(MAX_B_TN))}", callback_data="pages"),
                InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup( 
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^files#"))
async def file_send(bot, query):
    file_id = query.data.split("#", 1)[1]
    files_ = await get_file_details(file_id)           
    if not files_:
        return await query.answer('No such file exist.')
    files = files_[0]
    title = files.file_name
    size = get_size(files.file_size)
    f_caption = files.caption
    
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
        f_caption = f"{files.file_name}"

    try:
        if AUTH_CHANNEL and not await is_subscribed(bot, query):
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
            return
        elif settings['botpm']:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
            return
        else:
            await bot.send_cached_media(
                chat_id=query.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=True if ident == "filep" else False
            )
            await query.answer('Check PM, I have sent files in pm', show_alert=True)
    except UserIsBlocked:
        await query.answer('Unblock the bot mahn !', show_alert=True)
    except PeerIdInvalid:
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
    except Exception as e:
        await query.answer('Some error occurred!!', show_alert=True)
        logger.exception(e)

@Client.on_callback_query(filters.regex(r"^sendfiles#"))
async def send_all_files(bot, query):
    ident, search = query.data.split("#", 1)
    settings = await get_settings(query.message.chat.id)
    
    files, offset, total_results = await get_search_results(search, max_results=10)
    if not files:
        await query.answer("No files found", show_alert=True)
        return
    
    if AUTH_CHANNEL and not await is_subscribed(bot, query):
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=all_{search}")
        return
    elif settings['botpm']:
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=all_{search}")
        return
    
    batch_ids = []
    for file in files:
        batch_ids.append(file.file_id)
    
    try:
        for file_id in batch_ids:
            files_ = await get_file_details(file_id)
            if not files_:
                continue
            files = files_[0]
            title = files.file_name
            size = get_size(files.file_size)
            f_caption = files.caption
            
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                           file_size='' if size is None else size,
                                                           file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption = f_caption
            if f_caption is None:
                f_caption = f"{files.file_name}"
            
            await bot.send_cached_media(
                chat_id=query.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=True
            )
            await asyncio.sleep(1)
        
        await query.answer(f'All files sent to your PM!', show_alert=True)
    except UserIsBlocked:
        await query.answer('Unblock the bot!', show_alert=True)
    except Exception as e:
        await query.answer('Some error occurred!', show_alert=True)
        logger.exception(e)

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer('Piracy Is Crime')
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer('Piracy Is Crime')

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer('Piracy Is Crime')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
            await query.answer('Piracy Is Crime')
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            await query.answer("Process Cancelled")
            await query.message.delete()
    elif query.data.startswith("groupcb"):
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    elif query.data.startswith("connectcb"):
        await query.answer()

        group_id = query.data.split(":")[1]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
    elif query.data.startswith("disconnect"):
        await query.answer()

        group_id = query.data.split(":")[1]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
    elif query.data.startswith("deletecb"):
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    elif query.data == "pages":
        await query.answer()
