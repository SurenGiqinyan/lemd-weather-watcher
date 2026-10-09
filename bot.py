import os
import requests

# Твой рабочий вебхук n8n Cloud
N8N_WEBHOOK_URL = "https://gevorgghevondyan.app.n8n.cloud/webhook/weather-update-lemd"
WEATHER_API_URL = "https://aviationweather.gov/api/data/metar?ids=LEMD&format=json"

def get_current_temperature():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(WEATHER_API_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                temp = data[0].get('temp')
                if temp is not None:
                    return float(temp)
    except Exception as e:
        print(f"Ошибка получения погоды: {e}")
    return None

def main():
    curr_temp = get_current_temperature()
    print(f"Текущая температура LEMD: {curr_temp}°C")

    if curr_temp is None:
        print("❌ Не удалось получить температуру.")
        return

    # ТЕСТОВЫЙ РЕЖИМ: Отправка выполняется при КАЖДОМ запуске
    print("🧪 ТЕСТОВЫЙ РЕЖИМ: Принудительно отправляем запрос в n8n...")
    payload = {
        "temperature": f"{curr_temp}°C",
        "mode": "test_run"
    }
    
    try:
        res = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
        print(f"✅ Ответ от n8n: статус {res.status_code}")
    except Exception as e:
        print(f"❌ Ошибка отправки в n8n: {e}")

    # Записываем температуру в файл
    with open("last_temp.txt", "w") as f:
        f.write(str(curr_temp))

if __name__ == "__main__":
    main()
