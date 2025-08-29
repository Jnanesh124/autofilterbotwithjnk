
import pymongo
from info import OTHER_DB_URI, DATABASE_NAME
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(OTHER_DB_URI)
mydb = myclient[DATABASE_NAME]
ignore_col = mydb["ignore_words"]

async def add_ignore_word(word):
    """Add a word to ignore list"""
    try:
        ignore_col.update_one(
            {'word': word.lower()},
            {"$set": {'word': word.lower()}},
            upsert=True
        )
        return True
    except Exception as e:
        logger.exception('Error adding ignore word', exc_info=True)
        return False

async def remove_ignore_word(word):
    """Remove a word from ignore list"""
    try:
        result = ignore_col.delete_one({'word': word.lower()})
        return result.deleted_count > 0
    except Exception as e:
        logger.exception('Error removing ignore word', exc_info=True)
        return False

async def get_ignore_words():
    """Get all ignore words"""
    try:
        words = []
        for doc in ignore_col.find():
            words.append(doc['word'])
        return words
    except Exception as e:
        logger.exception('Error getting ignore words', exc_info=True)
        return []

async def is_ignored_word(word):
    """Check if a word should be ignored"""
    try:
        return ignore_col.find_one({'word': word.lower()}) is not None
    except Exception as e:
        logger.exception('Error checking ignore word', exc_info=True)
        return False
