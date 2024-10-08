# Credit - JISSHU BOTS
# Modified By NBBotz
# Some Codes Are Taken From A GitHub Repository And We Forgot His Name
# Base Code Bishal

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import CHANNELS, MOVIE_UPDATE_CHANNEL, ADMINS , LOG_CHANNEL
from database.ia_filterdb import save_file, unpack_new_file_id
from utils import get_poster, temp
import re
from database.users_chats_db import db

processed_movies = set()
media_filter = filters.document | filters.video

media_filter = filters.document | filters.video

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    bot_id = bot.me.id
    media = getattr(message, message.media.value, None)
    if media.mime_type in ['video/mp4', 'video/x-matroska']: 
        media.file_type = message.media.value
        media.caption = message.caption
        success_sts = await save_file(media)
        if success_sts == 'suc':
            latest_movie = await formatted_name(file_name=media.file_name, caption=media.caption)
            if latest_movie in recent_movies:
                return
            recent_movies.append(latest_movie)
            if await db.get_send_movie_update_status(bot_id):
                file_id, file_ref = unpack_new_file_id(media.file_id)
                await send_movie_updates(bot, file_name=media.file_name, caption=media.caption, file_id=file_id)


async def formatted_name(file_name, caption):
    year_match = re.search(r"\b(19|20)\d{2}\b", caption)
    year = year_match.group(0) if year_match else None      
    pattern = r"(?i)(?:s|season)0*(\d{1,2})"
    season = re.search(pattern, caption)
    if not season:
        season = re.search(pattern, file_name) 
    if year:
        file_name = file_name[:file_name.find(year) + 4]      
    if not year:
        if season:
            season = season.group(1) if season else None       
            file_name = file_name[:file_name.find(season) + 1]
    movie_name = await movie_name_format(file_name)    
    return movie_name


@Client.on_message(filters.command(["latest"]))
async def latest_movies(bot, message):
 try:
     last_movies = list(recent_movies)[-20:]
     message_text = "List of New Added Movies In DB:\n\n"
     for num, movie_name in enumerate(last_movies, start=1):
         message_text += f"{num}. {movie_name}\n"
     await message.reply_text(message_text)
 except Exception as e:
     print(f"Error showing latest movies: {e}")
     await bot.send_message(LOG_CHANNEL, f"Error showing latest movies: {e}")
