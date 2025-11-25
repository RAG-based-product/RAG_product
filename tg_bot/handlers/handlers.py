from telegram import Update

from telegram.ext import ContextTypes

from utils import get_model, get_prompt


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(
        f'Привет {user.first_name}! Я бот, работающий c MistralAI!'
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    llm = get_model()
    user_content = update.message.text
    prompt = get_prompt(user_content)
    res = llm.invoke(prompt)
    # print(res.content)
    ans =  res.content

    await context.bot.send_message(chat_id=update.effective_chat.id, text=ans)