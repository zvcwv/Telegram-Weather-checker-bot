import telebot
import webbrowser
from telebot import types
import requests
import json



bot = telebot.TeleBot('')
API = ''


user_language = {}



city_map = {
    "서울": "Seoul",
    "부산": "Busan",
    "대구": "Daegu",
    "인천": "Incheon",
    "광주": "Gwangju",
    "대전": "Daejeon",
    "울산": "Ulsan"
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')
    btn2 = types.InlineKeyboardButton("🇬🇧 English", callback_data='lang_eng')
    btn3 = types.InlineKeyboardButton("🇰🇷 한국어", callback_data='lang_kr')
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, 'Choose your language:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
    chat_id = call.message.chat.id
    lang = call.data.split('_')[1]
    user_language[chat_id] = lang
    if lang == 'ru':
        bot.send_message(chat_id, "Привет! Я AyanBot 🤖\nНапиши /weather чтобы узнать погоду 🌦")
    elif lang == 'kr':
        bot.send_message(chat_id, "안녕하세요, 저는 아얀봇 (AYANBOT)🤖\n'날씨를 알려받으려고 '/weather'를 쓰십시오")
    else:
        bot.send_message(chat_id, "Hi! I’m AyanBot 🤖\nType /weather to check the weather 🌦")
    
    


@bot.message_handler(commands=['weather'])
def ask_city(message):
    lang = user_language.get(message.chat.id, 'en')
    if lang == 'ru':
        bot.send_message(message.chat.id, 'Введите название вашего города 🌍')
    elif lang == 'kr':
        bot.send_message(message.chat.id, '도시 이름을 입력하세요 🌍')    
    else:
        bot.send_message(message.chat.id, 'Please enter your city name 🌍')
    bot.register_next_step_handler(message, get_weather)


def get_weather(message):
    lang = user_language.get(message.chat.id, 'en')
    city = message.text.strip().lower()
    
    if city == '/stop':
        if lang == 'ru':
            bot.reply_to(message, "👋 Хорошо, погоду больше не спрашиваю.")
        elif lang == 'kr':
            bot.reply_to(message, "👋 알겠습니다. 더 이상 날씨에 대해 묻지 않겠습니다.")
        else:
            bot.reply_to(message, "👋 Okay, I won't ask about the weather anymore.")
        return
    
    city_eng = city_map.get(city, city)
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city_eng}&appid={API}&units=metric&lang={lang}')

    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].capitalize()

        if lang == 'ru':
            bot.reply_to(message, f"🌤 Погода в {city.title()}: {temp}°C, {desc}")
            next_msg = bot.send_message(message.chat.id, "Введи другой город или напиши /stop, чтобы выйти:")
        elif lang == 'kr':
            bot.reply_to(message, f"🌤 {city.title()}에서 {temp}°C, {desc}입니다")
            next_msg = bot.send_message(message.chat.id, "다른 도시를 입력하거나 /stop을 입력하세요:")
        else:
            bot.reply_to(message, f"🌤 Weather in {city.title()}: {temp}°C, {desc}")
            next_msg = bot.send_message(message.chat.id, "Enter another city or type /stop to exit:")
            
        bot.register_next_step_handler(next_msg, get_weather)
    else:
        if lang == 'ru':
            bot.reply_to(message, "❌ Город не найден. Попробуй снова.")
        elif lang == 'kr':
            bot.reply_to(message, "❌ 도시를 찾을 수 없습니다. 다시 시도해 주세요.")
        else:
            bot.reply_to(message, "❌ City not found. Please try again.")
        
        bot.register_next_step_handler(message, get_weather)










bot.polling(none_stop=True)