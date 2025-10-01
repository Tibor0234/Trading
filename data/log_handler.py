import os
import time
import pandas as pd
import csv
from playwright.sync_api import sync_playwright
from PIL import Image
from config import activity_log_path, chart_log_path
from data.time_provider import TimeProvider

def clear_chart_log_dir():
    os.makedirs(chart_log_path, exist_ok=True)

    for filename in os.listdir(chart_log_path):
        file_path = os.path.join(chart_log_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                pass
                #print('A fájl nem törölhető.', e)

def init_log_file():
    with open(activity_log_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['datetime', 'event', 'attachment_or_comment'])

def log_event(event, attachment_or_comment = '-'):
    time_as_dt = pd.to_datetime(TimeProvider.instance.get_time(), unit='s')
    time_as_string = time_as_dt.strftime("%Y/%m/%d_%H:%M:%S")

    row = [time_as_string, event, attachment_or_comment]
    try:
        with open(activity_log_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)
    except Exception as e:
        print('Hiba a log fájlba íráskor:', e)

def log_chart(symbol, timeframe, fig):
    now_as_dt = pd.to_datetime(int(time.time() * 1000), unit='ms')
    now_as_string = now_as_dt.strftime("%Y-%m-%d_%H-%M-%S-%f")

    filename = f'{symbol}-{timeframe}-{now_as_string}.html'
    filename_modified = filename.replace('/USDT:USDT', '')

    file_path = os.path.join(chart_log_path, filename_modified)
    fig.write_html(file_path)

    return file_path

def make_screenshot(html_path: str) -> str | None:
    img_path = html_path.replace('.html', '.png')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1200, "height": 800})

        url = f'file:///{html_path.replace(os.sep, "/")}'
        page.goto(url)

        page.screenshot(path=img_path, full_page=False)

        browser.close()

    img = Image.open(img_path)
    w, h = img.size
    if w > 40 and h > 40:
        img.crop((20, 20, w-20, h-20)).save(img_path)

    return img_path