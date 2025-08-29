# Overview

VJ Filter Bot is a comprehensive Telegram bot designed for automatic file filtering and distribution. The bot serves as a media file search engine that allows users to find and access movies, TV shows, and other content through an intelligent filtering system. It features a sophisticated clone system that enables users to create their own instances of the bot, along with premium subscription capabilities and referral programs.

The bot is built to handle large-scale file indexing from Telegram channels, provide intelligent search capabilities with AI spell-checking, and offer streaming functionality for media files. It includes comprehensive user management, force subscription mechanisms, and various utility features to enhance the user experience.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Built using Pyrogram, a modern Python framework for Telegram Bot API
- **Asynchronous Processing**: Utilizes asyncio for handling concurrent operations and improved performance
- **Plugin System**: Modular architecture with plugins organized in separate directories for maintainability
- **Multi-Client Support**: Implements multiple bot instances for load distribution and improved reliability

## Database Design
- **Primary Database**: MongoDB for file storage and indexing (FILE_DB_URI)
- **Secondary Database**: Fallback MongoDB instance for redundancy (SEC_FILE_DB_URI) 
- **User Database**: Separate MongoDB collection for user and chat management (USER_DB_URI)
- **Clone Database**: Dedicated storage for clone bot instances (CLONE_DATABASE_URI)
- **Multiple Database Strategy**: Automatic failover between primary and secondary databases

## File Management System
- **Automatic Indexing**: Monitors specified channels for new media files and indexes them automatically
- **Intelligent Search**: AI-powered search with spell-checking and suggestion capabilities
- **File Filtering**: Advanced filtering based on quality, language, season, episode, and year
- **Duplicate Detection**: Prevents duplicate file entries in the database

## Authentication & Authorization
- **Admin System**: Multi-level admin access with different permission levels
- **Force Subscribe**: Configurable force subscription to channels with request-to-join functionality
- **Premium System**: Time-based premium subscriptions with referral rewards
- **Token Verification**: Optional token-based verification system for enhanced security

## Bot Clone System
- **Dynamic Bot Creation**: Users can create their own bot instances using BotFather tokens
- **Isolated Databases**: Each clone maintains separate user databases while sharing the file index
- **Custom Configuration**: Clone bots can be independently configured with different settings
- **Resource Management**: Load balancing across multiple bot instances

## Content Delivery
- **Direct Streaming**: Built-in streaming server for video/audio content
- **File Serving**: Direct file download capabilities with resumable downloads
- **Web Interface**: HTML templates for browser-based file access and streaming
- **URL Shortening**: Integrated support for multiple URL shortener services

## Search & Filter Engine
- **Fuzzy Matching**: Intelligent search that handles typos and variations
- **Multi-Database Search**: Searches across primary and secondary databases
- **Pagination**: Efficient result pagination with inline keyboard navigation
- **Real-time Results**: Live search updates as users type

## User Interface Design
- **Inline Keyboards**: Rich interactive buttons for navigation and actions
- **Callback Handling**: Efficient callback query processing for button interactions
- **Auto-Delete Messages**: Configurable automatic message deletion in private chats
- **Multi-language Support**: Internationalization support for different user languages

# External Dependencies

## Core Telegram Integration
- **Pyrogram/Pyrofork**: Modern Telegram MTProto API framework for bot development
- **TGCrypto**: Cryptographic library for secure Telegram communications

## Database Services
- **MongoDB**: Primary document database for file storage and user management
- **Motor**: Asynchronous MongoDB driver for Python
- **PyMongo**: MongoDB driver with connection pooling

## AI & Content Processing
- **OpenAI**: AI-powered spell checking and content suggestions
- **IMDb Integration**: Movie metadata and poster fetching via Cinemagoer
- **Google Translate**: Text translation services for multi-language support

## Media Processing
- **yt-dlp/youtube-dl**: Video downloading and processing from various platforms
- **FFmpeg**: Video/audio transcoding and thumbnail generation
- **Pillow**: Image processing and manipulation
- **OpenCV**: Advanced image and video processing

## URL Services
- **Shortzy**: URL shortening service integration
- **PyShorteners**: Multiple URL shortener service support

## Web Framework
- **aiohttp**: Asynchronous HTTP client/server for streaming capabilities
- **Jinja2**: Template engine for web interface rendering
- **Bootstrap/Tailwind**: Frontend frameworks for responsive web design

## Utility Libraries
- **APScheduler**: Advanced Python scheduler for background tasks
- **BeautifulSoup**: HTML/XML parsing for web scraping
- **Requests**: HTTP library for API interactions
- **pytz**: Timezone handling for global user support
- **humanize**: Human-readable data formatting

## Development Tools
- **python-decouple**: Environment variable management
- **colorama**: Cross-platform colored terminal output
- **logging**: Comprehensive logging and error tracking

The architecture emphasizes scalability, reliability, and user experience while maintaining clean separation of concerns through its modular plugin system.