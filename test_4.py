import requests
from bs4 import BeautifulSoup
import telebot
from datetime import datetime
import time

# Telegram Bot API
bot = telebot.TeleBot('8134670429:AAEHZDAZpgYmKkAtbDOHWGYThZqSU_vZOjY')

# URL для парсинга
URL = 'https://cryptorank.io/funding-rounds'

# Функция для парсинга данных
def parse_funding_rounds():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    projects = []
    # Найти проекты, привлекшие от 5 млн и данные по фондам, инвестициям
    for project in soup.find_all('div', class_='project-card'):
        try:
            name = project.find('h3', class_='project-name').text
            raised = int(project.find('span', class_='raised-amount').text.replace('$', '').replace('M', ''))
            team = project.find('div', class_='team').text
            funds = [fund.text for fund in project.find_all('div', class_='fund-name')]
            
            # Проверка на привлечение более 5 млн
            if raised >= 5:
                projects.append({
                    'name': name,
                    'raised': raised,
                    'team': team,
                    'funds': funds
                })
        except AttributeError:
            continue

    return projects

# Функция для фильтрации данных
def filter_projects(projects, min_funds=None, max_funds=None, stage=None, fund_type=None):
    filtered_projects = []
    for project in projects:
        if min_funds and project['raised'] < min_funds:
            continue
        if max_funds and project['raised'] > max_funds:
            continue
        if stage and stage not in project.get('stage', ''):
            continue
        if fund_type and fund_type not in project.get('funds', []):
            continue
        filtered_projects.append(project)
    return filtered_projects

# Отправка сообщений в Telegram
def send_funding_updates():
    projects = parse_funding_rounds()
    filtered_projects = filter_projects(projects, min_funds=5)

    message = ""
    for project in filtered_projects:
        message += f"Проект: {project['name']}\nПривлечено: ${project['raised']}M\nКоманда: {project['team']}\nФонды: {', '.join(project['funds'])}\n\n"
    
    bot.send_message(chat_id='YOUR_CHAT_ID', text=message)

# Автоматическое обновление
def start_schedule():
    while True:
        send_funding_updates()
        time.sleep(3600)  # запуск каждые 1 час

# Запуск бота
if __name__ == '__main__':
    start_schedule()
