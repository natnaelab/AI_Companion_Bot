from dataclasses import dataclass
from telegram.ext import (
    CallbackContext,
    ExtBot,
    Application,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram import Update
from telegram.constants import ParseMode, ChatAction
from workersai import dreamshaper_8_lcm, llama2_7b_chat_fp16, whisper
from io import BytesIO
import os


@dataclass
class WebhookUpdate:
    user_id: int
    payload: str


class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):
    @classmethod
    def from_update(
        cls,
        update: object,
        application: "Application",
    ) -> "CustomContext":
        if isinstance(update, WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)


async def start(update: Update, _):
    """Handler for /start command"""
    text = """👋 Hi there!

Feel free to send me any text messages, and I'll do my best to respond. You can also use the <code>/imagine</code> command followed by a prompt to generate images, or send me voice messages to chat.
"""
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def chat(update: Update, _):
    """Handler for all text messages."""
    await update.message.reply_chat_action(ChatAction.TYPING)

    try:
        response = await llama2_7b_chat_fp16(update.message.text)
        text = response.get("result", {}).get("response", "Something went wrong...")
    except Exception as e:
        text = str(e)

    await update.message.reply_text(text, reply_to_message_id=update.message.message_id)


async def voice_chat(update: Update, context: CustomContext):
    """Handler for voice messages"""
    await update.message.reply_chat_action(ChatAction.TYPING)
    voice_file = await context.bot.getFile(update.message.voice.file_id)
    memory_voice = BytesIO()
    await voice_file.download_to_memory(memory_voice)

    memory_voice.seek(0)
    try:
        transcription = await whisper(memory_voice)
        response = await llama2_7b_chat_fp16(transcription)
    except Exception as e:
        return await update.message.reply_text(
            str(e), reply_to_message_id=update.message.message_id
        )

    text = response.get("result", {}).get("response", "Something went wrong...")
    await update.message.reply_text(text, reply_to_message_id=update.message.message_id)


async def imagine(update: Update, _):
    """handler /imagine command for generating images"""
    await update.message.reply_chat_action(ChatAction.UPLOAD_PHOTO)

    prompt = " ".join(update.message.text.split()[1:])

    try:
        response = await dreamshaper_8_lcm(prompt)

        await update.message.reply_photo(
            response,
            caption=f"`{prompt}`",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_to_message_id=update.message.message_id,
        )
    except Exception as e:
        await update.message.reply_text(str(e))


context_types = ContextTypes(context=CustomContext)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize telegram bot
bot_app = (
    Application.builder()
    .token(TELEGRAM_BOT_TOKEN)
    .updater(None)
    .context_types(context_types)
    .build()
)


# Update handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("imagine", imagine))
bot_app.add_handler(MessageHandler(filters.TEXT, chat))
bot_app.add_handler(MessageHandler(filters.VOICE, voice_chat))
