import os
import requests
from datetime import datetime

# 读取环境变量
SENDKEY_MOM = os.getenv("SENDKEY_MOM")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# 天津坐标
LAT = 39.0842
LON = 117.2000

def get_weather():
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": LAT,
        "lon": LON,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "zh_cn"
    }
    response = requests.get(url, params=params)
    data = response.json()

    temp = data["main"]["temp"]
    temp_min = data["main"]["temp_min"]
    temp_max = data["main"]["temp_max"]
    weather = data["weather"][0]["description"]

    return temp, temp_min, temp_max, weather

def send_wechat(message):
    url = f"https://sctapi.ftqq.com/{SENDKEY_MOM}.send"
    data = {
        "title": "妈妈的每日天气提醒",
        "desp": message
    }
    r = requests.post(url, data=data)
    print("Server酱返回:", r.text)

def main():
    today = datetime.now().strftime("%Y-%m-%d")

    temp, temp_min, temp_max, weather = get_weather()

    message = f"""
📅 日期：{today}

📍 天津
🌤 天气：{weather}
🌡 当前温度：{temp}℃
🔺 最高温：{temp_max}℃
🔻 最低温：{temp_min}℃

💖 今天也要开心哦～
"""

    print("准备发送消息...")
    print(message)

    send_wechat(message)

if __name__ == "__main__":
    main()
