from telegram.ext import Application, ChatJoinRequestHandler, MessageHandler, filters

import settings
from bot.handlers import handle_join_request, handle_photo_submission
from database import init_db

init_db()

app = Application.builder().token(settings.TOKEN).build()

app.add_handler(
    ChatJoinRequestHandler(handle_join_request)
)

app.add_handler(
    MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, handle_photo_submission)
)

print("Bot is running...")
app.run_polling()