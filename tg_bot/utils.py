from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
import os
from telegram.ext import ApplicationBuilder

def get_application():
    load_dotenv(".env")
    TOKEN = os.environ.get("soft_code_fix_bot_key")
    
    application = ApplicationBuilder().token(TOKEN).build()

    return application

# def get_model():
#     # TODO:


#     return llm


