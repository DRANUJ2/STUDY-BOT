import logging
import asyncio
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.study_db import db as study_db
from config import *
from utils import temp, get_readable_time

logger = logging.getLogger(__name__)

# PM filter for batch commands
@Client.on_message(filters.command("Anuj") & filters.private)
async def handle_batch_command_pm(client: Client, message: Message):
    """Handle /Anuj command in private messages"""
    try:
        # Extract batch name from command
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply_text("❌ Please provide a batch name.\n\nUsage: /Anuj <batch_name>\n\nExample: /Anuj NEET2026")
            return
        
        batch_name = command_parts[1].strip()
        
        # Process batch command
        await process_batch_command(client, message, batch_name, is_pm=True)
        
    except Exception as e:
        logger.error(f"Error in PM batch command: {e}")
        await message.reply_text("❌ An error occurred while processing your request.")

# Group filter for batch commands
@Client.on_message(filters.command("Anuj") & filters.group)
async def handle_batch_command_group(client: Client, message: Message):
    """Handle /Anuj command in groups"""
    try:
        # Check if PM is enabled
        if not PM_FILTER:
            await message.reply_text("❌ Private messaging is disabled. Please contact the bot owner.")
            return
        
        # Extract batch name from command
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply_text("❌ Please provide a batch name.\n\nUsage: /Anuj <batch_name>\n\nExample: /Anuj NEET2026")
            return
        
        batch_name = command_parts[1].strip()
        
        # Process batch command
        await process_batch_command(client, message, batch_name, is_pm=False)
        
    except Exception as e:
        logger.error(f"Error in group batch command: {e}")
        await message.reply_text("❌ An error occurred while processing your request.")

async def process_batch_command(client: Client, message: Message, batch_name: str, is_pm: bool):
    """Process batch command and show batch information"""
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        
        # Get or create user
        user = await study_db.get_user(user_id)
        if not user:
            await study_db.add_user(user_id, first_name)
        
        # Update user's current batch and last active
        await study_db.update_user(user_id, {
            'current_batch': batch_name,
            'last_active': int(asyncio.get_event_loop().time())
        })
        
        # Get batch information
        batch = await study_db.get_batch(batch_name)
        if not batch:
            # Create default batch if it doesn't exist
            await study_db.add_batch(batch_name, {
                'subjects': ["Physics", "Chemistry", "Biology"],
                'teachers': ["Mr Sir", "Saleem Sir"],
                'is_active': True,
                'created_at': int(asyncio.get_event_loop().time())
            })
        
        # Create batch image caption
        caption = f"""📚 **{batch_name.upper()}** 📚

🎯 **Welcome to your study journey!**

📖 **Available Subjects:**
• Physics
• Chemistry  
• Biology

👨‍🏫 **Teachers:**
• Mr Sir
• Saleem Sir

💡 **Select a subject to continue**"""
        
        # Create subject selection buttons
        keyboard = [
            [InlineKeyboardButton("🧪 Physics", callback_data=f"subject_{batch_name}_Physics")],
            [InlineKeyboardButton("⚗️ Chemistry", callback_data=f"subject_{batch_name}_Chemistry")],
            [InlineKeyboardButton("🧬 Biology", callback_data=f"subject_{batch_name}_Biology")],
            [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")],
            [InlineKeyboardButton("📊 Batch Stats", callback_data=f"batch_stats_{batch_name}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send batch image with caption and buttons
        if is_pm:
            # Already in PM, send directly
            await message.reply_text(caption, reply_markup=reply_markup)
        else:
            # In group, send with PM instruction
            group_message = f"""👋 **{first_name}**, I've found your batch!

📚 **{batch_name.upper()}** is available.

🔐 **Please check your private messages** to continue with your studies.

💡 **Tip:** Make sure you've started the bot in PM first."""
            
            await message.reply_text(group_message)
            
            # Send to PM
            try:
                await client.send_message(
                    user_id,
                    caption,
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Failed to send PM to {user_id}: {e}")
                await message.reply_text("❌ I couldn't send you a private message. Please start the bot in PM first.")
        
        # Log the interaction
        logger.info(f"User {user_id} ({first_name}) accessed batch: {batch_name}")
        
    except Exception as e:
        logger.error(f"Error processing batch command: {e}")
        await message.reply_text("❌ An error occurred while processing your batch request.")

# Handle subject selection callback
@Client.on_callback_query(filters.regex(r"^subject_"))
async def handle_subject_selection(client: Client, callback_query):
    """Handle subject selection callback"""
    try:
        data = callback_query.data
        _, batch_name, subject = data.split("_", 2)
        
        user_id = callback_query.from_user.id
        
        # Update user's current subject
        await study_db.update_user(user_id, {'current_subject': subject})
        
        # Create teacher selection buttons
        caption = f"""📚 **{batch_name.upper()}** - {subject}

👨‍🏫 **Select your teacher:**"""
        
        keyboard = [
            [InlineKeyboardButton("👨‍🏫 Mr Sir", callback_data=f"teacher_{batch_name}_{subject}_Mr Sir")],
            [InlineKeyboardButton("👨‍🏫 Saleem Sir", callback_data=f"teacher_{batch_name}_{subject}_Saleem Sir")],
            [InlineKeyboardButton("🔙 Back to Subjects", callback_data=f"back_subjects_{batch_name}")],
            [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(caption, reply_markup=reply_markup)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in subject selection: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle teacher selection callback
@Client.on_callback_query(filters.regex(r"^teacher_"))
async def handle_teacher_selection(client: Client, callback_query):
    """Handle teacher selection callback"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher = data.split("_", 3)
        
        user_id = callback_query.from_user.id
        
        # Update user's current teacher
        await study_db.update_user(user_id, {'current_teacher': teacher})
        
        # Create chapter selection buttons
        caption = f"""📚 **{batch_name.upper()}** - {subject}
👨‍🏫 **Teacher:** {teacher}

📖 **Select chapter format:**"""
        
        keyboard = [
            [InlineKeyboardButton("🔢 Chapter Numbers", callback_data=f"chapters_num_{batch_name}_{subject}_{teacher}")],
            [InlineKeyboardButton("📝 Chapter Names", callback_data=f"chapters_name_{batch_name}_{subject}_{teacher}")],
            [InlineKeyboardButton("🔙 Back to Teachers", callback_data=f"back_teachers_{batch_name}_{subject}")],
            [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(caption, reply_markup=reply_markup)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in teacher selection: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle chapter number selection
@Client.on_callback_query(filters.regex(r"^chapters_num_"))
async def handle_chapter_numbers(client: Client, callback_query):
    """Handle chapter number selection"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher = data.split("_", 3)
        
        # Create chapter number buttons (CH01, CH02, etc.)
        caption = f"""📚 **{batch_name.upper()}** - {subject}
👨‍🏫 **Teacher:** {teacher}
🔢 **Select Chapter Number:**"""
        
        keyboard = []
        for i in range(1, 21):  # CH01 to CH20
            chapter_num = f"CH{i:02d}"
            keyboard.append([InlineKeyboardButton(
                chapter_num, 
                callback_data=f"chapter_{batch_name}_{subject}_{teacher}_{chapter_num}"
            )])
        
        # Add navigation and other buttons
        keyboard.extend([
            [InlineKeyboardButton("🔙 Back to Format", callback_data=f"back_format_{batch_name}_{subject}_{teacher}")],
            [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(caption, reply_markup=reply_markup)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in chapter numbers: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle chapter name selection
@Client.on_callback_query(filters.regex(r"^chapters_name_"))
async def handle_chapter_names(client: Client, callback_query):
    """Handle chapter name selection"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher = data.split("_", 3)
        
        # Sample chapter names for different subjects
        chapter_names = {
            "Physics": [
                "[CH-1] WAVES", "[CH-2] OPTICS", "[CH-3] MECHANICS",
                "[CH-4] THERMODYNAMICS", "[CH-5] ELECTROMAGNETISM"
            ],
            "Chemistry": [
                "[CH-1] ORGANIC", "[CH-2] INORGANIC", "[CH-3] PHYSICAL",
                "[CH-4] ANALYTICAL", "[CH-5] BIOCHEMISTRY"
            ],
            "Biology": [
                "[CH-1] CELL BIOLOGY", "[CH-2] GENETICS", "[CH-3] ECOLOGY",
                "[CH-4] ANATOMY", "[CH-5] PHYSIOLOGY"
            ]
        }
        
        chapters = chapter_names.get(subject, [])
        
        caption = f"""📚 **{batch_name.upper()}** - {subject}
👨‍🏫 **Teacher:** {teacher}
📝 **Select Chapter Name:**"""
        
        keyboard = []
        for chapter in chapters:
            keyboard.append([InlineKeyboardButton(
                chapter, 
                callback_data=f"chapter_{batch_name}_{subject}_{teacher}_{chapter}"
            )])
        
        # Add navigation and other buttons
        keyboard.extend([
            [InlineKeyboardButton("🔙 Back to Format", callback_data=f"back_format_{batch_name}_{subject}_{teacher}")],
            [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(caption, reply_markup=reply_markup)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in chapter names: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle chapter selection
@Client.on_callback_query(filters.regex(r"^chapter_"))
async def handle_chapter_selection(client: Client, callback_query):
    """Handle chapter selection and show content options"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher, chapter = data.split("_", 4)
        
        user_id = callback_query.from_user.id
        
        # Update user's current chapter
        await study_db.update_user(user_id, {'current_chapter': chapter})
        
        # Create content type selection buttons
        caption = f"""📚 **{batch_name.upper()}** - {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}

📝 **Select content type:**"""
        
        keyboard = [
            [InlineKeyboardButton("📖 Lectures", callback_data=f"content_lectures_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("📝 DPP", callback_data=f"content_dpp_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("📚 ALL STUDY MATERIALS", callback_data=f"content_all_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("🔙 Back to Chapters", callback_data=f"back_chapters_{batch_name}_{subject}_{teacher}")],
            [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(caption, reply_markup=reply_markup)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in chapter selection: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle content type selection
@Client.on_callback_query(filters.regex(r"^content_"))
async def handle_content_selection(client: Client, callback_query):
    """Handle content type selection and deliver content"""
    try:
        data = callback_query.data
        _, content_type, batch_name, subject, teacher, chapter = data.split("_", 5)
        
        user_id = callback_query.from_user.id
        
        if content_type == "lectures":
            await show_lectures(client, callback_query, batch_name, subject, teacher, chapter)
        elif content_type == "dpp":
            await show_dpp(client, callback_query, batch_name, subject, teacher, chapter)
        elif content_type == "all":
            await show_all_materials(client, callback_query, batch_name, subject, teacher, chapter)
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in content selection: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

async def show_lectures(client: Client, callback_query, batch_name: str, subject: str, teacher: str, chapter: str):
    """Show lecture options"""
    caption = f"""📚 **{batch_name.upper()}** - {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📖 **Content:** Lectures

📝 **Select lecture:**"""
    
    keyboard = []
    for i in range(1, 11):  # L01 to L10
        lecture_num = f"L{i:02d}"
        keyboard.append([InlineKeyboardButton(
            lecture_num, 
            callback_data=f"lecture_{batch_name}_{subject}_{teacher}_{chapter}_{lecture_num}"
        )])
    
    keyboard.extend([
        [InlineKeyboardButton("🔙 Back to Content", callback_data=f"chapter_{batch_name}_{subject}_{teacher}_{chapter}")],
        [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.edit_message_text(caption, reply_markup=reply_markup)

async def show_dpp(client: Client, callback_query, batch_name: str, subject: str, teacher: str, chapter: str):
    """Show DPP options"""
    caption = f"""📚 **{batch_name.upper()}** - {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📝 **Content:** DPP

📋 **Select DPP type:**"""
    
    keyboard = [
        [InlineKeyboardButton("📝 Quiz DPP", callback_data=f"dpp_quiz_{batch_name}_{subject}_{teacher}_{chapter}")],
        [InlineKeyboardButton("📄 PDF DPP", callback_data=f"dpp_pdf_{batch_name}_{subject}_{teacher}_{chapter}")],
        [InlineKeyboardButton("🔙 Back to Content", callback_data=f"chapter_{batch_name}_{subject}_{teacher}_{chapter}")],
        [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.edit_message_text(caption, reply_markup=reply_markup)

async def show_all_materials(client: Client, callback_query, batch_name: str, subject: str, teacher: str, chapter: str):
    """Show all study materials"""
    caption = f"""📚 **{batch_name.upper()}** - {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📚 **Content:** All Study Materials

📋 **Select material type:**"""
    
    materials = [
        "Mind Maps", "Revision", "Short Notes", "PYQs", 
        "KPP PDF", "KPP Solution", "Practice Sheet", 
        "Kattar NEET 2026", "IMPORTANT", "Handwritten Notes", "Module Question"
    ]
    
    keyboard = []
    for material in materials:
        keyboard.append([InlineKeyboardButton(
            material, 
            callback_data=f"material_{batch_name}_{subject}_{teacher}_{chapter}_{material.replace(' ', '_')}"
        )])
    
    keyboard.extend([
        [InlineKeyboardButton("🔙 Back to Content", callback_data=f"chapter_{batch_name}_{subject}_{teacher}_{chapter}")],
        [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.edit_message_text(caption, reply_markup=reply_markup)

# Handle lecture selection
@Client.on_callback_query(filters.regex(r"^lecture_"))
async def handle_lecture_selection(client: Client, callback_query):
    """Handle lecture selection and deliver content"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher, chapter, lecture = data.split("_", 5)
        
        # Here you would typically fetch the actual lecture file from content bot
        # For now, we'll show a placeholder message
        caption = f"""📚 **{batch_name.upper()}** - {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📖 **Lecture:** {lecture}

📝 **Content will be delivered by content bot**"""
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Lectures", callback_data=f"content_lectures_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await callback_query.edit_message_text(caption, reply_markup=reply_markup)
        
        # TODO: Implement content delivery from content bot
        await callback_query.answer("📚 Lecture content will be delivered!")
        
    except Exception as e:
        logger.error(f"Error in lecture selection: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle DPP selection
@Client.on_callback_query(filters.regex(r"^dpp_"))
async def handle_dpp_selection(client: Client, callback_query):
    """Handle DPP selection and deliver content"""
    try:
        data = callback_query.data
        _, dpp_type, batch_name, subject, teacher, chapter = data.split("_", 5)
        
        # Here you would typically fetch the actual DPP file from content bot
        content_type = "Quiz DPP" if dpp_type == "quiz" else "PDF DPP"
        
        caption = f"""📚 **{batch_name.upper()}** - {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📝 **Content:** {content_type}

📄 **Content will be delivered by content bot**"""
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to DPP", callback_data=f"content_dpp_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await callback_query.edit_message_text(caption, reply_markup=reply_markup)
        
        # TODO: Implement content delivery from content bot
        await callback_query.answer(f"📝 {content_type} will be delivered!")
        
    except Exception as e:
        logger.error(f"Error in DPP selection: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle material selection
@Client.on_callback_query(filters.regex(r"^material_"))
async def handle_material_selection(client: Client, callback_query):
    """Handle material selection and deliver content"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher, chapter, material = data.split("_", 5)
        
        # Convert material name back to readable format
        material_name = material.replace('_', ' ')
        
        # Here you would typically fetch the actual material file from content bot
        caption = f"""📚 **{batch_name.upper()}** - {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📚 **Material:** {material_name}

📄 **Content will be delivered by content bot**"""
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Materials", callback_data=f"content_all_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await callback_query.edit_message_text(caption, reply_markup=reply_markup)
        
        # TODO: Implement content delivery from content bot
        await callback_query.answer(f"📚 {material_name} will be delivered!")
        
    except Exception as e:
        logger.error(f"Error in material selection: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Navigation back buttons
@Client.on_callback_query(filters.regex(r"^back_"))
async def handle_back_navigation(client: Client, callback_query):
    """Handle back navigation"""
    try:
        data = callback_query.data
        parts = data.split("_")
        
        if parts[1] == "subjects":
            batch_name = parts[2]
            # Go back to batch selection
            await show_batch_selection(client, callback_query, batch_name)
            
        elif parts[1] == "teachers":
            batch_name, subject = parts[2], parts[3]
            # Go back to subject selection - create a mock callback query
            mock_callback = type('MockCallback', (), {
                'data': f"subject_{batch_name}_{subject}",
                'from_user': callback_query.from_user,
                'edit_message_text': callback_query.edit_message_text,
                'answer': callback_query.answer
            })()
            await handle_subject_selection(client, mock_callback)
            
        elif parts[1] == "format":
            batch_name, subject, teacher = parts[2], parts[3], parts[4]
            # Go back to teacher selection - create a mock callback query
            mock_callback = type('MockCallback', (), {
                'data': f"teacher_{batch_name}_{subject}_{teacher}",
                'from_user': callback_query.from_user,
                'edit_message_text': callback_query.edit_message_text,
                'answer': callback_query.answer
            })()
            await handle_teacher_selection(client, mock_callback)
            
        elif parts[1] == "chapters":
            batch_name, subject, teacher = parts[2], parts[3], parts[4]
            # Go back to teacher selection - create a mock callback query
            mock_callback = type('MockCallback', (), {
                'data': f"teacher_{batch_name}_{subject}_{teacher}",
                'from_user': callback_query.from_user,
                'edit_message_text': callback_query.edit_message_text,
                'answer': callback_query.answer
            })()
            await handle_teacher_selection(client, mock_callback)
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in back navigation: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

async def show_batch_selection(client: Client, callback_query, batch_name: str):
    """Show batch selection screen"""
    caption = f"""📚 **{batch_name.upper()}** 📚

🎯 **Welcome to your study journey!**

📖 **Available Subjects:**
• Physics
• Chemistry  
• Biology

👨‍🏫 **Teachers:**
• Mr Sir
• Saleem Sir

💡 **Select a subject to continue**"""
    
    keyboard = [
        [InlineKeyboardButton("🧪 Physics", callback_data=f"subject_{batch_name}_Physics")],
        [InlineKeyboardButton("⚗️ Chemistry", callback_data=f"subject_{batch_name}_Chemistry")],
        [InlineKeyboardButton("🧬 Biology", callback_data=f"subject_{batch_name}_Biology")],
        [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")],
        [InlineKeyboardButton("📊 Batch Stats", callback_data=f"batch_stats_{batch_name}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.edit_message_text(caption, reply_markup=reply_markup)

# Handle batch stats
@Client.on_callback_query(filters.regex(r"^batch_stats_"))
async def handle_batch_stats(client: Client, callback_query):
    """Handle batch statistics"""
    try:
        batch_name = callback_query.data.split("_")[2]
        
        # Get batch statistics from database
        # This would typically include user count, progress, etc.
        stats_text = f"📊 **{batch_name.upper()} Statistics**\n\n"
        stats_text += f"👥 **Active Users:** Calculating...\n"
        stats_text += f"📚 **Total Subjects:** 3\n"
        stats_text += f"👨‍🏫 **Total Teachers:** 2\n"
        stats_text += f"📖 **Total Chapters:** 20+\n"
        stats_text += f"📅 **Created:** Recently"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Batch", callback_data=f"back_subjects_{batch_name}")],
            [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await callback_query.edit_message_text(stats_text, reply_markup=reply_markup)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in batch stats: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Log when plugin loads
logger.info("PM Filter plugin loaded successfully")
