import ta
import telebot
from datetime import datetime
from time import sleep

from config import *

class Utils(object):
    
    def __init__(self, bot):
        self.tg = telebot.TeleBot(telegram)
        self.bot = bot
    
    def send(self, text):
        self.tg.send_message(channel_id, text)
