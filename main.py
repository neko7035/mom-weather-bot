import os
import requests
import random
from datetime import datetime
from lunardate import LunarDate

SENDKEY = os.getenv("SENDKEY_MOM")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# ====== 你的基础信息（修改这里） ======
CITY = "Tianjin"
START_DATE = datetime(1995, 12, 8)  # 改成真实母女纪念日
# 农历生日（例如：正月三十）
LUNAR_MONTH = 1
LUNAR_DAY = 30
# =====================================

# 获取天气
def get_weather():
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": CITY,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "zh_cn"
        }
        r = requests.get(url, params=params)
        data = r.json()

        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]

        return temp, temp_min, temp_max, weather
    except:
        return 0, 0, 0, "天气获取失败"


# 随机早安开头
def random_greeting():
    greetings = [
        "妈妈，早上好呀 ☀",
        "妈妈早安 🌷",
        "早安妈妈 💛",
        "新的一天开始啦 ☀"
    ]
    return random.choice(greetings)


# 节日系统
def get_festival():
    festivals = {
        "01-01": "🎉 新年快乐",
        "05-12": "💐 母亲节快乐",
        "10-01": "🇨🇳 国庆节快乐",
        "12-25": "🎄 圣诞节快乐"
    }

    today_md = datetime.now().strftime("%m-%d")
    return festivals.get(today_md, "")
    
def get_lunar_birthday_countdown():
    today = datetime.now()
    year = today.year

    def get_solar_date(y):
        try:
            lunar = LunarDate(y, LUNAR_MONTH, LUNAR_DAY)
            return lunar.toSolarDate()
        except:
            # 如果当年没有这个农历日期（比如正月三十不存在）
            return None

    solar_birthday = get_solar_date(year)

    # 如果今年没有这个农历日期或已经过了，算明年
    if not solar_birthday or solar_birthday < today.date():
        year += 1
        solar_birthday = get_solar_date(year)

    return (datetime.combine(solar_birthday, datetime.min.time()) - today).days

# 母女天数
def get_love_days():
    return (datetime.now() - START_DATE).days

# 随机鼓励语（不连续重复）
def get_random_poetry():
    with open("poetry.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    lines = [line.strip() for line in lines if line.strip()]

    try:
        with open("last_poetry.txt", "r", encoding="utf-8") as f:
            last_line = f.read().strip()
    except:
        last_line = ""

    choices = [line for line in lines if line != last_line]

    if not choices:
        poetry = random.choice(lines)
    else:
        poetry = random.choice(choices)

    with open("last_poetry.txt", "w", encoding="utf-8") as f:
        f.write(poetry)

    return poetry


# 发送微信
def send_wechat(message):
    url = f"https://sctapi.ftqq.com/{SENDKEY}.send"
    data = {
        "title": "妈妈的每日问候",
        "desp": message
    }
    requests.post(url, data=data)


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    weekday_map = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekday_map[datetime.now().weekday()]
    temp, temp_min, temp_max, weather = get_weather()

    # ===== 天气逻辑 =====
    temp_diff = temp_max - temp_min

    if temp_diff >= 8:
        diff_tip = "🌬 今天温差有点大，记得多穿一点。"
    else:
        diff_tip = ""

    if "雨" in weather:
        rain_tip = "☔ 今天可能下雨，记得带伞。"
    else:
        rain_tip = ""

    if temp_max >= 35:
        extreme_tip = "🔥 天气炎热，注意防暑降温。"
    elif temp_min <= 5:
        extreme_tip = "❄ 天气偏冷，注意保暖。"
    else:
        extreme_tip = ""

    festival_tip = get_festival()
    love_days = get_love_days()
    birthday_left = get_lunar_birthday_countdown()
    poetry = get_random_poetry()
    greeting = random_greeting()

    message = f"""
{greeting}

📅 今天是{today} {weekday}
📍 地区：{CITY}
🌤 今日天气：{weather}
🌡 当前温度：{temp}℃
🔺 最高气温：{temp_max}℃
🔻 最低气温：{temp_min}℃

💕 今天是你我做母女的第 {love_days} 天
🎂 距离你的生日还有 {birthday_left} 天

{diff_tip}
{rain_tip}
{extreme_tip}
{festival_tip}

——————————

💛 {poetry}
"""

    print("准备发送消息...")
    print(message)

    send_wechat(message)

