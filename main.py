import telebot
from telebot import types
import sqlite3
from sqlite3 import Error
from random import randint

bot = telebot.TeleBot("1872431011:AAH_kELBADL1MDa-B9YibVPXtAhDYIkAj6o", parse_mode=None)

target_age = '18-25'
target_price = 'cheap'
target_brand = 'None'
target_type = 'None'

def get_sql_query(sql_query):
    with sqlite3.connect('db/cosmetics.sqlite3', check_same_thread=False) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(sql_query)
        except Error:
            raise
        result = cursor.fetchall()
        print(result)
        return result

def show_ages():
    select_query = 'select * from selectCosmetics_ages'
    return [item[1] for item in get_sql_query(select_query)]

def show_prices():
    select_query = 'select * from selectCosmetics_prices'
    return [item[1] for item in get_sql_query(select_query)]

def show_brands():
    select_query = 'select * from selectCosmetics_brands'
    return [item[1] for item in get_sql_query(select_query)]

def show_types():
    select_query = 'select * from selectCosmetics_types'
    return [item[1] for item in get_sql_query(select_query)]

def select_cosmetic():
    select_query = 'select description from (((((selectCosmetics_preferences inner join selectCosmetics_cosmetics on selectCosmetics_preferences.cosmetics_id = selectCosmetics_cosmetics.id) '\
        'inner join selectCosmetics_brands on selectCosmetics_cosmetics.brand_id = selectCosmetics_brands.id)'\
        'inner join selectCosmetics_types on selectCosmetics_cosmetics.type_id = selectCosmetics_types.id) '\
        'inner join selectCosmetics_prices on selectCosmetics_cosmetics.price_id = selectCosmetics_prices.id) '\
        'inner join selectCosmetics_ages on selectCosmetics_preferences.age_id = selectCosmetics_ages.id) '\
        'where selectCosmetics_ages.limits = ' + "'" + str(target_age) + "'" + ' and selectCosmetics_prices.limits = ' + "'" + str(target_price) + "'" + ' '
    if target_brand != 'None':
        select_query += 'and selectCosmetics_brands.name = ' + "'" + str(target_brand) + "'" + ' '
    if target_type != 'None':
        select_query += 'and selectCosmetics_types.name = ' + "'" + str(target_type) + "'" + ' '
    return get_sql_query(select_query)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(True,True)
    for age in show_ages():
        keyboard.row(age)
    keyboard.add('Cancel')
    send = bot.send_message(message.chat.id, 'Выбирете для какой возрастной категории', reply_markup=keyboard)
    bot.register_next_step_handler(send, select_cosmetics_after_age)

@bot.message_handler(content_types=['text'])
def select_cosmetics_after_age(message):
    bot.send_message(message.chat.id,'Вы выбрали ' + str(message.text))
    if message.text in show_ages():
        global target_age
        target_age = message.text
        keyboard = types.ReplyKeyboardMarkup(True,True)
        for index in show_prices():
            keyboard.row(index)
        keyboard.add('Cancel')
        send = bot.send_message(message.chat.id,'Выбирете для какой ценовой категории', reply_markup=keyboard)
        bot.register_next_step_handler(send, select_cosmetics_after_price)
    elif message.text == 'Cancel':
        send_welcome(message)
    else:
        bot.send_message(message.chat.id, 'Повторите пожалуйста еще раз /start')

@bot.message_handler(content_types=['text'])
def select_cosmetics_after_price(message):
    bot.send_message(message.chat.id,'Вы выбрали ' + str(message.text))
    if message.text in show_prices():
        global target_price
        target_price = message.text
        keyboard = types.ReplyKeyboardMarkup(True,True)
        for index in show_brands():
            keyboard.row(index)
        keyboard.add('None')
        keyboard.add('Cancel')
        send = bot.send_message(message.chat.id,'Выбирете какой бренд предпочитаете', reply_markup=keyboard)
        bot.register_next_step_handler(send, select_cosmetics_after_brand)
    elif message.text == 'Cancel':
        send_welcome(message)
    else:
        bot.send_message(message.chat.id, 'Повторите пожалуйста еще раз /start')

@bot.message_handler(content_types=['text'])
def select_cosmetics_after_brand(message):
    bot.send_message(message.chat.id,'Вы выбрали ' + str(message.text))
    if message.text in show_brands() or message.text == 'None':
        global target_brand
        target_brand = message.text
        keyboard = types.ReplyKeyboardMarkup(True,True)
        for index in show_types():
            keyboard.row(index)
        keyboard.add('None')
        keyboard.add('Cancel')
        send = bot.send_message(message.chat.id,'Выбирете какой бренд предпочитаете', reply_markup=keyboard)
        bot.register_next_step_handler(send, select_cosmetics_after_type)
    elif message.text == 'Cancel':
        send_welcome(message)
    else:
        bot.send_message(message.chat.id, 'Повторите пожалуйста еще раз /start')

bot.message_handler(content_types=['text'])
def select_cosmetics_after_type(message):
    bot.send_message(message.chat.id,'Вы выбрали ' + str(message.text))
    if message.text in show_types() or message.text == 'None':
        global target_type
        target_type = message.text
        bot.send_message(message.chat.id,'Вы выбрали ' + str(target_age) + ' ' + str(target_price) + ' ' + str(target_brand) + ' ' + str(target_type))
        selected_cosmetics = select_cosmetic()
        if len(selected_cosmetics) > 0:
            bot.send_message(message.chat.id, 'Baш выбор ' + str(selected_cosmetics[randint(0, len(selected_cosmetics) - 1]))
        else:
            bot.send_message(message.chat.id, 'Ничего не найдено по вашему запросу - попробуйте еще раз')
    elif message.text == 'Cancel':
        send_welcome(message)
    else:
        bot.send_message(message.chat.id, 'Повторите пожалуйста еще раз /start')

bot.polling()