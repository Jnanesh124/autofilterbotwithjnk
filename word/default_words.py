
# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from database.ignore_words_db import add_ignore_word

DEFAULT_IGNORE_WORDS = [
    "in", "upload", "series", "full", "horror", "thriller", "mystery", "print", "file",
    "movie", "movies", "please", "send", "give", "download", "link", "new", "latest",
    "bro", "bruh", "hello", "hi", "hey", "thanks", "thank", "you", "dubbed", "hindi",
    "tamil", "telugu", "malayalam", "kannada", "english", "quality", "hd", "720p", 
    "1080p", "480p", "bluray", "webrip", "hdtv", "cam", "ts", "dvd", "web", "dl"
]

async def initialize_default_words():
    """Initialize default ignore words if not already present"""
    for word in DEFAULT_IGNORE_WORDS:
        await add_ignore_word(word)
    print("Default ignore words initialized!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(initialize_default_words())
