import sqlite3
import telebot
from telebot import types
from geopy.geocoders import Nominatim
import osmnx as ox
import os
import random

users = {}

loc = Nominatim(user_agent='ekbturismbot')
bot = telebot.TeleBot('6187784834:AAHkkxwT3qlf-KP6cxu66aqfQdpOh56YosY')

def choose(message, page, area, count):
    db = sqlite3.connect('sight.db')
    curs = db.cursor()
    curs.execute('SELECT * FROM '+area+' WHERE id = '+str(page))
    for row in curs.fetchall():
        sin = str(row[0])
        sid = str(row[1]).replace("\\"+"n ", "\n")
        lats = float(row[2])
        lngs = float(row[3])
    markup1 = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'Для построения маршрута нажмите "Выбрать"', reply_markup=markup1)
    markup = types.InlineKeyboardMarkup()
    cp = "pagep|"+str(page)+"|"+area+"|"+str(count)
    cm = "pagem|"+str(page)+"|"+area+"|"+str(count)
    cc = "choose|"+str(lats)+"|"+str(lngs)+"|"
    ce = "esc|||"
    btn1 = types.InlineKeyboardButton(text='<---', callback_data=cm)
    btn2 = types.InlineKeyboardButton(text='--->', callback_data=cp)
    btn3 = types.InlineKeyboardButton(text='Выбрать', callback_data=cc)
    btn4 = types.InlineKeyboardButton(text='Отмена', callback_data=ce)
    markup.add(btn1,btn2,btn3,btn4)
    bot.send_message(message.chat.id, sin+'\n'+sid, reply_markup = markup)
@bot.message_handler(content_types=['location'])
def location(message):
    if message.location is not None:
        chat = message.chat.id
        latu = message.location.latitude
        lngu = message.location.longitude
        users[chat] = [latu,lngu]
        menu(message)
@bot.callback_query_handler(func=lambda callback:True)
def callback_query(callback):
    fp = callback.data.split('|')[0]
    sp = callback.data.split('|')[1]
    tp = callback.data.split('|')[2]
    qp = callback.data.split('|')[3]
    page = sp
    area = tp
    count = qp
    if fp == 'pagep':
        page = str(int(page)+1)
        if int(page) > int(count):
            page = "1"
    elif fp == 'pagem':
        page = str(int(page)-1)
        if page == "0":
            page = str(count)
    elif fp == 'esc':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton('Верх-Исетский')
        btn2 = types.KeyboardButton('Железнодорожный')
        btn3 = types.KeyboardButton('Кировский')
        btn4 = types.KeyboardButton('Ленинский')
        btn5 = types.KeyboardButton('Октябрьский')
        btn6 = types.KeyboardButton('Орджоникидзевский')
        btn7 = types.KeyboardButton('Чкаловский')
        btn8 = types.KeyboardButton('Академический')
        btn9 = types.KeyboardButton('Где я нахожусь')
        btn10 = types.KeyboardButton("/menu")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10) 
        bot.send_message(callback.message.chat.id, text="Выберите район", reply_markup=markup)
        return
    elif fp == "choose":
        routes(callback.message, float(sp), float(tp))
        return
    db = sqlite3.connect('sight.db')
    curs = db.cursor()
    curs.execute('SELECT * FROM '+area+' WHERE id = '+page)
    for row in curs.fetchall():
        sin = str(row[0])
        sid = str(row[1]).replace("\\"+"n ", "\n")
        lats = str(row[2])
        lngs = str(row[3])
    cp = "pagep|"+str(page)+"|"+area+"|"+str(count)
    cm = "pagem|"+str(page)+"|"+area+"|"+str(count)
    cc = "choose|"+lats+"|"+lngs+"|"
    ce = "esc|||"
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='<---', callback_data=cm)
    btn2 = types.InlineKeyboardButton(text='--->', callback_data=cp)
    btn3 = types.InlineKeyboardButton(text='Выбрать', callback_data=cc)
    btn4 = types.InlineKeyboardButton(text='Отмена', callback_data=ce)
    markup.add(btn1,btn2,btn3,btn4)
    bot.edit_message_text(sin+'\n'+sid,chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=markup)
@bot.message_handler(commands = ['start'])
def start(message):
    chat = message.chat.id
    if not(chat in users):
        users.update({chat:[0,0]})
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton('Составить маршрут', request_location=True)
    btn2 = types.KeyboardButton('Подобрать достопримечательность', request_location=True)
    btn3 = types.KeyboardButton("Обновить мою геолокацию", request_location=True)
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "Здравствуйте! Что Вас интересует?", reply_markup=markup)
@bot.message_handler(commands = ['help'])
def help(message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Справочное меню / Help menu: \n /help - вызов этого меню / calling this menu \n /menu - выйти в главное меню / exit to the main menu", reply_markup=markup)
@bot.message_handler(commands = ['menu'])
def menu(message):
    chat = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    latu = users[chat][0]
    lngu = users[chat][1]
    if latu != 0 and lngu != 0:
        btn1 = types.KeyboardButton('Составить маршрут')
        btn2 = types.KeyboardButton('Подобрать достопримечательность')
    else:
        btn1 = types.KeyboardButton('Составить маршрут', request_location=True)
        btn2 = types.KeyboardButton('Подобрать достопримечательность', request_location=True)
    btn3 = types.KeyboardButton("Обновить мою геолокацию", request_location=True)
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "Что Вас интересует?", reply_markup=markup)
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Составить маршрут":
        markup = types.ReplyKeyboardRemove()
        msg = bot.send_message(message.chat.id, "Введите адрес (улица, дом) или название места", reply_markup=markup)
        bot.register_next_step_handler(msg, route)
    elif message.text == 'Подобрать достопримечательность':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton('Верх-Исетский')
        btn2 = types.KeyboardButton('Железнодорожный')
        btn3 = types.KeyboardButton('Кировский')
        btn4 = types.KeyboardButton('Ленинский')
        btn5 = types.KeyboardButton('Октябрьский')
        btn6 = types.KeyboardButton('Орджоникидзевский')
        btn7 = types.KeyboardButton('Чкаловский')
        btn8 = types.KeyboardButton('Академический')
        btn9 = types.KeyboardButton('Где я нахожусь')
        btn10 = types.KeyboardButton("/menu")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10)
        bot.send_message(message.chat.id, "Выберите район", reply_markup=markup)
    elif message.text == 'Верх-Исетский':
        area = 'verhiset'
        db = sqlite3.connect('sight.db')
        curs = db.cursor()
        curs.execute('SELECT COUNT(*) FROM '+area)
        for row in curs.fetchall():
            count = row[0]
        choose(message, 1, area, count)
    elif message.text == 'Железнодорожный':
        area = 'zshelezn'
        db = sqlite3.connect('sight.db')
        curs = db.cursor()
        curs.execute('SELECT COUNT(*) FROM '+area)
        for row in curs.fetchall():
            count = row[0]
        choose(message, 1, area, count)
    elif message.text == 'Кировский':
        area = 'kirovski'
        db = sqlite3.connect('sight.db')
        curs = db.cursor()
        curs.execute('SELECT COUNT(*) FROM '+area)
        for row in curs.fetchall():
            count = row[0]
        choose(message, 1, area, count)
    elif message.text == 'Ленинский':
        area = 'leninski'
        db = sqlite3.connect('sight.db')
        curs = db.cursor()
        curs.execute('SELECT COUNT(*) FROM '+area)
        for row in curs.fetchall():
            count = row[0]
        choose(message, 1, area, count)
    elif message.text == 'Октябрьский':
        area = 'oktyabrs'
        db = sqlite3.connect('sight.db')
        curs = db.cursor()
        curs.execute('SELECT COUNT(*) FROM '+area)
        for row in curs.fetchall():
            count = row[0]
        choose(message, 1, area, count)
    elif message.text == 'Орджоникидзевский':
        area = 'ordzshon'
        db = sqlite3.connect('sight.db')
        curs = db.cursor()
        curs.execute('SELECT COUNT(*) FROM '+area)
        for row in curs.fetchall():
            count = row[0]
        choose(message, 1, area, count)
    elif message.text == 'Чкаловский':
        area = 'chkalovs'
        db = sqlite3.connect('sight.db')
        curs = db.cursor()
        curs.execute('SELECT COUNT(*) FROM '+area)
        for row in curs.fetchall():
            count = row[0]
        choose(message, 1, area, count)
    elif message.text == 'Академический':
        area = 'akademic'
        db = sqlite3.connect('sight.db')
        curs = db.cursor()
        curs.execute('SELECT COUNT(*) FROM '+area)
        for row in curs.fetchall():
            count = row[0]
        choose(message, 1, area, count)
    elif message.text == "Где я нахожусь":
        latu = users[message.chat.id][0]
        lngu = users[message.chat.id][1]
        coords = (latu,lngu)
        get = loc.reverse(coords, zoom=12)
        ar = get.address[0:get.address.find(' ')]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton(text=ar)
        markup.add(btn)
        bot.send_message(message.chat.id, text="Вы находитесь:\nШирота: "+str(latu)+"\nДолгота: "+str(lngu)+"\nРайон: "+ar, reply_markup=markup)
def route(message):
    address = str(message.text)
    if address == '/menu':
        menu(message)
    elif address == '/help':
        help(message)
    elif address == '/start':
        start(message)
    else:
        getl = loc.geocode('Екатеринбург,'+address)
        try:
            lats = getl.latitude
            lngs = getl.longitude
            routes(message, lats, lngs)
        except:
            bot.send_message(message.chat.id, 'Извините, адрес не найден. Пожалуйста, попробуйте ввести более точную информацию или выберите вариант из предложенных во вкладке "Подобрать достопримечательность".')
            menu(message)
def routes(message, lats, lngs):
    chat = message.chat.id
    if users[chat][0]==0 or users[chat][1]==0:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn = types.KeyboardButton("Отправить геолокацию", request_location=True)
        markup.add(btn)
        bot.send_message(chat, "Для построения маршрута необходимо отправить боту геолокацию", reply_markup=markup)
    else:
        symbols = "abcdefghijklmnopqrstuvwxyz1234567890"
        rand = ''.join(random.choice(symbols) for i in range(8))
        markup1 = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Пожалуйста, подождите", reply_markup=markup1)
        lngu = users[chat][1]
        latu = users[chat][0]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn = types.KeyboardButton("/menu")
        markup.add(btn)
        place = "Екатеринбург, Свердловская область, Россия"
        G = ox.graph.graph_from_place(place, network_type="drive")
        orig = ox.distance.nearest_nodes(G, lngu, latu)
        dest = ox.distance.nearest_nodes(G, lngs, lats)
        route = ox.distance.shortest_path(G, orig, dest, weight="lenght")
        fig = ox.folium.plot_route_folium(G, route, tiles='openstreetmap')
        fig.save(rand+".html")
        htmlf = open("./"+rand+".html", "rb")
        bot.send_document(message.chat.id, htmlf, reply_markup=markup)
        os.remove('./'+rand+'.html')

bot.polling(none_stop = True)