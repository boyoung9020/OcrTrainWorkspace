from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
from datetime import datetime
from multiprocessing import Pool
from functools import partial
import re
import subprocess
import logging

options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('--disable-logging')
#options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log.txt')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def clean_title(title):
    cleaned_title = re.sub(r'\([^)]*\)', '', title)
    cleaned_title = re.sub(r'\[[^\]]*\]', '', cleaned_title)
    return cleaned_title.strip()

category = {100: 200, 101: 400, 102: 600, 103: 90, 104: 100, 105: 90}

def crawl_category(category_info, position):
    key, value = category_info
    start_page = 1

    base_url1 = f"https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={key}#&date=%2000:00:00&"
    base_url2 = "page={}"

    unique_titles = set()
    contents = []

    category_name = ""
    if key == 100:
        category_name = '정치'
    elif key == 101:
        category_name = '경제'
    elif key == 102:
        category_name = '사회'
    elif key == 103:
        category_name = '생활/문화'
    elif key == 104:
        category_name = '세계'
    elif key == 105:
        category_name = 'IT/과학'
    else:  
        category_name = "???"    

    pbar = tqdm(range(start_page, value + 1),ascii=True, desc=category_name, unit="page", position=position)
    for page in pbar:
        base_url = base_url1 + base_url2
        url = base_url.format(page)
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        for dt_tag in soup.select("dt:not(.photo) a"):
            title = dt_tag.text.strip()
            if title not in unique_titles:
                unique_titles.add(title)
                cleaned_title = clean_title(title)
                item = {"title": cleaned_title}
                contents.append(item)

    driver.quit()
    return contents

def get_all_contents():
    all_contents = []
    positions = list(range(len(category)))
    
    with Pool() as pool:
        results = pool.starmap(crawl_category, zip(category.items(), positions))
        for contents in results:
            all_contents.extend(contents)
            
    return all_contents

def save_to_text(all_contents, backupfile, all_headline):
    with open(backupfile, "w", encoding="utf-8") as file:
        for content in all_contents:
            file.write(f"{content['title']}\n")
    with open(all_headline, 'a', encoding='utf-8') as file:
        for content in all_contents:
            file.write(f"{content['title']}\n")
    with open(all_headline, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    unique_lines = list(set(lines))
    with open(all_headline, 'w', encoding='utf-8') as outfile:
        outfile.writelines(unique_lines)
        print(f"중복제거 complete.. 총 headline count: {len(unique_lines)}")
        logging.info(f" 총 headline count: {len(unique_lines)}")

def open_notepad(all_headline):
    subprocess.run(["notepad.exe", all_headline], check=True)

if __name__ == "__main__":
    backup_time = datetime.now()
    backupdir = f'{backup_time.strftime("%y%m%d_%H%M")}'
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'headline_crawling_backup/{backupdir}'))
    backupfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'headline_crawling_backup/{backupdir}/{backupdir}.txt')
    all_headline = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'all_headline.txt')
    print(f'{backupdir}백업폴더 생성 완료')

    contents = get_all_contents()
    save_to_text(contents, backupfile, all_headline)
    open_notepad(all_headline)
