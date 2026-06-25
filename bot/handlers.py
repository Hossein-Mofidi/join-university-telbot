# bot/handlers.py
from telegram import Update
from telegram.ext import ContextTypes

from .services import join_service, verify_card_service

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Automatically asks for ID card upon chat join request."""
    join_request = update.chat_join_request
    await join_service(join_request, context)

async def handle_photo_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the submitted ID card photo in private chat."""
    await verify_card_service(update, context)