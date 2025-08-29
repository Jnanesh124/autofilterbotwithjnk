# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import pymongo
from info import OTHER_DB_URI, DATABASE_NAME
from pyrogram import enums
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Initialize MongoDB client and database
# Use asyncio compatible driver if available, otherwise, it might cause issues
# This example assumes a synchronous client, but the functions are made async
# to handle potential async operations later or with an async driver.
# For true async with MongoDB, consider using 'motor'.
try:
    myclient = pymongo.MongoClient(OTHER_DB_URI)
    mydb = myclient[DATABASE_NAME]
    filtered_words_col = mydb["filtered_words"]
    logger.info("MongoDB client initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing MongoDB client: {e}")
    # Fallback or error handling for client initialization
    myclient = None
    mydb = None
    filtered_words_col = None

async def _ensure_db_initialized():
    """Ensures the database and collection are available."""
    if not myclient or not mydb or not filtered_words_col:
        raise ConnectionError("Database not initialized properly.")
    # In a real async scenario with 'motor', you might check connection status here.
    # For synchronous pymongo wrapped in async, this is more of a placeholder.
    pass


# Default filtered words - case insensitive patterns
DEFAULT_FILTERED_WORDS = [
    # Channel usernames
    "@jnk_backup", "@jnkbacluop_joibn", "@tech_vj", "@vj_botz",
    # Common website patterns
    "cinevood", "moviesflix", "filmywap", "tamilrockers", "isaimini",
    "moviesda", "kuttymovies", "tamilgun", "movierulz", "bollyflix",
    # Quality indicators
    "hq", "hd", "720p", "1080p", "480p", "360p", "bluray", "webrip",
    "dvdrip", "camrip", "hdts", "hdcam", "dvdscr",
    # Common link patterns
    "www.", "http", "https", ".com", ".in", ".net", ".org", ".co",
    "t.me", "telegram.me", "bit.ly", "short.link",
    # File format indicators
    "mkv", "mp4", "avi", "x264", "x265", "hevc",
    # Common spam words
    "join", "channel", "group", "link", "download", "free",
    "latest", "new", "update", "movie", "film", "series"
]

async def initialize_filtered_words():
    """Initialize the filtered words collection with default words if empty"""
    try:
        await _ensure_db_initialized()
        # Check if collection is empty
        count = await filtered_words_col.count_documents({})
        if count == 0:
            # Insert default words
            words_data = [{"word": word.lower()} for word in DEFAULT_FILTERED_WORDS]
            await filtered_words_col.insert_many(words_data)
            logger.info(f"Initialized filtered words collection with {len(DEFAULT_FILTERED_WORDS)} default words")
        else:
            logger.info(f"Filtered words collection already contains {count} words")
    except Exception as e:
        logger.error(f"Error initializing filtered words: {e}")

async def add_filtered_word(word: str) -> bool:
    """Add a word to the filtered words list"""
    try:
        await _ensure_db_initialized()
        word_lower = word.lower()
        # Check if word already exists
        if await filtered_words_col.find_one({"word": word_lower}):
            return False
        # Add the word
        await filtered_words_col.insert_one({"word": word_lower})
        logger.info(f"Added filtered word: {word_lower}")
        return True
    except Exception as e:
        logger.error(f"Error adding filtered word '{word}': {e}")
        return False

async def remove_filtered_word(word: str) -> bool:
    """Remove a word from the filtered words list"""
    try:
        await _ensure_db_initialized()
        word_lower = word.lower()
        result = await filtered_words_col.delete_one({"word": word_lower})
        if result.deleted_count > 0:
            logger.info(f"Removed filtered word: {word_lower}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error removing filtered word '{word}': {e}")
        return False

async def get_all_filtered_words() -> list:
    """Get all filtered words"""
    try:
        await _ensure_db_initialized()
        words = filtered_words_col.find({}, {"word": 1, "_id": 0})
        return [doc["word"] async for doc in words]
    except Exception as e:
        logger.error(f"Error getting filtered words: {e}")
        return []

async def reset_filtered_words():
    """Reset filtered words to default list"""
    try:
        await _ensure_db_initialized()
        # Clear existing words
        await filtered_words_col.delete_many({})
        # Insert default words
        words_data = [{"word": word.lower()} for word in DEFAULT_FILTERED_WORDS]
        await filtered_words_col.insert_many(words_data)
        logger.info(f"Reset filtered words to default ({len(DEFAULT_FILTERED_WORDS)} words)")
    except Exception as e:
        logger.error(f"Error resetting filtered words: {e}")

async def is_word_filtered(text: str) -> bool:
    """Check if text contains any filtered words"""
    try:
        if not text:
            return False

        text_lower = text.lower()
        filtered_words = await get_all_filtered_words()

        for word in filtered_words:
            if word in text_lower:
                logger.info(f"Filtered word detected: '{word}' in text: '{text[:50]}...'")
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking filtered words: {e}")
        return False

async def get_filtered_words_count():
    """Get count of filtered words"""
    try:
        await _ensure_db_initialized()
        return await filtered_words_col.count_documents({})
    except Exception as e:
        logger.error(f"Error counting filtered words: {e}")
        return 0

async def should_ignore_message(text):
    """Main function to check if a message should be ignored based on filtered words"""
    try:
        if not text or len(text.strip()) < 2:
            return True

        # Check if message contains filtered words
        if await is_word_filtered(text):
            return True

        # Additional checks for URLs and channel mentions
        text_lower = text.lower()

        # Check for URL patterns
        url_patterns = ['http://', 'https://', 'www.', '.com', '.in', '.net', '.org', '.co', 't.me/', 'telegram.me/']
        if any(pattern in text_lower for pattern in url_patterns):
            return True

        # Check for channel/group mentions
        if text_lower.startswith('@') or '[' in text_lower or ']' in text_lower:
            return True

        # Check for common spam indicators
        spam_indicators = ['join', 'link', 'channel', 'group', 'download', 'free', 'click']
        words_in_text = text_lower.split()
        spam_count = sum(1 for indicator in spam_indicators if any(indicator in word for word in words_in_text))

        if spam_count >= 2:  # If 2 or more spam indicators found
            return True

        return False
    except Exception as e:
        logger.exception(f'Error in should_ignore_message: {e}')
        return False