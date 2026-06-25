import os

import pytesseract

from PIL import Image
from telegram import ChatJoinRequest, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import settings
from database import save_student, check_student_joined
from settings import STUDENT_INFO


async def join_service(join_request: ChatJoinRequest, context: ContextTypes.DEFAULT_TYPE):
    user = join_request.from_user
    chat = join_request.chat

    print(f'Received join request from {user.first_name} for {chat.title}')

    context.user_data['state'] = 'send_card'
    context.user_data['pending_group_id'] = chat.id

    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=f"""
            سلام {user.first_name}! برای عضویت در گروه *{chat.title}* لطفا عکس *کارت دانشجویی* خودتون رو به صورت *HD* ارسال کنید.
            \nدقت کنید که فقط کارت در عکس مشخص باشه(اگر نیست حتما تصویر رو *کراپ* کنید) و حالت عکس روی *SD* نبوده و روی *HD* باشه
            """,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as e:
        print(f'Could not send PM to user (they might not have started the bot): {e}')


async def verify_card_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    state = context.user_data.get('state')
    pending_group_id = context.user_data.get('pending_group_id')

    if state != 'send_card' or not pending_group_id:
        await context.bot.send_message(text='لطفا دوباره درخواست عضویت بدید.')

    # get the best resolution photo
    photo = update.message.photo[-1]
    photo_file = await context.bot.get_file(photo.file_id)

    # save image in drive
    path = f'photos/{pending_group_id}'
    os.makedirs(path, exist_ok=True)

    image = await photo_file.download_to_drive(f'{path}/{user.id}.jpg')

    # extract text from image
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    photo_info = pytesseract.image_to_string(Image.open(image), lang='fas')

    # extract information from text
    st_info = {}
    for info in photo_info.split('\n'):
        print(info)
        try:
            field, val = info.split(':')
            st_info[field] = val
        except:
            continue

    # check if information is valid
    is_card_valid = False
    if set(st_info.keys()) == set(STUDENT_INFO.values()):
        st_info = {
            key: st_info[value].strip()
            for key, value in STUDENT_INFO.items()
        }
        if st_info.get('field') == settings.FIELD and not check_student_joined(st_info.get('st_number')):
            is_card_valid = True

    if is_card_valid:
        save_student(
            user_id=user.id,
            username=user.username,
            group_id=pending_group_id,
            **st_info
        )

        try:
            await context.bot.approve_chat_join_request(
                chat_id=pending_group_id,
                user_id=user.id
            )
            await update.message.reply_text('کارت دانشجویی شما تایید شد! ✅\nبه گروه اضافه شدید.')
        except Exception as e:
            print(f'Error approving join request: {e}')
            await update.message.reply_text('مشکلی در اضافه کردن شما به گروه پیش آمد.')

    else:
        await context.bot.decline_chat_join_request(
            chat_id=pending_group_id,
            user_id=user.id
        )
        await update.message.reply_text('کارت دانشجویی شما تایید نشد. ❌ درخواست شما رد شد.')

    context.user_data.clear()