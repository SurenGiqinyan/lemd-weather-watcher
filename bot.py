import os
import requests

# 1. Вставьте сюда ВАШУ реальную ссылку на Webhook из n8n
N8N_WEBHOOK_URL = "https://gevorgghevondyan.app.n8n.cloud/webhook/weather-update-lemd"

# Публичный API погоды для станции LEMD (Мадрид)
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
        print(f"Ошибка получения данных погоды: {e}")
    return None

def main():
    curr_temp = get_current_temperature()
    print(f"Текущая температура: {curr_temp}°C")

    if curr_temp is None:
        print("❌ Не удалось получить температуру.")
        return

    temp_file = "last_temp.txt"
    saved_temp = None

    # Считываем предыдущую температуру из кэша
    if os.path.exists(temp_file):
        try:
            with open(temp_file, "r") as f:
                saved_temp = float(f.read().strip())
        except ValueError:
            saved_temp = None

    print(f"Предыдущая сохраненная температура: {saved_temp}°C")

    # СРАВНЕНИЕ: отправка в n8n выполняется СТРОГО при РОСТЕ температуры
    if saved_temp is not None and curr_temp > saved_temp:
        print(f"🔥 Температура выросла ({saved_temp}°C ➡️ {curr_temp}°C)! Отправляем запрос в n8n...")
        payload = {
            "temperature": f"{curr_temp}°C",
            "previous_temperature": f"{saved_temp}°C"
        }
        try:
            res = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
            print(f"Ответ от n8n: статус {res.status_code}")
        except Exception as e:
            print(f"Ошибка отправки в n8n: {e}")
    elif saved_temp is None:
        print("🚀 Первый запуск: записываем базовую температуру в кэш без отправки в n8n.")
    else:
        print(f"💤 Температура не изменилась или упала (Было: {saved_temp}°C, Стало: {curr_temp}°C). n8n не вызываем.")

    # Всегда обновляем сохраненное значение для следующей проверки
    with open(temp_file, "w") as f:
        f.write(str(curr_temp))

if __name__ == "__main__":
    main()
