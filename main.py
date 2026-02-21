import os
import requests
import random
from datetime import datetime, timezone, timedelta
from lunardate import LunarDate

JST = timezone(timedelta(hours=9))

def now():
    return datetime.now(JST)

SENDKEY = os.getenv("SENDKEY_MOM")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

CITY = "Tianjin"
START_DATE = datetime(1995, 12, 8)
LUNAR_MONTH = 1
LUNAR_DAY = 30


def get_weather():
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": f"{CITY},cn",
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "zh_cn"
        }

        r = requests.get(url, params=params)
        data = r.json()

        if data.get("cod") != "200":
            return 0, 0, 0, "天气获取失败", 0

        today_str = now().strftime("%Y-%m-%d")

        temps = []
        pops = []
        weather_desc = ""

        for item in data["list"]:
            if item["dt_txt"].startswith(today_str):
                temps.append(item["main"]["temp"])
                pops.append(item.get("pop", 0))
                weather_desc = item["weather"][0]["description"]

        if not temps:
            return 0, 0, 0, "天气获取失败", 0

        temp = sum(temps) / len(temps)
        temp_min = min(temps)
        temp_max = max(temps)
        rain_probability = int(max(pops) * 100)

        return round(temp, 1), round(temp_min, 1), round(temp_max, 1), weather_desc, rain_probability

    except Exception as e:
        print("天气获取异常:", e)
        return 0, 0, 0, "天气获取失败", 0


def get_festival():
    festivals = {
        "01-01": "🎉 新年快乐",
        "05-12": "💐 母亲节快乐",
        "10-01": "🇨🇳 国庆节快乐",
        "12-25": "🎄 圣诞节快乐"
    }
    return festivals.get(now().strftime("%m-%d"), "")


def get_lunar_birthday_countdown():
    today = now()
    year = today.year

    def get_solar(y):
        try:
            return LunarDate(y, LUNAR_MONTH, LUNAR_DAY).toSolarDate()
        except:
            return None

    solar = get_solar(year)
    if not solar or solar < today.date():
        solar = get_solar(year + 1)

    return (datetime.combine(solar, datetime.min.time(), tzinfo=JST) - today).days


def get_love_days():
    return (now().date() - START_DATE.date()).days


def get_random_poetry():
    with open("poetry.txt", "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    try:
        with open("last_poetry.txt", "r", encoding="utf-8") as f:
            last = f.read().strip()
    except:
        last = ""

    choices = [l for l in lines if l != last]
    poetry = random.choice(choices or lines)

    with open("last_poetry.txt", "w", encoding="utf-8") as f:
        f.write(poetry)

    return poetry


def send_wechat(message):
    if not SENDKEY:
        print("SENDKEY 未设置")
        return

    try:
        r = requests.post(
            f"https://sctapi.ftqq.com/{SENDKEY}.send",
            data={"title": "妈妈的每日问候", "desp": message}
        )
        print("状态码:", r.status_code)
        print("返回:", r.text)
    except Exception as e:
        print("发送失败:", e)


def main():
    current = now()
    today = current.strftime("%Y-%m-%d")
    weekday = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"][current.weekday()]

    temp, tmin, tmax, weather, rain = get_weather()

    diff_tip = "🌬 今天温差有点大，记得多穿一点哟！" if tmax - tmin >= 8 else ""
    rain_tip = "☔ 出门记得带伞哟！别感冒啦！" if rain >= 50 else ""
    hot_tip = "🔥 注意防暑降温，别中暑了哟！" if tmax >= 35 else ""
    cold_tip = "❄ 注意保暖，别冻感冒啦！" if tmin <= 5 else ""

    birthday_left = get_lunar_birthday_countdown()
    birthday_text = "🎉 今天是妈妈的生日！🎂\n" if birthday_left == 0 else f"🎂 距离妈妈的生日还有 {birthday_left} 天\n"

    weather_block = "\n".join([
        f"🌤 今日天气：{weather}\n",
        f"🌡 当前温度：{temp}℃\n",
        f"🔺 最高气温：{tmax}℃\n",
        f"🔻 最低气温：{tmin}℃\n",
        f"🌧 降雨概率：{rain}%\n"
    ])

    extra = "\n".join([l for l in [diff_tip, rain_tip, hot_tip, cold_tip, get_festival()] if l])

    message = "\n\n".join([p for p in [
        random.choice(["妈妈早安 🌞","妈妈早安 🌷","早安妈妈 💛"]),
        f"📅 {today} {weekday}\n",
        f"📍 {CITY}\n",
        weather_block,
        f"💕 今天是你我做母女的第 {get_love_days()} 天\n", 
        f"{birthday_text}\n",
        extra,
        "——————————",
        f"💛 {get_random_poetry()}"
    ] if p])

    print(message)
    send_wechat(message)


if __name__ == "__main__":
    main()


