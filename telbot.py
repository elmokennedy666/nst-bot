import os
import telebot
import torch
from flask import Flask, request
from telebot import types

from transforming_functions import run_style_transfer, cnn_normalization_std, cnn_normalization_mean, unload, image_loader


def start():
    bot = telebot.TeleBot('1393457415:AAGHThyEYg1-uLpRXsgN31koxDAI62d6vXM', threaded=False)
    server = Flask(__name__)
    id = {}

    @server.route('/' + '1393457415:AAGHThyEYg1-uLpRXsgN31koxDAI62d6vXM', methods=['POST'])
    def get_message():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200

    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url='https://nst-bot.herokuapp.com/' + '1393457415:AAGHThyEYg1-uLpRXsgN31koxDAI62d6vXM')
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
    
    '''

    bot_help = '''
    
    Send me 2 pictures in 1 message
    
    I will transform style from style picture to content picture!
    
    '''

    bot_transfer_text = '''
    I started transforming! \n
    Please, wait a couple of minutes, \n
    I will send you transformed image, when it wll be ready!
    '''
    '''
    @bot.message_handler(content_types=['photo'])
    def get_img(message):
        style_file_id, content_file_id = message.photo[-2].file_id, message.photo[-1].file_id
        bot.send_message(message.chat.id, bot_transfer_text)
        save_image(message.chat.id, style_file_id, '_style.jpg')
        save_image(message.chat.id, content_file_id, '_content.jpg')
        style_img = image_loader(str(message.chat.id) + '_style.jpg')
        content_img = image_loader(str(message.chat.id) + '_content.jpg')
        input_img = image_loader(str(message.chat.id) + '_content.jpg')
        cnn = torch.load('m.pth')
        transformed_image = run_style_transfer(cnn, cnn_normalization_mean, cnn_normalization_std, style_img, content_img, input_img, 200)
        import time
        time.sleep(100)
        unload(transformed_image).save(str(message.chat.id) + '_transformed.jpg')
        with open(str(message.chat.id) + '_transformed.jpg', 'rb') as file_read:
            bot.send_photo(message.chat.id, file_read)
    '''
    @bot.message_handler(content_types=['photo'])
    def get_image(message):
        #check user id
        if message.chat.id in id:
            if not id[message.chat.id]['style']:
                id[message.chat.id]['style'] = message.photo[-1].file_id
                style_img = id[message.chat.id]['style']

            elif not id[message.chat.id]['content']:
                id[message.chat.id]['content'] = message.photo[-1].file_id
                content_img = id[message.chat.id]['content']
                input_img = id[message.chat.id]['content']

            cnn = torch.load('m.pth')
                #bot.send_message(message.chat.id, 'Transfer started, wait ~1 min')
            transformed_image = run_style_transfer(cnn, cnn_normalization_mean, cnn_normalization_std, style_img,
                                                       content_img, input_img, 200)
            unload(transformed_image).save(str(message.chat.id) + '_transformed.jpg')
            with open(str(message.chat.id) + '_transformed.jpg', 'rb') as f:
                bot.send_photo(message.chat.id, f)

    def save_image(id, file_id, name):
        image = bot.get_file(file_id)
        with open(str(id) + name, 'wb') as file_style:
            file_style.write(bot.download_file(image.file_path))


    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

