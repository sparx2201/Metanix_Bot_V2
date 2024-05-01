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

@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name  
    if file.file_size > 2000 * 1024 * 1024:
        return await message.reply_text("Sorry, this bot doesn't support uploading files bigger than 2GB")
    
    # Creating Directory for Metadata
    metadata_dir = "Metadata"
    if not os.path.isdir(metadata_dir):
        os.mkdir(metadata_dir)
        
    prefix = await db.get_prefix(message.chat.id)
    suffix = await db.get_suffix(message.chat.id)
    new_name = file.file_name 
    new_filename_ = new_name.split(":-")[1]
    remname_text = await db.get_remname(message.chat.id)  # Get the remname text from the user's database entry
    if remname_text and remname_text in new_filename_:
        new_filename_ = new_filename_.replace(remname_text, "")  # Remove the remname text from the new filename
        
    try:
        # adding prefix and suffix
        new_filename = add_prefix_suffix(new_filename_, prefix, suffix)
    except Exception as e:
        return await message.edit(f"⚠️ Something went wrong, can't set Prefix or Suffix \nError: {e}")

    file_path = f"downloads/{new_filename}"
    file = message

    ms = await message.edit("**Trying To Download....**")
    try:
        path = await client.download_media(message=file, file_name=file_path, progress=progress_for_pyrogram, progress_args=("**Download Started....**", ms, time.time()))
    except RPCError as e:
        return await ms.edit(f"Error downloading file: {e}")
    except Exception as e:
        return await ms.edit(f"Error: {e}")

    # Rename the file automatically
    os.rename(path, file_path)
    
    _bool_metadata = await db.get_metadata(message.chat.id)

    if _bool_metadata:
        metadata_path = f"{metadata_dir}/{new_filename}"
        metadata = await db.get_metadata_code(message.chat.id)
        if metadata:
            try:
                await ms.edit("Adding Metadata To File....")
                cmd = f"""ffmpeg -i "{path}" {metadata} "{metadata_path}" """
                process = await asyncio.create_subprocess_shell(
                    cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                er = stderr.decode()
                if er:
                    return await ms.edit(str(er) + "\n\n**Error**")
            except Exception as e:
                return await ms.edit(f"Error adding metadata: {e}")
        await ms.edit("**Metadata added to the file successfully ✅**\n\n**Trying to upload....**")
    else:
        await ms.edit("**Trying to upload....**")

    duration = 0
    try:
        parser = createParser(file_path)
        metadata = extractMetadata(parser)
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        parser.close()
    except Exception as e:
        return await ms.edit(f"Error getting duration: {e}")

    ph_path = None
    media = getattr(file, file.media.value)
    c_caption = await db.get_caption(message.chat.id)
    c_thumb = await db.get_thumbnail(message.chat.id)

    if c_caption:
        try:
            caption = c_caption.format(filename=new_filename, filesize=humanbytes(media.file_size), duration=convert(duration))
        except Exception as e:
            return await ms.edit(text=f"Your Caption Error Exception ●> ({e})")
    else:
        caption = f"**{new_filename}**"

    if media.thumbs or c_thumb:
        if c_thumb:
            ph_path = await client.download_media(c_thumb)
            width, height, ph_path = await fix_thumb(ph_path)
        else:
            try:
                ph_path_ = await take_screen_shot(file_path, os.path.dirname(os.path.abspath(file_path)), random.randint(0, duration - 1))
                width, height, ph_path = await fix_thumb(ph_path_)
            except Exception as e:
                ph_path = None
                print(e)

    upload_type = await db.get_upload_type(message.from_user.id)

    if media.file_size > 2000 * 1024 * 1024:
        try:
            if upload_type == "document":
                filw = await client.send_document(
                    Config.LOG_CHANNEL,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                   caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("**Upload Started....**", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await client.copy_message(message.from_user.id, from_chat, mg_id)
                await ms.delete()
                await client.delete_messages(from_chat, mg_id)

            elif upload_type == "video":
                filw = await client.send_video(
                    message.chat.id,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("**Upload Started....**", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await client.copy_message(message.from_user.id, from_chat, mg_id)
                await ms.delete()
                await client.delete_messages(from_chat, mg_id)
           

        except RPCError as e:
            return await ms.edit(f"Error uploading file: {e}")
        except Exception as e:
            return await ms.edit(f"Error: {e}")
    else:
        try:
            if upload_type == "document":
                await client.send_document(
                    message.chat.id,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("**Upload Started....**", ms, time.time()))
            elif upload_type == "video":
                await client.send_video(
                    message.chat.id,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("**Upload Started....**", ms, time.time()))
          
        except RPCError as e:
            return await ms.edit(f"Error uploading file: {e}")
        except Exception as e:
            return await ms.edit(f"Error: {e}")

    await ms.delete()

    if ph_path:
        os.remove(ph_path)
    if file_path:
        os.remove(file_path)
    if metadata_path:
        os.remove(metadata_path)
