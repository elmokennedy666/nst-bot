import telebot
import torchvision
from ipywidgets import IntSlider, Output
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import matplotlib.pyplot as plt
from PIL import Image
import torchvision.transforms as transforms
import torchvision.models as models
import copy
import datetime
import requests
import urllib.request
import subprocess
import os
from os import environ
from telebot import types
from transforming_functions import run_style_transfer, cnn_normalization_std, cnn_normalization_mean, content_layers_default, loader, unload, image_loader
import heroku


bot = telebot.TeleBot('1155891195:AAF4_6_WxZSLOzIoE8WaU8X1pntM8zpSmg4')

@bot.message_handler(commands=['start'])
def command_start(message):
    bot.send_message(message.chat.id, bot_start_text, reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['help'])
def command_help(message):
    bot.send_message(message.chat.id, bot_help, reply_markup=types.ReplyKeyboardRemove())

image = {}


bot_start_text = '''
Hello!
I can transfer style from one image to another! \n

Send me 2 pictures and i wll show you the result!

'''

bot_help = '''

You can use command /style to send style image \n

And command /content to send content image \n

I will transform style from style picture to content picture!

'''

bot_transfer_text = '''
I started transforming! \n
Please, wait a couple of minutes, \n
I will send you transformed image, when it wll be ready!
'''

@bot.message_handler(content_types=['photo'])
def get_img(message):
    #print(message)
    style_file_id, content_file_id = message.photo[-2].file_id, message.photo[-1].file_id
    bot.send_message(message.chat.id, bot_transfer_text)
    save_image(message.chat.id, style_file_id, '_style.jpg')
    save_image(message.chat.id, content_file_id, '_content.jpg')
    style_img = image_loader(str(message.chat.id) + '_style.jpg')
    content_img = image_loader(str(message.chat.id) + '_content.jpg')
    input_img = image_loader(str(message.chat.id) + '_content.jpg')
    cnn = torch.load('m.pth')
    transformed_image = run_style_transfer(cnn, cnn_normalization_mean, cnn_normalization_std, style_img, content_img, input_img, 50)
    unload(transformed_image).save(str(message.chat.id) + '_transformed.jpg')
    with open(str(message.chat.id) + '_transformed.jpg', 'rb') as file_read:
        bot.send_photo(message.chat.id, file_read)
    #remove_data(message.chat.id)


def save_image(id, file_id, name):
    image = bot.get_file(file_id)
    with open(str(id) + name, 'wb') as file_style:
        file_style.write(bot.download_file(image.file_path))



#def remove_data(id):
#    for i in ['_content.jpg', '_style.jpg', '_transformed.jpg']:
#        os.remove(str(id) + i)
 #   del image[id]




bot.polling()



