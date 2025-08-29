
# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ignore_words_db import add_ignore_word, remove_ignore_word, get_ignore_words
from info import ADMINS
import io

@Client.on_message(filters.command('addword') & filters.incoming)
async def add_word_handler(client, message):
    if str(message.from_user.id) not in ADMINS:
        return await message.reply("Only admins can use this command!")
    
    try:
        cmd, word = message.text.split(" ", 1)
        word = word.strip().lower()
        
        if await add_ignore_word(word):
            await message.reply(f"✅ Word '{word}' added to ignore list!")
        else:
            await message.reply("❌ Failed to add word!")
    except ValueError:
        await message.reply("Usage: /addword <word>\nExample: /addword movie")

@Client.on_message(filters.command('removeword') & filters.incoming)
async def remove_word_handler(client, message):
    if str(message.from_user.id) not in ADMINS:
        return await message.reply("Only admins can use this command!")
    
    try:
        cmd, word = message.text.split(" ", 1)
        word = word.strip().lower()
        
        if await remove_ignore_word(word):
            await message.reply(f"✅ Word '{word}' removed from ignore list!")
        else:
            await message.reply("❌ Word not found in ignore list!")
    except ValueError:
        await message.reply("Usage: /removeword <word>\nExample: /removeword movie")

@Client.on_message(filters.command('listwords') & filters.incoming)
async def list_words_handler(client, message):
    if str(message.from_user.id) not in ADMINS:
        return await message.reply("Only admins can use this command!")
    
    words = await get_ignore_words()
    
    if not words:
        return await message.reply("No ignore words found!")
    
    word_list = "\n".join([f"• {word}" for word in words])
    
    if len(word_list) > 4000:
        with io.BytesIO(str.encode(word_list)) as word_file:
            word_file.name = "ignore_words.txt"
            await message.reply_document(
                document=word_file,
                caption="📝 All Ignore Words"
            )
    else:
        await message.reply(f"📝 **Ignore Words List:**\n\n{word_list}")
