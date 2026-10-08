import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.weather.gov/wrh/timeseries?site=lemd"
# Ваш вебхук из n8n, куда слать SMS/уведомление при изменении
N8N_WEBHOOK_URL = "ЗДЕСЬ_УКАЖИТЕ_ВАШ_URL_ВЕБХУКА_N8N"

def get_current_temperature():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Парсим погоду с weather.gov (ищем блок/ячейку с температурой)
    # На этой странице данные обычно в таблице таймсерии. 
    # Замените этот селектор под ваш текущий парсер, который вы уже использовали:
    temp_element = soup.find('td', class_='data') # Пример, поставьте ваш селектор
    
    # Если вы уже парсили температуру раньше, просто вставьте свой рабочий кусок кода получения температуры ниже:
    # --- НАЧАЛО ВАШЕГО ПАРСЕРА ---
    temperature = temp_element.text.strip() if temp_element else "Unknown"
    # --- КОНЕЦ ВАШЕГО ПАРСЕРА ---
    
    return temperature

def main():
    current_temp = get_current_temperature()
    print(f"Текущая температура с сайта: {current_temp}")

    temp_file = "last_temp.txt"
    
    # Читаем старую температуру, если она сохранилась с прошлого запуска
    saved_temp = None
    if os.path.exists(temp_file):
        with open(temp_file, "r") as f:
            saved_temp = f.read().strip()

    print(f"Последняя сохраненная температура: {saved_temp}")

    # Сравниваем
    if current_temp != saved_temp:
        print("⚡ Температура изменилась! Отправляем запрос в n8n...")
        
        payload = {"temperature": current_temp}
        try:
            response = requests.post(N8N_WEBHOOK_URL, json=payload)
            print(f"Ответ от n8n: {response.status_code}")
        except Exception as e:
            print(f"Ошибка отправки в n8n: {e}")
    else:
        print("💤 Температура не изменилась. Ничего не отправляем в n8n (экономим кредиты).")

    # Записываем актуальную температуру для следующего запуска
    with open(temp_file, "w") as f:
        f.write(current_temp)

if __name__ == "__main__":
    main()
