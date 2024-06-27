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
@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename(client, message):
    print("Function called")
    file = getattr(message, message.media.value)
    filename = file.file_name  
    if file.file_size > 2000 * 1024 * 1024:
         return await message.reply_text("Sorry Bro This Bot Doesn't Support Uploading Files Bigger Than 2GB")

#    if message.document:
#        file_id = message.document.file_id
#        file_name = message.document.file_name
#        media_type = media_preference or "document"  # Use preferred media type or default to document
 #       print("Document detected")
#    elif message.video:
 #       file_id = message.video.file_id
 #       file_name = f"{message.video.file_name}.mp4"
#       media_type = media_preference or "video"  # Use preferred media type or default to video
 #       print("Video detected")
 #   else:
 #       print("Unsupported file type")
 #       return await message.reply_text("Unsupported File Type")
#
 #   if not os.path.isdir("Metadata"):
  #      os.mkdir("Metadata")
  #      print("Metadata directory created")

    prefix = await db.get_prefix(message.chat.id)
    suffix = await db.get_suffix(message.chat.id)
    print(f"Prefix: {prefix}, Suffix: {suffix}")

    new_name = filename
    new_filename_ = new_name.split(":-")[1]
    remname_text = await db.get_remname(message.chat.id)  # Get the remname text from the user's database entry
    if remname_text and remname_text in new_filename_:
        new_filename_ = new_filename_.replace(remname_text, "")  # Remove the remname text from the new filename
        print(f"Remname text: {remname_text} removed from filename")

    try:
        # adding prefix and suffix
        new_filename = add_prefix_suffix(new_filename_, prefix, suffix)
        print(f"New filename: {new_filename}")
    except Exception as e:
        print(f"Error setting prefix/suffix: {e}")
        return await message.edit(f"⚠️ Something went wrong, can't set Prefix or Suffix \nError: {e}")

    file_path = f"downloads/{new_filename}"
    file = message

    ms = await message.reply_text(text="Trying To Download.....")

    try:
        path = await bot.download_media(message=file, file_name=file_path, progress=progress_for_pyrogram, progress_args=("**Download Started....\nRenaming as {new_filename_} **", ms, time.time()))
        print(f"File downloaded to {path}")
    except Exception as e:
        print(f"Error downloading media: {e}")
        return await ms.edit(e)

    _bool_metadata = await db.get_metadata(message.chat.id)

    if _bool_metadata:
        metadata_path = f"Metadata/{new_filename}"
        metadata = await db.get_metadata_code(message.chat.id)
        if metadata:
            print("Adding metadata to file")
            await ms.edit("Adding Metadata To File....")
            cmd = f"""ffmpeg -i "{path}" {metadata} "{metadata_path}" """

            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            er = stderr.decode()

            try:
                if er:
                    print(f"FFmpeg error: {er}")
                    return await ms.edit(str(er) + "\n\n**Error**")
            except BaseException as e:
                print(f"Error processing FFmpeg output: {e}")
                pass
        await ms.edit("**Metadata added to the file successfully ✅**\n\n**Trying to upload....**")
    else:
        print("No metadata to add")
        await ms.edit("**Trying to upload....**")

    duration = 0
    try:
        parser = createParser(file_path)
        metadata = extractMetadata(parser)
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        parser.close()
        print(f"File duration: {duration}")
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        pass

    ph_path = None
    media = getattr(file, file.media.value)
    c_caption = await db.get_caption(message.chat.id)
    c_thumb = await db.get_thumbnail(message.chat.id)

    if c_caption:
        try:
            caption = c_caption.format(filename=new_filename, filesize=humanbytes(media.file_size), duration=convert(duration))
            print(f"Caption: {caption}")
        except Exception as e:
            print(f"Caption error: {e}")
            return await ms.edit(text=f"Your Caption Error Exception ●> ({e})")
    else:
        caption = f"**{new_filename}**"
        print(f"Default caption: {caption}")

    if media.thumbs or c_thumb:
        if c_thumb:
            ph_path = await bot.download_media(c_thumb)
            width, height, ph_path = await fix_thumb(ph_path)
            print(f"Custom thumbnail path: {ph_path}")
        else:
            try:
                ph_path_ = await take_screen_shot(file_path, os.path.dirname(os.path.abspath(file_path)), random.randint(0, duration - 1))
                width, height, ph_path = await fix_thumb(ph_path_)
                print(f"Generated thumbnail path: {ph_path}")
            except Exception as e:
                ph_path = None
                print(f"Error generating thumbnail: {e}")

    upload_type = await db.get_upload_type(message.from_user.id)
    print(f"Upload type: {upload_type}")

    if media.file_size > 2000 * 1024 * 1024:
        try:
            if upload_type == "document":
                filw = await app.send_document(
                    Config.LOG_CHANNEL,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("**Upload Started....**", ms, time.time())
                )
                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(message.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)
                print("Document uploaded")
            elif upload_type == "video":
                filw = await app.send_video(
                    update.message.chat.id,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("**Upload Started....**", ms, time.time())
                )
                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(message.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)
                print("Video uploaded")
        except Exception as e:
            print(f"Upload error: {e}")
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
                await bot.send_document(
                    update.message.chat.id,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("**Upload Started....**", ms, time.time())
                )
                print("Document uploaded")
            elif upload_type == "video":
                await bot.send_video(
                    update.message.chat.id,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("**Upload Started....**", ms, time.time())
                )
                print("Video uploaded")
        except Exception as e:
            print(f"Upload error: {e}")
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            if metadata_path:
                os.remove(metadata_path)
            if path:
                os.remove(path)
            return await ms.edit(f" Error {e}")

    await ms.delete()
    print("Message deleted")

    if ph_path:
        os.remove(ph_path)
    if file_path:
        os.remove(file_path)
    if metadata_path:
        os.remove(metadata_path)
    print("Temporary files removed")



