import logging
import time
import re
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from config import ADMINS, INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.study_db import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp, get_readable_time
from math import ceil

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

lock = asyncio.Lock()

@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")
    _, raju, chat, lst_msg_id, from_user = query.data.split("#")
    if raju == 'reject':
        await query.message.delete()
        await bot.send_message(int(from_user),
                               f'Your Submission for indexing {chat} has been declined by our moderators.',
                               reply_to_message_id=int(lst_msg_id))
        return

    if lock.locked():
        return await query.answer('Wait until previous process complete.', show_alert=True)
    msg = query.message

    await query.answer('Processing...⏳', show_alert=True)
    if int(from_user) not in ADMINS:
        await bot.send_message(int(from_user),
                               f'Your Submission for indexing {chat} has been accepted by our moderators and will be added soon.',
                               reply_to_message_id=int(lst_msg_id))
    await msg.edit(
        "Starting Indexing",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
        )
    )
    try:
        chat = int(chat)
    except:
        chat = chat
    await index_files_to_db(int(lst_msg_id), chat, msg, bot)


@Client.on_message((filters.forwarded | (filters.regex(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text ) & filters.private & filters.incoming)
async def send_for_index(bot, message):
    if message.text:
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match:
            return await message.reply('Invalid link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id  = int(("-100" + chat_id))
    elif message.forward_from_chat and message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return
    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply('This may be a private channel / group. Make me an admin over there to index the files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        logger.exception(e)
        return await message.reply(f'Errors - {e}')
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply('Make Sure That Iam An Admin In The Channel, if channel is private')
    if k.empty:
        return await message.reply('This may be group and i am not a admin of the group.')

    if message.from_user.id in ADMINS:
        buttons = [
            [InlineKeyboardButton('Yes', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
            [InlineKeyboardButton('Close', callback_data='close_data')]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        return await message.reply(
            f'Do you Want To Index This Channel/ Group ?\n\nChat ID/ Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>\n\nɴᴇᴇᴅ sᴇᴛsᴋɪᴘ 👉🏻 /setskip',
            reply_markup=reply_markup)

    if type(chat_id) is int:
        try:
            link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired:
            return await message.reply('Make sure I am an admin in the chat and have permission to invite users.')
        except Exception as e:
            return await message.reply(f'Make sure I am an admin in the chat and have permission to invite users.\n\nError: {e}')
    else:
        link = f"https://t.me/{chat_id}"
    
    await bot.send_message(LOG_CHANNEL,
        f'#index_request\n\nBy : {message.from_user.mention} (<code>{message.from_user.id}</code>)\nChat ID/ Username : <code>{chat_id}</code>\nChat Title : {k.chat.title}\n\nLast Message ID: <code>{last_msg_id}</code>\n\nLink : {link}',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('Accept', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
            [InlineKeyboardButton('Reject', callback_data=f'index#reject#{chat_id}#{last_msg_id}#{message.from_user.id}')]
        ])
    )

async def index_files_to_db(lst_msg_id, chat, msg, bot):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    index = 0
    temp.CANCEL = False
    
    async for message in bot.iter_messages(chat, lst_msg_id, reverse=True):
        if temp.CANCEL:
            await msg.edit(f"Successfully Cancelled!!\n\nCompleted : {index}\nTotal Saved : {total_files}\nDuplicate : {duplicate}\nDeleted : {deleted}\nErrors : {errors}\nUnsupported : {unsupported}")
            break
        
        if message.empty:
            continue
        
        if message.media not in [enums.MessageMediaType.DOCUMENT, enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.PHOTO]:
            no_media += 1
            continue
        
        try:
            file = await save_file(message)
            if file:
                total_files += 1
            else:
                duplicate += 1
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            errors += 1
            continue
        
        index += 1
        if index % 20 == 0:
            try:
                await msg.edit(f"Indexing...\n\nCompleted : {index}\nTotal Saved : {total_files}\nDuplicate : {duplicate}\nDeleted : {deleted}\nErrors : {errors}\nUnsupported : {unsupported}")
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                logger.error(f"Error updating message: {e}")
    
    await msg.edit(f"Indexing Completed!\n\nTotal Files : {total_files}\nDuplicate : {duplicate}\nDeleted : {deleted}\nErrors : {errors}\nUnsupported : {unsupported}")
