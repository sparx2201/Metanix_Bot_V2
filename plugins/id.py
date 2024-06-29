from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from helper.database import db

# Handle /id command
@Client.on_message(filters.private & filters.command('id'))
async def handle_id_command(client, message):
    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    upload_type = await db.get_upload_type(message.from_user.id)
    print(f"Current upload type for user_id={message.from_user.id} is {upload_type}")
    await ms.delete()
    
    try:
        
        DOC = InlineKeyboardMarkup([
            [InlineKeyboardButton("Document ✔", callback_data="upload_document_on"), 
             InlineKeyboardButton("Video", callback_data="upload_video_on")],  
            [InlineKeyboardButton("Close", callback_data="close")]
        ])

        VID = InlineKeyboardMarkup([
            [InlineKeyboardButton("Document", callback_data="upload_document_on"), 
             InlineKeyboardButton("Video ✔", callback_data="upload_video_on")],  
            [InlineKeyboardButton("Close", callback_data="close")]
        ])

        if upload_type == "document":
            await message.reply_text(f"Your current upload format: **Document**.", reply_markup=DOC)
            print(f"Reply sent: Current upload format is Document for user_id={user_id}")
        elif upload_type == "video":
            await message.reply_text(f"Your current upload format: **Video**.", reply_markup=VID)
            print(f"Reply sent: Current upload format is Video for user_id={user_id}")
        else:
            print(f"Unknown upload type for user_id={user_id}")
            await message.reply_text("Unknown upload type. Please set your upload type.")
    except Exception as e:
        print(f"Error handling /id command for user_id={user_id}: {e}")
        await message.reply_text("An error occurred. Please try again later.")
    finally:
        await ms.delete()

# Handle callback queries
@Client.on_callback_query()
async def handle_callback_query(client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    print(f"Callback query received: data={data}, user_id={user_id}")

    DOC = InlineKeyboardMarkup([
        [InlineKeyboardButton("Document ✔", callback_data="upload_document_on"), 
         InlineKeyboardButton("Video", callback_data="upload_video_on")],  
        [InlineKeyboardButton("Close", callback_data="close")]
    ])

    VID = InlineKeyboardMarkup([
        [InlineKeyboardButton("Document", callback_data="upload_document_on"), 
         InlineKeyboardButton("Video ✔", callback_data="upload_video_on")],  
        [InlineKeyboardButton("Close", callback_data="close")]
    ])

    try:
        if data == "upload_document_on":
            await db.set_upload_type(user_id, "document")
            await query.message.edit_text(text="Your current upload format: **Document**.", disable_web_page_preview=True, reply_markup=DOC)
            print(f"Set upload type to Document for user_id={user_id}")
        
        elif data == "upload_video_on":
            await db.set_upload_type(user_id, "video")
            await query.message.edit_text(text="Your current upload format: **Video**.", disable_web_page_preview=True, reply_markup=VID)
            print(f"Set upload type to Video for user_id={user_id}")
        
        elif data == "close":
            await query.message.delete()
            print(f"Closed message for user_id={user_id}")
    except Exception as e:
        print(f"Error handling callback query for user_id={user_id}: {e}")


@Client.on_message(filters.private & filters.command('del'))
async def handle_id_command(client, message):
    
    await db.delete_upload_type(message.from_user.id)
    await message.reply_text("done")
