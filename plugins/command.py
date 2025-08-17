import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.study_db import db, StudyFiles, Batches, Chapters, Users, StudySessions, ContentAnalytics, BotSettings, JoinRequests, Chats, GroupSettings
from config import *
from studybot.Bot import studybot, content_bot
import re

logger = logging.getLogger(__name__)

# Handle lectures content selection
@studybot.on_callback_query(filters.regex(r"^content_lectures_"))
async def handle_lectures_content(client: Client, callback_query):
    """Handle lectures content selection"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher, chapter = data.split("_", 4)
        
        user_id = callback_query.from_user.id
        
        # Update user's current content type
        user = await Users.find_one({"_id": user_id})
        if user:
            user.current_content_type = "Lectures"
            await user.commit()
        
        # Create lecture buttons (L01, L02, L03, etc.)
        caption = f"""📚 **{batch_name.upper()}** - {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📖 **Content Type:** Lectures

🎯 **Select Lecture:**"""
        
        keyboard = []
        for i in range(1, 16):  # L01 to L15
            lecture_num = f"L{i:02d}"
            keyboard.append([InlineKeyboardButton(
                lecture_num, 
                callback_data=f"lecture_{batch_name}_{subject}_{teacher}_{chapter}_{lecture_num}"
            )])
        
        # Add navigation and other buttons
        keyboard.extend([
            [InlineKeyboardButton("🔙 Back to Content Types", callback_data=f"back_content_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(caption, reply_markup=reply_markup)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in lectures content: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle DPP content selection
@studybot.on_callback_query(filters.regex(r"^content_dpp_"))
async def handle_dpp_content(client: Client, callback_query):
    """Handle DPP content selection"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher, chapter = data.split("_", 4)
        
        user_id = callback_query.from_user.id
        
        # Update user's current content type
        user = await Users.find_one({"_id": user_id})
        if user:
            user.current_content_type = "DPP"
            await user.commit()
        
        # Create DPP selection buttons
        caption = f"""📚 **{batch_name.upper()}** - {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📝 **Content Type:** DPP

🎯 **Select DPP Type:**"""
        
        keyboard = [
            [InlineKeyboardButton("📝 Quiz DPP", callback_data=f"dpp_quiz_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("📄 PDF DPP", callback_data=f"dpp_pdf_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("🔙 Back to Content Types", callback_data=f"back_content_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(caption, reply_markup=reply_markup)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in DPP content: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle ALL STUDY MATERIALS content selection
@studybot.on_callback_query(filters.regex(r"^content_all_"))
async def handle_all_study_materials(client: Client, callback_query):
    """Handle ALL STUDY MATERIALS content selection"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher, chapter = data.split("_", 4)
        
        user_id = callback_query.from_user.id
        
        # Update user's current content type
        user = await Users.find_one({"_id": user_id})
        if user:
            user.current_content_type = "ALL STUDY MATERIALS"
            await user.commit()
        
        # Create all study materials buttons (12 buttons as requested)
        caption = f"""📚 **{batch_name.upper()}** - {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📚 **Content Type:** ALL STUDY MATERIALS

🎯 **Select Study Material:**"""
        
        keyboard = [
            [InlineKeyboardButton("🧠 Mind Maps", callback_data=f"material_mindmaps_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("📖 Revision", callback_data=f"material_revision_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("📝 Short Notes", callback_data=f"material_shortnotes_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("❓ PYQs", callback_data=f"material_pyqs_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("📄 KPP PDF", callback_data=f"material_kpppdf_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("📋 KPP Solution", callback_data=f"material_kppsolution_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("📝 Practice Sheet", callback_data=f"material_practicesheet_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("🎯 Kattar NEET 2026", callback_data=f"material_kattarneet_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("⭐ IMPORTANT", callback_data=f"material_important_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("✍️ Handwritten Notes", callback_data=f"material_handwritten_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("📚 Module Question", callback_data=f"material_module_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("🔙 Back to Content Types", callback_data=f"back_content_{batch_name}_{subject}_{teacher}_{chapter}")],
            [InlineKeyboardButton("🎁 Surprise Here!", url="https://t.me/your_channel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await callback_query.edit_message_text(caption, reply_markup=reply_markup)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in all study materials: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle individual lecture selection
@studybot.on_callback_query(filters.regex(r"^lecture_"))
async def handle_individual_lecture(client: Client, callback_query):
    """Handle individual lecture selection and deliver content"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher, chapter, lecture_num = data.split("_", 5)
        
        user_id = callback_query.from_user.id
        
        # Log the lecture request
        logger.info(f"User {user_id} requested lecture {lecture_num} for {batch_name} - {subject} - {teacher} - {chapter}")
        
        # Send confirmation message
        await callback_query.edit_message_text(
            f"""✅ **Lecture Requested Successfully!**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📖 **Lecture:** {lecture_num}

📤 **Your lecture is being sent to the Content Bot...**
Please check your Content Bot for the file."""
        )
        
        # Send the lecture file from content bot
        try:
            # Find the lecture file in database
            file_query = {
                "batch_name": batch_name,
                "subject": subject,
                "teacher": teacher,
                "chapter_no": chapter,
                "content_type": "Lectures",
                "file_name": {"$regex": f"{lecture_num}", "$options": "i"}
            }
            
            study_file = await StudyFiles.find_one(file_query)
            
            if study_file:
                # Send file from content bot
                await content_bot.send_message(
                    user_id,
                    f"""📖 **Here's your requested lecture:**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📖 **Lecture:** {lecture_num}

📄 **File:** {study_file.file_name}
📏 **Size:** {get_file_size(study_file.file_size)}
📅 **Uploaded:** {study_file.uploaded_at.strftime('%Y-%m-%d %H:%M')}

💡 **Note:** This file is sent from the Content Bot."""
                )
                
                # Update user statistics
                user = await Users.find_one({"_id": user_id})
                if user:
                    user.total_downloads += 1
                    user.last_active = datetime.utcnow()
                    
                    # Update study progress
                    progress_key = f"{batch_name}.{subject}.{chapter}"
                    if not user.study_progress:
                        user.study_progress = {}
                    if progress_key not in user.study_progress:
                        user.study_progress[progress_key] = {}
                    if "Lectures" not in user.study_progress[progress_key]:
                        user.study_progress[progress_key]["Lectures"] = 0
                    user.study_progress[progress_key]["Lectures"] += 1
                    
                    await user.commit()
                
                logger.info(f"Lecture {lecture_num} sent successfully to user {user_id}")
                
            else:
                # File not found, send placeholder
                await content_bot.send_message(
                    user_id,
                    f"""❌ **Lecture Not Found**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📖 **Lecture:** {lecture_num}

⚠️ **This lecture file is not available in the database yet.**
Please contact the bot admin to upload this content."""
                )
                
        except Exception as e:
            logger.error(f"Error sending lecture file: {e}")
            await content_bot.send_message(
                user_id,
                f"""❌ **Error Sending Lecture**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📖 **Lecture:** {lecture_num}

⚠️ **An error occurred while sending the file.**
Please try again or contact support."""
            )
        
        await callback_query.answer("✅ Lecture requested successfully!")
        
    except Exception as e:
        logger.error(f"Error in individual lecture: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle DPP Quiz selection
@studybot.on_callback_query(filters.regex(r"^dpp_quiz_"))
async def handle_dpp_quiz(client: Client, callback_query):
    """Handle DPP Quiz selection and deliver content"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher, chapter = data.split("_", 4)
        
        user_id = callback_query.from_user.id
        
        # Log the DPP Quiz request
        logger.info(f"User {user_id} requested DPP Quiz for {batch_name} - {subject} - {teacher} - {chapter}")
        
        # Send confirmation message
        await callback_query.edit_message_text(
            f"""✅ **DPP Quiz Requested Successfully!**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📝 **Content:** Quiz DPP

📤 **Your Quiz DPP is being sent to the Content Bot...**
Please check your Content Bot for the file."""
        )
        
        # Send the Quiz DPP from content bot
        try:
            # Find the Quiz DPP file in database
            file_query = {
                "batch_name": batch_name,
                "subject": subject,
                "teacher": teacher,
                "chapter_no": chapter,
                "content_type": "DPP Quiz"
            }
            
            study_file = await StudyFiles.find_one(file_query)
            
            if study_file:
                # Send file from content bot
                await content_bot.send_message(
                    user_id,
                    f"""📝 **Here's your requested Quiz DPP:**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📝 **Content:** Quiz DPP

📄 **File:** {study_file.file_name}
📏 **Size:** {get_file_size(study_file.file_size)}
📅 **Uploaded:** {study_file.uploaded_at.strftime('%Y-%m-%d %H:%M')}

💡 **Note:** This file is sent from the Content Bot."""
                )
                
                # Update user statistics
                user = await Users.find_one({"_id": user_id})
                if user:
                    user.total_downloads += 1
                    user.last_active = datetime.utcnow()
                    
                    # Update study progress
                    progress_key = f"{batch_name}.{subject}.{chapter}"
                    if not user.study_progress:
                        user.study_progress = {}
                    if progress_key not in user.study_progress:
                        user.study_progress[progress_key] = {}
                    if "DPP Quiz" not in user.study_progress[progress_key]:
                        user.study_progress[progress_key]["DPP Quiz"] = 0
                    user.study_progress[progress_key]["DPP Quiz"] += 1
                    
                    await user.commit()
                
                logger.info(f"DPP Quiz sent successfully to user {user_id}")
                
            else:
                # File not found, send placeholder
                await content_bot.send_message(
                    user_id,
                    f"""❌ **Quiz DPP Not Found**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📝 **Content:** Quiz DPP

⚠️ **This Quiz DPP file is not available in the database yet.**
Please contact the bot admin to upload this content."""
                )
                
        except Exception as e:
            logger.error(f"Error sending DPP Quiz file: {e}")
            await content_bot.send_message(
                user_id,
                f"""❌ **Error Sending Quiz DPP**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📝 **Content:** Quiz DPP

⚠️ **An error occurred while sending the file.**
Please try again or contact support."""
            )
        
        await callback_query.answer("✅ Quiz DPP requested successfully!")
        
    except Exception as e:
        logger.error(f"Error in DPP Quiz: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle DPP PDF selection
@studybot.on_callback_query(filters.regex(r"^dpp_pdf_"))
async def handle_dpp_pdf(client: Client, callback_query):
    """Handle DPP PDF selection and deliver content"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher, chapter = data.split("_", 4)
        
        user_id = callback_query.from_user.id
        
        # Log the DPP PDF request
        logger.info(f"User {user_id} requested DPP PDF for {batch_name} - {subject} - {teacher} - {chapter}")
        
        # Send confirmation message
        await callback_query.edit_message_text(
            f"""✅ **DPP PDF Requested Successfully!**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📄 **Content:** PDF DPP

📤 **Your PDF DPP is being sent to the Content Bot...**
Please check your Content Bot for the file."""
        )
        
        # Send the PDF DPP from content bot
        try:
            # Find the PDF DPP file in database
            file_query = {
                "batch_name": batch_name,
                "subject": subject,
                "teacher": teacher,
                "chapter_no": chapter,
                "content_type": "DPP PDF"
            }
            
            study_file = await StudyFiles.find_one(file_query)
            
            if study_file:
                # Send file from content bot
                await content_bot.send_message(
                    user_id,
                    f"""📄 **Here's your requested PDF DPP:**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📄 **Content:** PDF DPP

📄 **File:** {study_file.file_name}
📏 **Size:** {get_file_size(study_file.file_size)}
📅 **Uploaded:** {study_file.uploaded_at.strftime('%Y-%m-%d %H:%M')}

💡 **Note:** This file is sent from the Content Bot."""
                )
                
                # Update user statistics
                user = await Users.find_one({"_id": user_id})
                if user:
                    user.total_downloads += 1
                    user.last_active = datetime.utcnow()
                    
                    # Update study progress
                    progress_key = f"{batch_name}.{subject}.{chapter}"
                    if not user.study_progress:
                        user.study_progress = {}
                    if progress_key not in user.study_progress:
                        user.study_progress[progress_key] = {}
                    if "DPP PDF" not in user.study_progress[progress_key]:
                        user.study_progress[progress_key]["DPP PDF"] = 0
                    user.study_progress[progress_key]["DPP PDF"] += 1
                    
                    await user.commit()
                
                logger.info(f"DPP PDF sent successfully to user {user_id}")
                
            else:
                # File not found, send placeholder
                await content_bot.send_message(
                    user_id,
                    f"""❌ **PDF DPP Not Found**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📄 **Content:** PDF DPP

⚠️ **This PDF DPP file is not available in the database yet.**
Please contact the bot admin to upload this content."""
                )
                
        except Exception as e:
            logger.error(f"Error sending DPP PDF file: {e}")
            await content_bot.send_message(
                user_id,
                f"""❌ **Error Sending PDF DPP**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📄 **Content:** PDF DPP

⚠️ **An error occurred while sending the file.**
Please try again or contact support."""
            )
        
        await callback_query.answer("✅ PDF DPP requested successfully!")
        
    except Exception as e:
        logger.error(f"Error in DPP PDF: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle study material selection (generic handler for all materials)
@studybot.on_callback_query(filters.regex(r"^material_"))
async def handle_study_material(client: Client, callback_query):
    """Handle study material selection and deliver content"""
    try:
        data = callback_query.data
        _, material_type, batch_name, subject, teacher, chapter = data.split("_", 5)
        
        user_id = callback_query.from_user.id
        
        # Map material types to display names
        material_names = {
            "mindmaps": "Mind Maps",
            "revision": "Revision",
            "shortnotes": "Short Notes",
            "pyqs": "PYQs",
            "kpppdf": "KPP PDF",
            "kppsolution": "KPP Solution",
            "practicesheet": "Practice Sheet",
            "kattarneet": "Kattar NEET 2026",
            "important": "IMPORTANT",
            "handwritten": "Handwritten Notes",
            "module": "Module Question"
        }
        
        material_name = material_names.get(material_type, material_type.title())
        
        # Log the material request
        logger.info(f"User {user_id} requested {material_name} for {batch_name} - {subject} - {teacher} - {chapter}")
        
        # Send confirmation message
        await callback_query.edit_message_text(
            f"""✅ **{material_name} Requested Successfully!**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📚 **Content:** {material_name}

📤 **Your {material_name} is being sent to the Content Bot...**
Please check your Content Bot for the content."""
        )
        
        # Send the material from content bot
        try:
            # Find the material file in database
            file_query = {
                "batch_name": batch_name,
                "subject": subject,
                "teacher": teacher,
                "chapter_no": chapter,
                "content_type": material_name
            }
            
            study_file = await StudyFiles.find_one(file_query)
            
            if study_file:
                # Send file from content bot
                await content_bot.send_message(
                    user_id,
                    f"""📚 **Here's your requested {material_name}:**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📚 **Content:** {material_name}

📄 **File:** {study_file.file_name}
📏 **Size:** {get_file_size(study_file.file_size)}
📅 **Uploaded:** {study_file.uploaded_at.strftime('%Y-%m-%d %H:%M')}

💡 **Note:** This file is sent from the Content Bot."""
                )
                
                # Update user statistics
                user = await Users.find_one({"_id": user_id})
                if user:
                    user.total_downloads += 1
                    user.last_active = datetime.utcnow()
                    
                    # Update study progress
                    progress_key = f"{batch_name}.{subject}.{chapter}"
                    if not user.study_progress:
                        user.study_progress = {}
                    if progress_key not in user.study_progress:
                        user.study_progress[progress_key] = {}
                    if material_name not in user.study_progress[progress_key]:
                        user.study_progress[progress_key][material_name] = 0
                    user.study_progress[progress_key][material_name] += 1
                    
                    await user.commit()
                
                logger.info(f"{material_name} sent successfully to user {user_id}")
                
            else:
                # File not found, send placeholder
                await content_bot.send_message(
                    user_id,
                    f"""❌ **{material_name} Not Found**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📚 **Content:** {material_name}

⚠️ **This {material_name} file is not available in the database yet.**
Please contact the bot admin to upload this content."""
                )
                
        except Exception as e:
            logger.error(f"Error sending {material_name} file: {e}")
            await content_bot.send_message(
                user_id,
                f"""❌ **Error Sending {material_name}**

📚 **Batch:** {batch_name.upper()}
🧪 **Subject:** {subject}
👨‍🏫 **Teacher:** {teacher}
📖 **Chapter:** {chapter}
📚 **Content:** {material_name}

⚠️ **An error occurred while sending the file.**
Please try again or contact support."""
            )
        
        await callback_query.answer(f"✅ {material_name} requested successfully!")
        
    except Exception as e:
        logger.error(f"Error in study material: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Handle back navigation to content types
@studybot.on_callback_query(filters.regex(r"^back_content_"))
async def handle_back_to_content_types(client: Client, callback_query):
    """Handle back navigation to content types"""
    try:
        data = callback_query.data
        _, batch_name, subject, teacher, chapter = data.split("_", 4)
        
        # Go back to chapter selection
        await handle_chapter_selection(client, callback_query)
        
    except Exception as e:
        logger.error(f"Error in back to content types: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Utility function for file size formatting
def get_file_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

# Log when plugin loads
logger.info("Command plugin loaded successfully")
