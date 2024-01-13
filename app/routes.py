from flask import render_template, request, redirect, url_for, send_from_directory
from app import app
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import uuid
from flask import send_file
from selenium.common.exceptions import StaleElementReferenceException


# Директория для сохранения изображений
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        images = scrape_images(url)
        return render_template('index.html', images=images)

    return render_template('index.html', images=None)

@app.route('/download/<filename>')
def download(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print("Filepath:", filepath)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        print("Error:", e)
        return "File not found"

def has_zpravy_in_url(url):
    return "zpravy" in url.lower()

def scrape_images(url):
    driver = webdriver.Chrome()
    driver.get(url)

    # Находим все ссылки
    all_links = [link.get_attribute('href') for link in driver.find_elements(By.CSS_SELECTOR, 'div.cols-par a')]


    # Фильтруем ссылки, оставляем только те, в которых есть "zpravy" в самой ссылке
    news_links = list(filter(has_zpravy_in_url, all_links))
    print(news_links)
    images = []
    print(news_links)
    for news_url in news_links:
        driver.get(news_url)

        # Явное ожидание появления элементов img_tags
        wait = WebDriverWait(driver, 10)
        img_tags = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'img')))

        for img_tag in img_tags:
            try:
                img_url = img_tag.get_attribute('src')
                if img_url:
                    img_data = requests.get(img_url).content
                    img_name = f"image_{uuid.uuid4()}.jpg"
                    img_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], img_name)
                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_data)
                    images.append({'name': img_name, 'path': img_path})
            except StaleElementReferenceException:
                continue  # Пропустить этот элемент и перейти к следующему
    driver.quit()
    return images

