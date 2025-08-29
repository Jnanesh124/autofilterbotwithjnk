
# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import io
from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.filtered_words_db import (
    add_filtered_word,
    remove_filtered_word,
    get_all_filtered_words,
    get_filtered_words_count,
    initialize_filtered_words
)
from info import ADMINS

@Client.on_message(filters.command(['addword']) & filters.private & filters.user(ADMINS))
async def add_word_filter(client, message):
    """Add a word to the filtered words list"""
    try:
        if len(message.command) < 2:
            await message.reply_text(
                "**Usage:** `/addword word_to_filter`\n\n"
                "**Example:** `/addword @spamchannel`\n"
                "**Example:** `/addword cinevood`\n"
                "**Example:** `/addword hq`",
                quote=True
            )
            return
        
        word = " ".join(message.command[1:]).strip()
        
        if not word:
            await message.reply_text("Please provide a valid word to filter.", quote=True)
            return
        
        success = await add_filtered_word(word)
        
        if success:
            await message.reply_text(
                f"✅ **Successfully added:** `{word}`\n\n"
                "This word will now be ignored in auto-filter searches.",
                quote=True
            )
        else:
            await message.reply_text(
                f"❌ **Failed to add:** `{word}`\n\n"
                "This word might already exist in the filter list.",
                quote=True
            )
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}", quote=True)

@Client.on_message(filters.command(['rmword', 'removeword']) & filters.private & filters.user(ADMINS))
async def remove_word_filter(client, message):
    """Remove a word from the filtered words list"""
    try:
        if len(message.command) < 2:
            await message.reply_text(
                "**Usage:** `/rmword word_to_remove`\n\n"
                "**Example:** `/rmword @spamchannel`\n"
                "**Example:** `/rmword cinevood`",
                quote=True
            )
            return
        
        word = " ".join(message.command[1:]).strip()
        
        if not word:
            await message.reply_text("Please provide a valid word to remove.", quote=True)
            return
        
        success = await remove_filtered_word(word)
        
        if success:
            await message.reply_text(
                f"✅ **Successfully removed:** `{word}`\n\n"
                "This word will no longer be filtered in auto-filter searches.",
                quote=True
            )
        else:
            await message.reply_text(
                f"❌ **Failed to remove:** `{word}`\n\n"
                "This word was not found in the filter list.",
                quote=True
            )
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}", quote=True)

@Client.on_message(filters.command(['listwords', 'filteredwords']) & filters.private & filters.user(ADMINS))
async def list_filtered_words(client, message):
    """List all filtered words"""
    try:
        words = await get_all_filtered_words()
        count = len(words)
        
        if count == 0:
            await message.reply_text(
                "📝 **No filtered words found.**\n\n"
                "Use `/addword <word>` to add words to the filter list.",
                quote=True
            )
            return
        
        # Create the word list
        word_list = f"📝 **Filtered Words List ({count} words):**\n\n"
        
        for i, word in enumerate(sorted(words), 1):
            word_list += f"{i}. `{word}`\n"
        
        word_list += f"\n💡 **Tip:** Use `/rmword <word>` to remove words from this list."
        
        # Check if message is too long
        if len(word_list) > 4096:
            # Create a text file if the list is too long
            with io.BytesIO(str.encode(word_list.replace("`", ""))) as word_file:
                word_file.name = "filtered_words.txt"
                await message.reply_document(
                    document=word_file,
                    caption=f"📝 **Filtered Words List ({count} words)**",
                    quote=True
                )
        else:
            await message.reply_text(word_list, quote=True)
            
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}", quote=True)

@Client.on_message(filters.command(['resetwords']) & filters.private & filters.user(ADMINS))
async def reset_filtered_words(client, message):
    """Reset filtered words to default list"""
    try:
        # Confirmation message
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes, Reset", callback_data="reset_words_confirm"),
                InlineKeyboardButton("❌ Cancel", callback_data="reset_words_cancel")
            ]
        ])
        
        await message.reply_text(
            "⚠️ **Warning!**\n\n"
            "This will remove all current filtered words and reset to the default list.\n\n"
            "Are you sure you want to continue?",
            reply_markup=buttons,
            quote=True
        )
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}", quote=True)

@Client.on_callback_query(filters.regex(r"^reset_words_"))
async def reset_words_callback(client, query):
    """Handle reset words confirmation"""
    try:
        if query.data == "reset_words_confirm":
            # Initialize default words (this will reset the collection)
            from database.filtered_words_db import filtered_words_col
            filtered_words_col.drop()  # Clear all existing words
            await initialize_filtered_words()  # Add default words
            
            await query.message.edit_text(
                "✅ **Successfully reset filtered words!**\n\n"
                "The default filtered words list has been restored.",
                reply_markup=None
            )
        else:
            await query.message.edit_text(
                "❌ **Reset cancelled.**\n\n"
                "No changes were made to the filtered words list.",
                reply_markup=None
            )
    except Exception as e:
        await query.message.edit_text(f"Error: {str(e)}", reply_markup=None)

# Initialize filtered words on startup
async def init_filtered_words():
    await initialize_filtered_words()
