import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


async def get_weather(session,latitude,longitude):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=precipitation_probability&timezone=Europe%2FIstanbul&forecast_days=2"
    async with session.get(url) as response:
        months={
        "01":"Ocak",
        "02":"Şubat",
        "03":"Mart",
        "04":"Nisan",
        "05":"Mayıs",
        "06":"Haziran",
        "07":"Temmuz",
        "08":"Ağustos",
        "09":"Eylül",
        "10":"Ekim",
        "11": "Kasım",
        "12": "Aralık"
    }
        respond = await response.json()
        
        risky_hours = []
        hours = respond["hourly"]["time"][24:]   
        rain_chance = respond["hourly"]["precipitation_probability"][24:]
        day = respond["hourly"]["time"][24].split("T")[0]
        datetime_day = datetime.strptime(day,"%Y-%m-%d")
        day_str = datetime_day.strftime("%d.%m.%Y")
        obj=day_str.split(".")[1]
        day_str=day_str.replace(obj,months[obj]).replace("."," ")
        for hour,chance in zip(hours,rain_chance):
            
            if chance >30 :
                hour = hour.split("T")[1]
                risky_hours.append(f"{hour}-> Yağmur İhtimali: {chance}")
            
            
        if len(risky_hours) > 0: 
            return [risky_hours,day_str]
        else:
            return ["Yarın yağmur ihtimali yok.",day_str]
async def telegram_message(session,message):
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    context = {
        "chat_id" : CHAT_ID ,
        "text" : message 
    }
    async with session.post(url,json=context) as response:
        if response.status == 200:
            print("Başarılı mesaj gönderildi.")
        else:
            print("Hata Kodu:",response.status)



async def main():
    latitude = os.getenv("LATITUDE")
    longitude = os.getenv("LONGITUDE")
    async with aiohttp.ClientSession() as session :
        result = await get_weather(session,latitude,longitude)
        day = result[1]
        data = result[0]
        if data != "Yarın yağmur ihtimali yok." :
            hours_text = day +"\n" + "\n".join(data)
            hours_text += "\n%30 - %40: Hafif çiseleme veya geçici bir sağanak olabilir. Şemsiye alınabilir.\n%50 - %60: Büyük ihtimal yağar ona göre hazırlanmak gerek.\n%70 ve üzeri: Kesin gözüyle bakılır.\n"
            await telegram_message(session, hours_text)
        else:await telegram_message(session, day + " (Yarın) yağmur ihtimali yok.")

if __name__ == "__main__":
    asyncio.run(main())

