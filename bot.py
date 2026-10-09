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

    temp_file = "last_temp.txt"
    saved_temp = None

    # Считываем сохраненное значение
    if os.path.exists(temp_file):
        try:
            with open(temp_file, "r") as f:
                saved_temp = float(f.read().strip())
        except ValueError:
            saved_temp = None

    print(f"Сохраненная ранее температура: {saved_temp}°C")

    # Сравнение: отправляем ТОЛЬКО если текущая температура строго ВЫШЕ сохраненной
    if saved_temp is not None and curr_temp > saved_temp:
        print(f"🔥 Температура выросла ({saved_temp}°C ➡️ {curr_temp}°C)! Отправляем в n8n...")
        payload = {
            "temperature": f"{curr_temp}°C",
            "previous_temperature": f"{saved_temp}°C"
        }
        try:
            res = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
            print(f"✅ Ответ от n8n: статус {res.status_code}")
        except Exception as e:
            print(f"❌ Ошибка отправки в n8n: {e}")
    elif saved_temp is None:
        print("🚀 Первый запуск: фиксируем базовую температуру без вызова n8n.")
    else:
        print(f"💤 Температура не выросла (Было: {saved_temp}°C, Стало: {curr_temp}°C). n8n не вызываем.")

    # Обновляем кэш свежим значением
    with open(temp_file, "w") as f:
        f.write(str(curr_temp))

if __name__ == "__main__":
    main()
