"""
Study Bot - Extra Plugin
Provides additional utility functions and features
"""

import asyncio
import random
import string
import time
import logging
from typing import Optional, List, Dict, Any
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMINS

logger = logging.getLogger(__name__)

# Utility functions
def generate_random_string(length: int = 8) -> str:
    """Generate random string"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_id() -> str:
    """Generate random ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

def format_time_duration(seconds: int) -> str:
    """Format time duration in human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """Create a progress bar string"""
    filled = int(length * current // total)
    bar = '█' * filled + '░' * (length - filled)
    percentage = current / total * 100
    return f"{bar} {percentage:.1f}%"

# Bot commands
@Client.on_message(filters.command("random") & filters.private)
async def random_command(client: Client, message: Message):
    """Generate random values"""
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text(
                "❌ **Usage:** `/random <type> [options]`\n\n"
                "**Types:**\n"
                "• `number <min> <max>` - Random number\n"
                "• `string <length>` - Random string\n"
                "• `choice <item1,item2,item3>` - Random choice\n"
                "• `password <length>` - Random password\n"
                "• `color` - Random color\n\n"
                "**Examples:**\n"
                "• `/random number 1 100`\n"
                "• `/random string 10`\n"
                "• `/random choice apple,banana,orange`"
            )
            return
        
        random_type = args[1].lower()
        
        if random_type == "number":
            if len(args) < 4:
                await message.reply_text("❌ **Usage:** `/random number <min> <max>`")
                return
            
            try:
                min_val = int(args[2])
                max_val = int(args[3])
                random_num = random.randint(min_val, max_val)
                
                await message.reply_text(
                    f"🎲 **Random Number**\n\n"
                    f"📊 **Range:** {min_val} to {max_val}\n"
                    f"🎯 **Result:** `{random_num}`"
                )
            except ValueError:
                await message.reply_text("❌ Invalid number range!")
        
        elif random_type == "string":
            length = 8
            if len(args) > 2:
                try:
                    length = int(args[2])
                    if length <= 0 or length > 100:
                        await message.reply_text("❌ Length must be between 1 and 100!")
                        return
                except ValueError:
                    await message.reply_text("❌ Invalid length!")
                    return
            
            random_str = generate_random_string(length)
            await message.reply_text(
                f"🔤 **Random String**\n\n"
                f"📏 **Length:** {length}\n"
                f"🎯 **Result:** `{random_str}`"
            )
        
        elif random_type == "choice":
            if len(args) < 3:
                await message.reply_text("❌ **Usage:** `/random choice <item1,item2,item3>`")
                return
            
            choices = args[2].split(',')
            if len(choices) < 2:
                await message.reply_text("❌ Please provide at least 2 choices!")
                return
            
            # Clean choices
            choices = [choice.strip() for choice in choices if choice.strip()]
            if len(choices) < 2:
                await message.reply_text("❌ Please provide at least 2 valid choices!")
                return
            
            random_choice = random.choice(choices)
            await message.reply_text(
                f"🎯 **Random Choice**\n\n"
                f"📋 **Options:** {', '.join(choices)}\n"
                f"🎯 **Result:** `{random_choice}`"
            )
        
        elif random_type == "password":
            length = 12
            if len(args) > 2:
                try:
                    length = int(args[2])
                    if length <= 0 or length > 50:
                        await message.reply_text("❌ Length must be between 1 and 50!")
                        return
                except ValueError:
                    await message.reply_text("❌ Invalid length!")
                    return
            
            # Generate password with mixed characters
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            password = ''.join(random.choice(chars) for _ in range(length))
            
            await message.reply_text(
                f"🔐 **Random Password**\n\n"
                f"📏 **Length:** {length}\n"
                f"🎯 **Result:** `{password}`\n\n"
                f"💡 **Note:** This is a secure random password."
            )
        
        elif random_type == "color":
            # Generate random hex color
            color = '#{:06x}'.format(random.randint(0, 0xFFFFFF))
            
            await message.reply_text(
                f"🎨 **Random Color**\n\n"
                f"🎯 **Hex Code:** `{color}`\n"
                f"🔢 **RGB:** {tuple(int(color[i:i+2], 16) for i in (1, 3, 5))}"
            )
        
        else:
            await message.reply_text("❌ Invalid random type! Use `number`, `string`, `choice`, `password`, or `color`.")
    
    except Exception as e:
        logger.error(f"Error in random command: {e}")
        await message.reply_text(f"❌ Error generating random value: {e}")

@Client.on_message(filters.command("timer") & filters.private)
async def timer_command(client: Client, message: Message):
    """Set a timer"""
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text(
                "⏰ **Timer Command**\n\n"
                "**Usage:** `/timer <seconds> [message]`\n\n"
                "**Examples:**\n"
                "• `/timer 60` - 1 minute timer\n"
                "• `/timer 300 Study break!` - 5 minutes with message\n"
                "• `/timer 3600` - 1 hour timer"
            )
            return
        
        try:
            seconds = int(args[1])
            if seconds <= 0:
                await message.reply_text("❌ Timer duration must be positive!")
                return
            
            if seconds > 86400:  # 24 hours
                await message.reply_text("❌ Timer duration cannot exceed 24 hours!")
                return
        except ValueError:
            await message.reply_text("❌ Invalid timer duration!")
            return
        
        # Get optional message
        timer_message = "⏰ Time's up!"
        if len(args) > 2:
            timer_message = ' '.join(args[2:])
        
        # Send timer start message
        start_msg = await message.reply_text(
            f"⏰ **Timer Started!**\n\n"
            f"⏱️ **Duration:** {format_time_duration(seconds)}\n"
            f"📝 **Message:** {timer_message}\n\n"
            f"⏳ Timer is running..."
        )
        
        # Wait for timer
        await asyncio.sleep(seconds)
        
        # Send timer completion message
        await start_msg.edit_text(
            f"🔔 **Timer Complete!**\n\n"
            f"⏱️ **Duration:** {format_time_duration(seconds)}\n"
            f"📝 **Message:** {timer_message}"
        )
        
        # Send notification
        await message.reply_text(f"🔔 **Timer Complete!** ⏰\n\n{timer_message}")
        
    except Exception as e:
        logger.error(f"Error in timer command: {e}")
        await message.reply_text(f"❌ Error setting timer: {e}")

@Client.on_message(filters.command("countdown") & filters.private)
async def countdown_command(client: Client, message: Message):
    """Start a countdown timer"""
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text(
                "⏰ **Countdown Command**\n\n"
                "**Usage:** `/countdown <seconds>`\n\n"
                "**Examples:**\n"
                "• `/countdown 60` - 1 minute countdown\n"
                "• `/countdown 300` - 5 minutes countdown"
            )
            return
        
        try:
            seconds = int(args[1])
            if seconds <= 0:
                await message.reply_text("❌ Countdown duration must be positive!")
                return
            
            if seconds > 3600:  # 1 hour max for countdown
                await message.reply_text("❌ Countdown duration cannot exceed 1 hour!")
                return
        except ValueError:
            await message.reply_text("❌ Invalid countdown duration!")
            return
        
        # Send countdown start message
        countdown_msg = await message.reply_text(
            f"⏰ **Countdown Started!**\n\n"
            f"⏱️ **Duration:** {format_time_duration(seconds)}\n\n"
            f"⏳ Starting countdown..."
        )
        
        # Run countdown
        for remaining in range(seconds, 0, -1):
            if remaining % 10 == 0 or remaining <= 10:  # Update every 10 seconds or last 10 seconds
                progress_bar = create_progress_bar(seconds - remaining, seconds)
                await countdown_msg.edit_text(
                    f"⏰ **Countdown Running!**\n\n"
                    f"⏱️ **Remaining:** {format_time_duration(remaining)}\n"
                    f"📊 **Progress:** {progress_bar}\n\n"
                    f"⏳ {remaining} seconds left..."
                )
            
            await asyncio.sleep(1)
        
        # Send completion message
        await countdown_msg.edit_text(
            f"🎉 **Countdown Complete!**\n\n"
            f"⏱️ **Duration:** {format_time_duration(seconds)}\n"
            f"📊 **Progress:** {create_progress_bar(seconds, seconds)}\n\n"
            f"🎊 Time's up!"
        )
        
        # Send notification
        await message.reply_text("🎉 **Countdown Complete!** ⏰")
        
    except Exception as e:
        logger.error(f"Error in countdown command: {e}")
        await message.reply_text(f"❌ Error starting countdown: {e}")

@Client.on_message(filters.command("quote") & filters.private)
async def quote_command(client: Client, message: Message):
    """Get random motivational quote"""
    quotes = [
        "🎯 **Success is not final, failure is not fatal: it is the courage to continue that counts.** - Winston Churchill",
        "🚀 **The only way to do great work is to love what you do.** - Steve Jobs",
        "💪 **Believe you can and you're halfway there.** - Theodore Roosevelt",
        "🌟 **The future belongs to those who believe in the beauty of their dreams.** - Eleanor Roosevelt",
        "📚 **Education is the most powerful weapon which you can use to change the world.** - Nelson Mandela",
        "🎓 **Learning is a treasure that will follow its owner everywhere.** - Chinese Proverb",
        "🔥 **The only limit to our realization of tomorrow is our doubts of today.** - Franklin D. Roosevelt",
        "🌈 **Don't watch the clock; do what it does. Keep going.** - Sam Levenson",
        "⚡ **The harder you work for something, the greater you'll feel when you achieve it.** - Unknown",
        "🎉 **Every expert was once a beginner.** - Robert T. Kiyosaki",
        "🧠 **The mind is not a vessel to be filled, but a fire to be kindled.** - Plutarch",
        "📖 **Education is not preparation for life; education is life itself.** - John Dewey",
        "🎯 **Set your goals high, and don't stop till you get there.** - Bo Jackson",
        "💡 **The only impossible journey is the one you never begin.** - Tony Robbins",
        "🚀 **Dream big and dare to fail.** - Norman Vaughan"
    ]
    
    random_quote = random.choice(quotes)
    await message.reply_text(f"💭 **Daily Motivation**\n\n{random_quote}")

@Client.on_message(filters.command("fact") & filters.private)
async def fact_command(client: Client, message: Message):
    """Get random interesting fact"""
    facts = [
        "🧠 **Brain Fact:** Your brain uses about 20% of your body's total energy, even though it only weighs about 2% of your body weight.",
        "🌍 **Earth Fact:** The Earth's core is as hot as the surface of the sun, reaching temperatures of up to 5,400°C (9,800°F).",
        "🐜 **Ant Fact:** Ants can lift objects up to 50 times their own body weight.",
        "🌊 **Ocean Fact:** The ocean contains 97% of Earth's water and covers 71% of the Earth's surface.",
        "🌙 **Moon Fact:** The Moon is moving away from Earth at a rate of about 3.8 centimeters per year.",
        "⚡ **Lightning Fact:** Lightning can reach temperatures of up to 30,000°C (54,000°F), which is five times hotter than the surface of the sun.",
        "🦒 **Giraffe Fact:** A giraffe's tongue is about 50 centimeters (20 inches) long and is blue-black in color.",
        "🌵 **Cactus Fact:** Some cacti can live for over 200 years.",
        "🦈 **Shark Fact:** Sharks have been around for about 400 million years, making them older than dinosaurs.",
        "🌺 **Flower Fact:** The world's largest flower, the Rafflesia arnoldii, can grow up to 3 feet in diameter and weigh up to 15 pounds."
    ]
    
    random_fact = random.choice(facts)
    await message.reply_text(f"🔍 **Random Fact**\n\n{random_fact}")

@Client.on_message(filters.command("joke") & filters.private)
async def joke_command(client: Client, message: Message):
    """Get random joke"""
    jokes = [
        "😄 **Why don't scientists trust atoms?** Because they make up everything!",
        "😂 **Why did the scarecrow win an award?** Because he was outstanding in his field!",
        "🤣 **What do you call a fake noodle?** An impasta!",
        "😆 **Why did the math book look so sad?** Because it had too many problems!",
        "😊 **What do you call a bear with no teeth?** A gummy bear!",
        "😋 **Why don't eggs tell jokes?** They'd crack each other up!",
        "😎 **What do you call a fish wearing a bowtie?** So-fish-ticated!",
        "🤪 **Why can't you give Elsa a balloon?** She will let it go!",
        "😜 **What do you call a dinosaur that crashes his car?** Tyrannosaurus wrecks!",
        "🤓 **Why did the student eat his homework?** Because the teacher said it was a piece of cake!"
    ]
    
    random_joke = random.choice(jokes)
    await message.reply_text(f"😄 **Random Joke**\n\n{random_joke}")

@Client.on_message(filters.command("tools") & filters.private)
async def tools_command(client: Client, message: Message):
    """Show available tools and utilities"""
    tools_text = "🛠️ **Available Tools & Utilities**\n\n"
    
    tools_text += "🎲 **Random Generators:**\n"
    tools_text += "• `/random number <min> <max>` - Random number\n"
    tools_text += "• `/random string <length>` - Random string\n"
    tools_text += "• `/random choice <items>` - Random choice\n"
    tools_text += "• `/random password <length>` - Random password\n"
    tools_text += "• `/random color` - Random color\n\n"
    
    tools_text += "⏰ **Timers:**\n"
    tools_text += "• `/timer <seconds> [message]` - Set timer\n"
    tools_text += "• `/countdown <seconds>` - Start countdown\n\n"
    
    tools_text += "💭 **Entertainment:**\n"
    tools_text += "• `/quote` - Random motivational quote\n"
    tools_text += "• `/fact` - Random interesting fact\n"
    tools_text += "• `/joke` - Random joke\n\n"
    
    tools_text += "🔧 **Other:**\n"
    tools_text += "• `/tools` - Show this help\n"
    tools_text += "• `/help` - General bot help\n"
    
    await message.reply_text(tools_text)

# Utility functions for other plugins
def get_random_quote() -> str:
    """Get a random motivational quote"""
    quotes = [
        "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "The only way to do great work is to love what you do.",
        "Believe you can and you're halfway there.",
        "The future belongs to those who believe in the beauty of their dreams.",
        "Education is the most powerful weapon which you can use to change the world."
    ]
    return random.choice(quotes)

def get_random_fact() -> str:
    """Get a random interesting fact"""
    facts = [
        "Your brain uses about 20% of your body's total energy.",
        "The Earth's core is as hot as the surface of the sun.",
        "Ants can lift objects up to 50 times their own body weight.",
        "The ocean contains 97% of Earth's water.",
        "Lightning can reach temperatures of up to 30,000°C."
    ]
    return random.choice(facts)

def get_random_joke() -> str:
    """Get a random joke"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "What do you call a fake noodle? An impasta!",
        "Why did the math book look so sad? Because it had too many problems!",
        "What do you call a bear with no teeth? A gummy bear!"
    ]
    return random.choice(jokes)

def create_simple_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Create a simple progress bar"""
    filled = int(length * current // total)
    bar = '█' * filled + '░' * (length - filled)
    return bar

def format_elapsed_time(start_time: float) -> str:
    """Format elapsed time since start"""
    elapsed = time.time() - start_time
    return format_time_duration(int(elapsed))
