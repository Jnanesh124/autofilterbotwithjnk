
#!/usr/bin/env python3

import asyncio
from database.ignore_words_db import add_ignore_word

DEFAULT_WORDS = [
    "movie", "movies", "film", "films", "download", "free", "full", "hd", "quality",
    "watch", "online", "streaming", "series", "episode", "season", "latest", "new",
    "2024", "2023", "hindi", "english", "tamil", "telugu", "malayalam", "kannada",
    "dubbed", "subtitles", "subs", "web", "rip", "webrip", "bluray", "dvd", "cam",
    "ts", "tc", "scam", "print", "pre", "dvdscr", "r5", "brrip", "hdrip", "720p",
    "1080p", "480p", "360p", "4k", "uhd", "x264", "x265", "h264", "h265", "mkv",
    "mp4", "avi", "mov", "wmv", "flv", "3gp", "dual", "audio", "multi", "language"
]

async def main():
    print("Adding default ignore words...")
    for word in DEFAULT_WORDS:
        success = await add_ignore_word(word)
        if success:
            print(f"Added: {word}")
        else:
            print(f"Failed to add: {word}")
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
