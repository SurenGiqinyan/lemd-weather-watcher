from bs4 import BeautifulSoup
import json
import os
import requests

# URL страницы погоды аэропорта Мадрида
URL = 'https://www.weather.gov/wrh/timeseries?site=lemd'

# ЗАМЕНИТЕ НА ВАШ PRODUCTION URL ИЗ n8n!
N8N_WEBHOOK_URL = 'https://gevorgghevondyan.app.n8n.cloud/webhook/weather-update-lemd'
# Файл для хранения времени последней успешной проверки
STATE_FILE = 'last_checked_time.txt'


def get_latest_weather():
  headers = {'User-Agent': 'Mozilla/5.0'}
  response = requests.get(URL, headers=headers)
  if response.status_code != 200:
    print('Ошибка доступа к сайту погоды')
    return None

  soup = BeautifulSoup(response.text, 'html.parser')
  table = soup.find('table')
  if not table:
    return None

  rows = table.find_all('tr')
  for row in reversed(rows):
    cols = row.find_all('td')
    if len(cols) > 5:
      time_str = cols[0].text.strip()
      temp_c = cols[1].text.strip()
      return {'time': time_str, 'temp': temp_c, 'raw_html': str(row)}

  return None


def main():
  current_data = get_latest_weather()
  if not current_data:
    return

  current_time = current_data['time']

  last_time = ''
  if os.path.exists(STATE_FILE):
    with open(STATE_FILE, 'r') as f:
      last_time = f.read().strip()

  if current_time != last_time:
    print(
        f'Обнаружены новые данные! Время: {current_time}. Отправляем в n8n...'
    )
    res = requests.post(N8N_WEBHOOK_URL, json=current_data)
    if res.status_code == 200:
      with open(STATE_FILE, 'w') as f:
        f.write(current_time)
      print('Успешно отправлено в n8n!')
    else:
      print(f'Ошибка отправки веб-хука: {res.status_code}')
  else:
    print('Новых данных пока нет. Сайт не обновлялся.')


if __name__ == '__main__':
  main()
