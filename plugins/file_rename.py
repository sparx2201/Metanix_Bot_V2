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

# Define a function to handle the 'rename' callback
#@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
#async def rename_start(client, message):
#    file = getattr(message, message.media.value)
#    filename = file.file_name  
#    if file.file_size > 2000 * 1024 * 1024:
#        return await message.reply_text("Sorry, this bot doesn't support uploading files bigger than 2GB")

#    try:
#        await message.reply_text(
#            text=f"**Please Enter New Filename**\n\n**Old File Name** :- `{filename}`",
#            reply_to_message_id=message.id,  
#            reply_markup=ForceReply(True)
#        )       
#        await asyncio.sleep(30)
#    except FloodWait as e:
#        await asyncio.sleep(e.value)
#        await message.reply_text(
#            text=f"**Please Enter New Filename**\n\n**Old File Name** :- `{filename}`",
#            reply_to_message_id=message.id,  
#            reply_markup=ForceReply(True)
#        )
#    except:
#        pass

# Define the main message handler for private messages with replies
#@Client.on_message(filters.private & filters.reply)
#async def refunc(client, message):
#   reply_message = message.reply_to_message
#    if (reply_message.reply_markup) and isinstance(reply_message.reply_markup, ForceReply):
#        new_name = message.text
#        remname_text = await db.get_remname(message.from_user.id)  # Get the remname text from the user's database entry
#        if remname_text and remname_text in new_name:
#            new_name = new_name.replace(remname_text, "")  # Remove the remname text from the new filename
#        await message.delete()
#        msg = await client.get_messages(message.chat.id, reply_message.id)
#        file = msg.reply_to_message
#        media = getattr(file, file.media.value)
#        if not "." in new_name:
#            if "." in media.file_name:
#                extn = media.file_name.rsplit('.', 1)[-1]
#            else:
#                extn = "mkv"
#            new_name = new_name + "." + extn
#        await reply_message.delete()
#
#        # Use a list to store the inline keyboard buttons
#        button = [
#            [InlineKeyboardButton("📁 Document", callback_data="upload_document")]
#        ]
#        if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
#            button.append([InlineKeyboardButton("🎥 Video", callback_data="upload_video")])
#        elif file.media == MessageMediaType.AUDIO:
#            button.append([InlineKeyboardButton("🎵 Audio", callback_data="upload_audio")])
#
#        # Use a single call to reply with both text and inline keyboard
#        await message.reply(
#            text=f"**Select The Output File Type**\n**• File Name :-**  `{new_name}`",
#            reply_to_message_id=file.id,
#            reply_markup=InlineKeyboardMarkup(button)
#       )

# Define the callback for the 'upload' buttons
from pyrogram import Client, filters
from helper.database import db  # Assuming db is your Database class instance
import os
import random


@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name  
    if file.file_size > 2000 * 1024 * 1024:
        return await message.reply_text("Sorry, this bot doesn't support uploading files bigger than 2GB")
    
    # Creating Directory for Metadata
    if not os.path.isdir("Metadata"):
        os.mkdir("Metadata")
        
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
    except Exception as e:
        return await ms.edit(e)

    _bool_metadata = await db.get_metadata(message.chat.id)

    if _bool_metadata:
        metadata_path = f"Metadata/{new_filename}"
        metadata = await db.get_metadata_code(message.chat.id)
        if metadata:

            await ms.edit("Adding Metadata To File....")
            cmd = f"""ffmpeg -i "{path}" {metadata} "{metadata_path}" """

            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            er = stderr.decode()

            try:
                if er:
                    return await ms.edit(str(er) + "\n\n**Error**")
            except BaseException:
                pass
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

    except:
        pass
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

    upload_type = await db.get_upload_type(message.chat.id)

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
           

        except Exception as e:
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            if metadata_path:
                os.remove(metadata_path)
            if path:
                os.remove(path)
            return await ms.edit(f" Error {e}")

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
          
        except Exception as e:
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            if metadata_path:
                os.remove(metadata_path)
            if path:
                os.remove(path)
            return await ms.edit(f" Error {e}")

    await ms.delete()

    if ph_path:
        os.remove(ph_path)
    if file_path:
        os.remove(file_path)
    if metadata_path:
        os.remove(metadata_path)
