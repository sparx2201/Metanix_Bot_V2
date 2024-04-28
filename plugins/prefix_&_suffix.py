from pyrogram import Client, filters, enums
from helper.database import db


@Client.on_message(filters.private & filters.command('set_prefix'))
async def add_caption(client, message):

    if len(message.command) == 1:
        return await message.reply_text("**__Give The Prefix__\n\nExᴀᴍᴩʟᴇ:- `/set_prefix @MetaNiXbot`**")
    prefix = message.text.split(" ", 1)[1]
    SnowDev = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    await db.set_prefix(message.from_user.id, prefix)
    await SnowDev.edit("__**✅ ᴘʀᴇꜰɪx ꜱᴀᴠᴇᴅ**__")


@Client.on_message(filters.private & filters.command('del_prefix'))
async def delete_prefix(client, message):

    SnowDev = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    prefix = await db.get_prefix(message.from_user.id)
    if not prefix:
        return await SnowDev.edit("__** ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴘʀᴇꜰɪx**__")
    await db.set_prefix(message.from_user.id, None)
    await SnowDev.edit("__**❌️ ᴘʀᴇꜰɪx ᴅᴇʟᴇᴛᴇᴅ**__")


@Client.on_message(filters.private & filters.command('see_prefix'))
async def see_caption(client, message):

    SnowDev = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    prefix = await db.get_prefix(message.from_user.id)
    if prefix:
        await SnowDev.edit(f"**ʏᴏᴜʀ ᴘʀᴇꜰɪx:-**\n\n`{prefix}`")
    else:
        await SnowDev.edit("__** ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴘʀᴇꜰɪx**__")


# SUFFIX
@Client.on_message(filters.private & filters.command('set_suffix'))
async def add_csuffix(client, message):

    if len(message.command) == 1:
        return await message.reply_text("**__Give The Suffix__\n\nExᴀᴍᴩʟᴇ:- `/set_suffix @MetaNiXbot`**")
    suffix = message.text.split(" ", 1)[1]
    SnowDev = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    await db.set_suffix(message.from_user.id, suffix)
    await SnowDev.edit("__**✅ ꜱᴜꜰꜰɪx ꜱᴀᴠᴇᴅ**__")


@Client.on_message(filters.private & filters.command('del_suffix'))
async def delete_suffix(client, message):

    SnowDev = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    suffix = await db.get_suffix(message.from_user.id)
    if not suffix:
        return await SnowDev.edit("__** ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ꜱᴜꜰꜰɪx**__")
    await db.set_suffix(message.from_user.id, None)
    await SnowDev.edit("__**❌️ ꜱᴜꜰꜰɪx ᴅᴇʟᴇᴛᴇᴅ**__")


@Client.on_message(filters.private & filters.command('see_suffix'))
async def see_csuffix(client, message):

    SnowDev = await message.reply_text("Please Wait ...", reply_to_message_id=message.id)
    suffix = await db.get_suffix(message.from_user.id)
    if suffix:
        await SnowDev.edit(f"**ʏᴏᴜʀ ꜱᴜꜰꜰɪx:-**\n\n`{suffix}`")
    else:
        await SnowDev.edit("__** ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ꜱᴜꜰꜰɪx**__")


@Client.on_message(app.filters.private & app.filters.command('set_remname'))
async def add_remname(client, message):
    if len(message.command) == 1:
        return await message.reply_text("**__Give The Remname Text__\n\nExample:- `/set_remname text_pattern1, text_pattern2, ...`**")
    
    # Get all the text patterns provided in the command
    remname_text = message.text.split(' ', 1)[1]
    remname_patterns = [pattern.strip() for pattern in remname_text.split(',')]
    
    SnowDev = await message.reply_text("Please Wait ...")
    for pattern in remname_patterns:
        await jishubotz.add_remname(message.from_user.id, pattern)
    
    await SnowDev.edit("**Remname Text Saved Successfully ✅**")

@Client.on_message(app.filters.private & app.filters.command('del_remname'))
async def delete_remname(client, message):
    SnowDev = await message.reply_text("Please Wait ...")
    await jishubotz.delete_remname(message.from_user.id)
    await SnowDev.edit("**Remname Text Deleted Successfully 🗑️**")

@Client.on_message(app.filters.private & app.filters.command('see_remname'))
async def see_remname(client, message):
    SnowDev = await message.reply_text("Please Wait ...")
    remname_text = await jishubotz.get_remname(message.from_user.id)
    if remname_text:
        await SnowDev.edit(f"**Your Remname Texts:-**\n\n{remname_text}")
    else:
        await SnowDev.edit("**You Don't Have Any Remname Texts ❌**")

