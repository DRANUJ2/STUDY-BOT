import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.study_db import *
from config import *
from studybot.Bot import studybot, content_bot
import re
import json

logger = logging.getLogger(__name__)

# Command handlers
@studybot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    """Handle /start command in private chat"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    # Create or update user
    user = await Users.find_one({"_id": user_id})
    if not user:
        user_doc = Users(
            user_id=user_id,
            first_name=first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username
        )
        await user_doc.commit()
    
    welcome_text = f"""Hello {first_name}! 👋

Welcome to the Study Bot! 📚

Use /Anuj <batch_name> to start studying.
Example: /Anuj NEET2026

Features:
• 📖 Access study materials
• 📝 Download notes and DPPs
• 🎯 Track your progress
• 🏆 Earn achievements

Start your learning journey today! 🚀"""
    
    await message.reply_text(welcome_text)

@studybot.on_message(filters.command("Anuj") & (filters.group | filters.private))
async def anuj_command(client: Client, message: Message):
    """Handle /Anuj command for batch selection"""
    try:
        # Check if PM is enabled
        if not PM_ON and message.chat.type == "private":
            await message.reply_text("❌ PM is currently disabled. Please use this command in a group.")
            return
        
        # Extract batch name
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply_text("❌ Please provide a batch name.\n\nUsage: /Anuj <batch_name>\nExample: /Anuj NEET2026")
            return
        
        batch_name = command_parts[1].strip()
        
        # Get batch info
        batch_info = await get_batch_info(batch_name)
        if not batch_info:
            # Create default batch if it doesn't exist
            await create_batch(batch_name, created_by=message.from_user.id)
            batch_info = await get_batch_info(batch_name)
        
        # Create batch selection keyboard
        keyboard = []
        for subject in batch_info.subjects:
            keyboard.append([InlineKeyboardButton(subject, callback_data=f"subject_{batch_name}_{subject}")])
        
        # Add surprise button
        keyboard.append([InlineKeyboardButton("🎁 Surprise Here", url="https://t.me/your_channel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send batch image with caption
        caption = f"📚 **{batch_name}**\n\nSelect your subject to continue:"
        
        if batch_info.batch_image:
            await message.reply_photo(
                photo=batch_info.batch_image,
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            await message.reply_text(
                text=caption,
                reply_markup=reply_markup
            )
        
        # Forward to PM if in group and PM is enabled
        if message.chat.type == "group" and PM_ON:
            try:
                await client.send_message(
                    chat_id=message.from_user.id,
                    text=f"🎯 You selected batch: **{batch_name}**\n\nContinue here for better experience!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🚀 Continue", callback_data=f"continue_{batch_name}")
                    ]])
                )
            except Exception as e:
                logger.error(f"Failed to send PM: {e}")
                
    except Exception as e:
        logger.error(f"Error in anuj command: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.")

@studybot.on_callback_query(filters.regex(r"^subject_"))
async def subject_callback(client: Client, callback_query: CallbackQuery):
    """Handle subject selection callback"""
    try:
        data = callback_query.data
        _, batch_name, subject = data.split("_", 2)
        
        # Create teacher selection keyboard
        keyboard = []
        batch_info = await get_batch_info(batch_name)
        
        for teacher in batch_info.teachers:
            keyboard.append([InlineKeyboardButton(teacher, callback_data=f"teacher_{batch_name}_{subject}_{teacher}")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"back_batch_{batch_name}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(
            text=f"👨‍🏫 **{subject}**\n\nSelect your teacher:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in subject callback: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

@studybot.on_callback_query(filters.regex(r"^teacher_"))
async def teacher_callback(client: Client, callback_query: CallbackQuery):
    """Handle teacher selection callback"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher = data.split("_", 3)
        
        # Create chapter selection keyboard
        keyboard = []
        
        # Chapter by number button
        keyboard.append([InlineKeyboardButton("📊 Chapter by Number", callback_data=f"chapters_num_{batch_name}_{subject}_{teacher}")])
        
        # Chapter by name button
        keyboard.append([InlineKeyboardButton("📖 Chapter by Name", callback_data=f"chapters_name_{batch_name}_{subject}_{teacher}")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"back_subject_{batch_name}_{subject}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(
            text=f"📚 **{subject}** - {teacher}\n\nSelect chapter selection method:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in teacher callback: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

@studybot.on_callback_query(filters.regex(r"^chapters_num_"))
async def chapters_num_callback(client: Client, callback_query: CallbackQuery):
    """Handle chapter by number selection"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher = data.split("_", 3)
        
        # Create chapter number keyboard
        keyboard = []
        
        # Generate chapter numbers (CH01, CH02, etc.)
        for i in range(1, MAX_CHAPTERS + 1):
            chapter_no = f"CH{i:02d}"
            keyboard.append([InlineKeyboardButton(chapter_no, callback_data=f"chapter_{batch_name}_{subject}_{teacher}_{chapter_no}")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"back_teacher_{batch_name}_{subject}_{teacher}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(
            text=f"📊 **{subject}** - {teacher}\n\nSelect chapter number:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in chapters num callback: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

@studybot.on_callback_query(filters.regex(r"^chapters_name_"))
async def chapters_name_callback(client: Client, callback_query: CallbackQuery):
    """Handle chapter by name selection"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher = data.split("_", 3)
        
        # Create chapter name keyboard
        keyboard = []
        
        # Sample chapter names (you can customize these)
        chapter_names = [
            "WAVES", "MECHANICS", "THERMODYNAMICS", "ELECTROMAGNETISM",
            "OPTICS", "MODERN PHYSICS", "ATOMIC STRUCTURE", "CHEMICAL BONDING",
            "THERMOCHEMISTRY", "ELECTROCHEMISTRY", "ORGANIC CHEMISTRY",
            "BIOMOLECULES", "CELL BIOLOGY", "GENETICS", "ECOLOGY"
        ]
        
        for chapter_name in chapter_names:
            keyboard.append([InlineKeyboardButton(
                f"[CH-{len(keyboard)+1}] {chapter_name}", 
                callback_data=f"chapter_{batch_name}_{subject}_{teacher}_CH{len(keyboard)+1:02d}"
            )])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"back_teacher_{batch_name}_{subject}_{teacher}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(
            text=f"📖 **{subject}** - {teacher}\n\nSelect chapter:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in chapters name callback: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

@studybot.on_callback_query(filters.regex(r"^chapter_"))
async def chapter_callback(client: Client, callback_query: CallbackQuery):
    """Handle chapter selection callback"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher, chapter_no = data.split("_", 4)
        
        # Create content type selection keyboard
        keyboard = []
        
        # Main content buttons
        keyboard.append([InlineKeyboardButton("📹 Lectures", callback_data=f"content_{batch_name}_{subject}_{teacher}_{chapter_no}_LECTURES")])
        keyboard.append([InlineKeyboardButton("📝 DPP", callback_data=f"content_{batch_name}_{subject}_{teacher}_{chapter_no}_DPP")])
        keyboard.append([InlineKeyboardButton("📚 All Study Materials", callback_data=f"content_{batch_name}_{subject}_{teacher}_{chapter_no}_ALL")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"back_chapters_{batch_name}_{subject}_{teacher}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(
            text=f"📚 **{subject}** - {teacher}\n**Chapter {chapter_no}**\n\nSelect content type:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in chapter callback: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

@studybot.on_callback_query(filters.regex(r"^content_"))
async def content_callback(client: Client, callback_query: CallbackQuery):
    """Handle content type selection callback"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher, chapter_no, content_type = data.split("_", 5)
        
        if content_type == "LECTURES":
            await handle_lectures(client, callback_query, batch_name, subject, teacher, chapter_no)
        elif content_type == "DPP":
            await handle_dpp(client, callback_query, batch_name, subject, teacher, chapter_no)
        elif content_type == "ALL":
            await handle_all_materials(client, callback_query, batch_name, subject, teacher, chapter_no)
        else:
            await callback_query.answer("❌ Invalid content type", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error in content callback: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

async def handle_lectures(client: Client, callback_query: CallbackQuery, batch_name: str, subject: str, teacher: str, chapter_no: str):
    """Handle lecture content selection"""
    try:
        keyboard = []
        
        # Generate lecture buttons (L01, L02, L03, etc.)
        for i in range(1, MAX_LECTURES + 1):
            lecture_no = f"L{i:02d}"
            keyboard.append([InlineKeyboardButton(
                lecture_no, 
                callback_data=f"lecture_{batch_name}_{subject}_{teacher}_{chapter_no}_{lecture_no}"
            )])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"back_chapter_{batch_name}_{subject}_{teacher}_{chapter_no}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(
            text=f"📹 **{subject}** - {teacher}\n**Chapter {chapter_no}**\n\nSelect lecture:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in handle lectures: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

async def handle_dpp(client: Client, callback_query: CallbackQuery, batch_name: str, subject: str, teacher: str, chapter_no: str):
    """Handle DPP content selection"""
    try:
        keyboard = []
        
        # DPP options
        keyboard.append([InlineKeyboardButton("🧩 Quiz DPP", callback_data=f"dpp_{batch_name}_{subject}_{teacher}_{chapter_no}_QUIZ")])
        keyboard.append([InlineKeyboardButton("📄 PDF DPP", callback_data=f"dpp_{batch_name}_{subject}_{teacher}_{chapter_no}_PDF")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"back_chapter_{batch_name}_{subject}_{teacher}_{chapter_no}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(
            text=f"📝 **{subject}** - {teacher}\n**Chapter {chapter_no}**\n\nSelect DPP type:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in handle DPP: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

async def handle_all_materials(client: Client, callback_query: CallbackQuery, batch_name: str, subject: str, teacher: str, chapter_no: str):
    """Handle all study materials selection"""
    try:
        keyboard = []
        
        # All study material options
        materials = [
            ("🧠 Mind Maps", "mind_maps"),
            ("📖 Revision", "revision"),
            ("📝 Short Notes", "short_notes"),
            ("❓ PYQs", "pyqs"),
            ("📄 KPP PDF", "kpp_pdf"),
            ("✅ KPP Solution", "kpp_solution"),
            ("📋 Practice Sheet", "practice_sheet"),
            ("🎯 Kattar NEET 2026", "kattar_neet"),
            ("⭐ Important", "important"),
            ("✍️ Handwritten Notes", "handwritten"),
            ("📚 Module Question", "module_question")
        ]
        
        for material_name, material_type in materials:
            keyboard.append([InlineKeyboardButton(
                material_name, 
                callback_data=f"material_{batch_name}_{subject}_{teacher}_{chapter_no}_{material_type}"
            )])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"back_chapter_{batch_name}_{subject}_{teacher}_{chapter_no}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(
            text=f"📚 **{subject}** - {teacher}\n**Chapter {chapter_no}**\n\nSelect study material:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in handle all materials: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle final content selection and forward to content bot
@studybot.on_callback_query(filters.regex(r"^(lecture|dpp|material)_"))
async def final_content_callback(client: Client, callback_query: CallbackQuery):
    """Handle final content selection and forward to content bot"""
    try:
        data = callback_query.data
        content_type, batch_name, subject, teacher, chapter_no, specific_type = data.split("_", 5)
        
        # Get content from database
        files = await get_study_files(
            batch_name=batch_name,
            subject=subject,
            chapter_no=chapter_no,
            content_type=content_type.upper()
        )
        
        if not files:
            await callback_query.answer("❌ No content found for this selection", show_alert=True)
            return
        
        # Forward to content bot
        try:
            await content_bot.send_message(
                chat_id=callback_query.from_user.id,
                text=f"📚 **{batch_name}** - {subject}\n**Chapter {chapter_no}**\n\nHere's your requested content:"
            )
            
            # Send files (you can customize this based on your content bot setup)
            for file in files[:5]:  # Limit to 5 files
                await content_bot.send_message(
                    chat_id=callback_query.from_user.id,
                    text=f"📄 {file.file_name}\n\n**Type:** {file.content_type}\n**Size:** {file.file_size} bytes"
                )
            
            await callback_query.answer("✅ Content sent to your PM!", show_alert=True)
            
        except Exception as e:
            logger.error(f"Error forwarding to content bot: {e}")
            await callback_query.answer("❌ Failed to send content", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error in final content callback: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Back button handlers
@studybot.on_callback_query(filters.regex(r"^back_"))
async def back_button_callback(client: Client, callback_query: CallbackQuery):
    """Handle back button navigation"""
    try:
        data = callback_query.data
        _, back_type, *params = data.split("_")
        
        if back_type == "batch":
            batch_name = params[0]
            await anuj_command(client, callback_query.message)
        elif back_type == "subject":
            batch_name, subject = params
            await subject_callback(client, callback_query)
        elif back_type == "teacher":
            batch_name, subject, teacher = params
            await teacher_callback(client, callback_query)
        elif back_type == "chapters":
            batch_name, subject, teacher = params
            await teacher_callback(client, callback_query)
        elif back_type == "chapter":
            batch_name, subject, teacher, chapter_no = params
            await chapter_callback(client, callback_query)
        else:
            await callback_query.answer("❌ Invalid back navigation", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error in back button callback: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Admin commands
@studybot.on_message(filters.command("addbatch") & filters.user(ADMINS))
async def add_batch_command(client: Client, message: Message):
    """Admin command to add new batch"""
    try:
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply_text("❌ Usage: /addbatch <batch_name>")
            return
        
        batch_name = command_parts[1].strip()
        
        # Create batch
        success = await create_batch(batch_name, created_by=message.from_user.id)
        
        if success:
            await message.reply_text(f"✅ Batch '{batch_name}' created successfully!")
        else:
            await message.reply_text(f"❌ Failed to create batch '{batch_name}'")
            
    except Exception as e:
        logger.error(f"Error in add batch command: {e}")
        await message.reply_text("❌ An error occurred")

@studybot.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_command(client: Client, message: Message):
    """Admin command to show bot statistics"""
    try:
        # Get basic stats
        total_files = await StudyFiles.count_documents({"is_active": True})
        total_users = await Users.count_documents({})
        total_batches = await Batches.count_documents({"is_active": True})
        
        stats_text = f"📊 **Study Bot Statistics**\n\n"
        stats_text += f"📁 Total Files: {total_files}\n"
        stats_text += f"👥 Total Users: {total_users}\n"
        stats_text += f"📚 Total Batches: {total_batches}\n"
        
        await message.reply_text(stats_text)
        
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await message.reply_text("❌ An error occurred")
