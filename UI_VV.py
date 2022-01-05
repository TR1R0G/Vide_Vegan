import telebot
from telebot import types

import mysql.connector

bot = telebot.TeleBot('TOKEN OF THE BOT WHICH IS A SECRET KEY')

print(bot.get_me())

import mysql.connector

db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  port="3306",
  database="profile"
)

cursor = db.cursor()

### UPDATING A COLUMN
# sql = "UPDATE menu SET category = 'Пасты \U0001F60B' WHERE lim = 10"
#
# cursor.execute(sql)
# db.commit()

### INSERTING
# sql = "INSERT INTO menu (name, price, lim, description, image, category) VALUES (%s, %s, %s, %s, %s, %s)"
# val = [
#     ("Хумус классический", 40000, 10, "1 баночка 400 гр", "img/humus_classic.jpg", 'Пасты \U0001F60B'),
#     ("Бабагануш", 45000, 10, "1 баночка 400 гр", "img/babaganush.jpg"),
#     ("Хумус со шпинатом", 45000, 10, "1 баночка 400 гр", "img/humus_spinach.jpg")
# ]
# cursor.executemany(sql, val)
# db.commit()
#
# print(cursor.rowcount, "строк добавлены.")

user_dict = {}

# --- Register the USER --- #
class User:
    def __init__(self, name):
        self.name = name
        self.phone = None
        self.lat = None
        self.lon = None


# -------------  MAIN MENU  ---------------- #

markup_main = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

menu = types.KeyboardButton('Меню ' + u'\U0001F37D')
deals = types.KeyboardButton('Акции ' + u'\U0001F381')
contacts = types.KeyboardButton('Контакты ' + u'\U0000260E')
review = types.KeyboardButton('Оставить отзыв ' + u'\U0001F4DD')
about_us = types.KeyboardButton('О нас ' + u'\U0001F331')
cart = types.KeyboardButton('Корзина ' + u'\U0001F6D2')
markup_main.add(menu, deals, contacts, review, about_us, cart)

@bot.message_handler(commands=['start'])
def start_message(message):

    sql = "SELECT * FROM users WHERE user_id = %s"
    adr = (message.chat.id, )
    cursor.execute
    cursor.execute(sql, adr)
    result = cursor.fetchall()
    row_count = cursor.rowcount

    if row_count == 0:
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id,
                         'Рады видеть Вас! Vida Vegan это Единственная в Узбекистане этичная веганская кухня.'
                         'Мы готовим вкусные и полезные блюда и десерты без продуктов животного происхождения, глютена, сахара, белой муки и дрожжей.')

        bot.send_message(message.chat.id, 'Введите ФИО:')
        bot.register_next_step_handler(message, reg_name)

    else:
        bot.send_message(message.chat.id, "Главное меню: ", reply_markup=markup_main)
        bot.register_next_step_handler(message, main)


def reg_name(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user

        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить Контакт", request_contact=True)
        keyboard.add(button_geo)
        msg = bot.send_message(message.chat.id, "Отправьте или введите ваш номер телефона в формате +998xxxxxxxxx",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, geo)

    except:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте снова. /start')

def geo(message):

    chat_id = message.chat.id
    phone = message.contact.phone_number
    user = user_dict[chat_id]

    user.phone = phone
    bot.send_message(chat_id, "Phone number: " + str(user.phone))
    markup = types.ReplyKeyboardRemove(selective=False)

    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id,
                         "Отправьте свою геопозицию",
                         reply_markup=keyboard)

    bot.register_next_step_handler(message, user_location)


def user_location(message):
    lon = message.location.longitude
    lat = message.location.latitude

    chat_id = message.chat.id
    user = user_dict[chat_id]

    user.lat = lat
    user.lon = lon

    sql = "INSERT INTO users (user_id, name, phone, lat, lon) VALUES (%s, %s, %s, %s, %s)"
    val = (chat_id, user.name, user.phone, user.lat, user.lon)
    cursor.execute(sql, val)
    db.commit()

    bot.send_message(chat_id, 'Локация: ' + str(user.lat) + ' ' + str(user.lon))
    bot.send_message(message.chat.id, "Главное меню: ", reply_markup=markup_main)
    bot.register_next_step_handler(message, main)


def main(message):
    if message.text == 'Меню ' + u'\U0001F37D':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        cursor.execute("SELECT * FROM menu")
        menus = cursor.fetchall()
        menu_sorted = []

        for menu in menus:
            if menu[6] not in menu_sorted:
                menu_sorted.append(menu[6])
                markup.add(menu[6])

        markup.add("Назад " + u'\U00002B05')
        bot.send_message(message.chat.id, "Выберите раздел:", reply_markup=markup)
        bot.register_next_step_handler(message, category)

    elif message.text == 'Акции ' + u'\U0001F381':
        bot.send_message(message.chat.id, "В данный момент нету акций, но мы обязательно что нибудь придумаем " + u'\U0001F603')

    elif message.text == 'Контакты ' + u'\U0000260E':
        bot.send_message(message.chat.id, "Основатель Олейник Анна +998909393277"
        "Альтернативный способ заказа: https://t.me/v_vegan_chat")

    elif message.text == 'Оставить отзыв ' + u'\U0001F4DD':
        bot.send_message(message.chat.id, "Контроль сервиса. Ваш отзыв очень важен для нас, оцените нашу работу " + u'\U00002705')

    elif message.text == 'О нас ' + u'\U0001F331':
        bot.send_message(message.chat.id, "Единственная в Узбекистане этичная веганская кухня. "
        "Мы готовим вкусные и полезные блюда и десерты без продуктов животного происхождения, глютена, сахара, белой муки и дрожжей.")

    elif message.text == 'Корзина ' + u'\U0001F6D2':
        # add if empty if not empty ------------------------------------------------
        bot.send_message(message.chat.id,
                         'В корзине пусто ' + u'\U0001F614' + '\n' + 'Посмотрите меню, там много интересного ' + u'\U0001F609')


def category(message):
    if message.text == "Назад " + u'\U00002B05':
        bot.send_message(message.chat.id, "Главное меню: ", reply_markup=markup_main)
        main(message)
        return

    else:
        cursor.execute("SELECT * FROM menu")
        menus = cursor.fetchall()

        for menu in menus:
            if message.text == menu[6]:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                cursor.execute("SELECT * FROM menu")
                menus = cursor.fetchall()

                for menu in menus:
                    markup.add(menu[1])

                markup.add("Назад " + u'\U00002B05')

                bot.send_message(message.chat.id, "Выберите товар, чтобы вывести вкусненькое", reply_markup=markup)
                bot.register_next_step_handler(message, menu_further)
                break

def menu_further(message):
    if message.text == "Назад " + u'\U00002B05':
        #bot.send_message(message.chat.id, "Выберите раздел:", reply_markup=markup)
        category(message)
        return
    else:
        cursor.execute("SELECT * FROM menu")
        menus = cursor.fetchall()

        for menu in menus:
            if message.text == menu[1]:
                food = open(menu[5], 'rb')
                bot.send_photo(message.chat.id, food, menu[1] + "\n" + menu[4] + "\nЦена: " + str(menu[2]))
                food.close()


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

bot.polling(none_stop=True, interval=0) #keeps the bot running