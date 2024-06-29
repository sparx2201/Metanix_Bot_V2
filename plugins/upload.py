from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from helper.database import db
from config import Config
import logging
from pyrogram.errors import FloodWait
import humanize




ON = InlineKeyboardMarkup([
    [InlineKeyboardButton("Set to Document", callback_data="upload_document_on")],
    [InlineKeyboardButton("Set to Video", callback_data="upload_video_on")]
])

# Handle /upload command
@Client.on_message(filters.private & filters.command('upload'))
async def handle_upload_settings(client, message):
    print(f"Upload command received from user_id={message.from_user.id}")
    # Here we simulate the upload type retrieval; replace this with actual database call if needed
    upload_type = "unknown"  # Simulate the condition where the type is not set yet
    # You can change the value of upload_type to "document" or "video" to simulate different scenarios
    
    if upload_type == "document":
        await message.reply_text(
            "Your current upload format is set to **Document**.",
            reply_markup=ON
        )
        print(f"Reply sent: Current upload format is Document for user_id={message.from_user.id}")
    elif upload_type == "video":
        await message.reply_text(
            "Your current upload format is set to **Video**.",
            reply_markup=ON
        )
        print(f"Reply sent: Current upload format is Video for user_id={message.from_user.id}")
    else:
        await message.reply_text(
            "Please select the upload format:",
            reply_markup=ON
        )
        print(f"Reply sent: User needs to select upload format for user_id={message.from_user.id}")

# Handle callback queries
@Client.on_callback_query()
async def set_upload_format(client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    print(f"Callback query received: data={data}, user_id={user_id}")

    if data == "upload_document_on":
        await query.message.delete()
        # Simulate setting the upload type; replace this with actual database call if needed
        upload_type = "document"
        await query.message.reply_text("Upload format set to **document**.")
        print(f"Upload format set to document for user_id={user_id}")
    
    elif data == "upload_video_on":
        await query.message.delete()
        # Simulate setting the upload type; replace this with actual database call if needed
        upload_type = "video"
        await query.message.reply_text("Upload format set to **video**.")
        print(f"Upload format set to video for user_id={user_id}")

          

from pyrogram import Client, filters
from helper.database import db  # Assuming db is your Database class instance

# REMNAME
@Client.on_message(filters.private & filters.command('document'))
async def upload_document(client, message):
    # Get all the text patterns provided in the command
    SnowDev = await message.reply_text("Please Wait ...")
    user_id = message.from_user.id
    await db.set_upload_type(user_id, "document")
    await SnowDev.edit("**Upload format set to Document ✅**")

@Client.on_message(filters.private & filters.command('video'))
async def upload_video(client, message):
    SnowDev = await message.reply_text("Please Wait ...")
    user_id = message.from_user.id
    await db.set_upload_type(user_id, "video")
    await SnowDev.edit("**Upload format set to Video ✅**")
