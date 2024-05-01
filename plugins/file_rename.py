import random
import asyncio
import os
import time
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image

from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix
from helper.ffmpeg import fix_thumb, take_screen_shot
from helper.database import db
from config import Config

app = Client("test", api_id=Config.STRING_API_ID, api_hash=Config.STRING_API_HASH, session_string=Config.STRING_SESSION)


# Define the callback for the 'upload' buttons
from pyrogram import Client, filters
from helper.database import db  # Assuming db is your Database class instance
import os
import random
import asyncio
from pyrogram.errors import RPCError

#@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
#async def rename_start(client, message):
app = Client("my_bot")

# Define message handler for video files
@Client.on_message(filters.private & filters.video)
async def process_video(client, message):
    # Get the video file
    video_file = message.video

    # Download the video file
    file_path = await video_file.download()

    # Get the original filename
    original_filename = video_file.file_name

    # Rename the downloaded file using the original filename
    renamed_file_path = f"downloads/{original_filename}"
    os.rename(file_path, renamed_file_path)

    # Send the renamed file as a document
    await client.send_document(message.chat.id, document=renamed_file_path)

    # Cleanup: Remove the renamed file
    os.remove(renamed_file_path)
