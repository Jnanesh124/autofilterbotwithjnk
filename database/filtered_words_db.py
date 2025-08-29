
# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import pymongo
from info import OTHER_DB_URI, DATABASE_NAME
from pyrogram import enums
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(OTHER_DB_URI)
mydb = myclient[DATABASE_NAME]
filtered_words_col = mydb["filtered_words"]

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
    """Initialize the database with default filtered words if empty"""
    try:
        count = await get_filtered_words_count()
        if count == 0:
            for word in DEFAULT_FILTERED_WORDS:
                await add_filtered_word(word.lower())
            logger.info(f"Initialized {len(DEFAULT_FILTERED_WORDS)} default filtered words")
    except Exception as e:
        logger.exception(f"Error initializing filtered words: {e}")

async def add_filtered_word(word):
    """Add a word to the filtered words list"""
    try:
        word = word.lower().strip()
        if not word:
            return False
        
        data = {'word': word}
        result = filtered_words_col.update_one({'word': word}, {"$set": data}, upsert=True)
        return True
    except Exception as e:
        logger.exception(f'Error adding filtered word: {e}')
        return False

async def remove_filtered_word(word):
    """Remove a word from the filtered words list"""
    try:
        word = word.lower().strip()
        result = filtered_words_col.delete_one({'word': word})
        return result.deleted_count > 0
    except Exception as e:
        logger.exception(f'Error removing filtered word: {e}')
        return False

async def get_all_filtered_words():
    """Get all filtered words"""
    try:
        words = []
        cursor = filtered_words_col.find({})
        for doc in cursor:
            words.append(doc['word'])
        return words
    except Exception as e:
        logger.exception(f'Error getting filtered words: {e}')
        return []

async def get_filtered_words_count():
    """Get count of filtered words"""
    try:
        return filtered_words_col.count_documents({})
    except Exception as e:
        logger.exception(f'Error counting filtered words: {e}')
        return 0

async def is_word_filtered(text):
    """Check if text contains any filtered words (case insensitive)"""
    try:
        if not text:
            return False
        
        text_lower = text.lower()
        filtered_words = await get_all_filtered_words()
        
        for word in filtered_words:
            if word in text_lower:
                return True
        return False
    except Exception as e:
        logger.exception(f'Error checking filtered word: {e}')
        return False

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
