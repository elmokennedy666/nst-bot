import os
import telebot
import torch
from flask import Flask, request
from telebot import types
import time
from transforming_functions import run_style_transfer, cnn_normalization_std, cnn_normalization_mean, unload, \
    image_loader
from settings import TOKEN, URL

def start():
    bot = telebot.TeleBot(TOKEN, threaded=False)
    server = Flask(__name__)
    id = {}
    cnn = torch.load('m.pth')

    @server.route('/' + TOKEN, methods=['POST'])
    def get_message():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200

    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url = URL + TOKEN)
        return "!", 200

    @bot.message_handler(commands=['start'])
    def command_start(message):
        bot.send_message(message.chat.id, bot_start_text, reply_markup=types.ReplyKeyboardRemove())

    @bot.message_handler(commands=['help'])
    def command_help(message):
        bot.send_message(message.chat.id, bot_help, reply_markup=types.ReplyKeyboardRemove())

    bot_start_text = '''
    Hello!
    I can transfer style from one image to another! \n
    
    Send me 2 pictures and i wll show you the result!
    
    Other functions is /help, /transform
    
    '''

    bot_help = '''
    
    Send me 2 pictures in 1 message, using /transform command
    
    I will transform style from style picture to content picture!
    
    '''

    bot_start_transform = _text = '''
    
    Hello! At first send me style image and then content image!
    
    
    '''

    bot_content = '''
    
    i got style image, now send me content image! 
    
    '''

    bot_transfer_text = '''
    I started transforming! \n
    Please, wait a couple of minutes, \n
    I will send you transformed image, when it wll be ready!
    '''


    @bot.message_handler(commands=['transform'])
    def transform(message):
        id[message.chat.id] = {'started': True, 'style': False, 'content': False}
        bot.send_message(message.chat.id, bot_start_transform)

    @bot.message_handler(content_types=['photo'])
    def get_image(message):
        # check user id
        if message.chat.id in id:
            if not id[message.chat.id]['style']:
                id[message.chat.id]['style'] = message.photo[-1].file_id
                bot.send_message(message.chat.id, bot_content)
            elif not id[message.chat.id]['content']:
                id[message.chat.id]['content'] = message.photo[-1].file_id
                save_image(message.chat.id, id[message.chat.id]['style'], '_style.jpg')
                save_image(message.chat.id, id[message.chat.id]['content'], '_content.jpg')
                content_img = image_loader(str(message.chat.id) + '_content.jpg')
                input_img = image_loader(str(message.chat.id) + '_content.jpg')
                style_img = image_loader(str(message.chat.id) + '_style.jpg')
                bot.send_message(message.chat.id, bot_transfer_text)
                transformed_image = run_style_transfer(cnn, cnn_normalization_mean, cnn_normalization_std, style_img,
                                                       content_img, input_img, 150)
                time.sleep(30)
                unload(transformed_image).save(str(message.chat.id) + '_transformed.jpg')
                with open(str(message.chat.id) + '_transformed.jpg', 'rb') as file_transfer:
                    bot.send_photo(message.chat.id, file_transfer)

    def save_image(id, file_id, name):
        image = bot.get_file(file_id)
        with open(str(id) + name, 'wb') as file_save:
            file_save.write(bot.download_file(image.file_path))

    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
