import requests
from bs4 import BeautifulSoup
import os


def download_image(url, folder):
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(folder, url.split("/")[-1]), 'wb') as file:
            file.write(response.content)


def scrape_news_site(news_url, folder='downloaded_images'):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Поиск всех ссылок на новости
    news_links = soup.find_all('a', class_='art')  # замените 'your-news-class' на реальный класс

    for link in news_links:
        news_page_response = requests.get(link.get('href'))
        news_page_soup = BeautifulSoup(news_page_response.text, 'html.parser')

        # Находим и скачиваем все изображения с страницы новости
        images = news_page_soup.find_all('img')
        for img in images:
            img_url = img.get('src')
            download_image(img_url, folder)


# Вызовите функцию со ссылкой на ваш новостной сайт
scrape_news_site('https://www.idnes.cz')
