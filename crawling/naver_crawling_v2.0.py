from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
import logging
import shutil



chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument('--headless')
logging.getLogger('selenium').setLevel(logging.WARNING)
driver = webdriver.Chrome(options=chrome_options)


category = [100, 101, 102, 103, 104, 105]
output_file_path = "headlines.txt"
contents = []  # Change from set to list


def get_category_name(key):
    if key == 100:
        return '정치'
    elif key == 101:
        return '경제'
    elif key == 102:
        return '사회'
    elif key == 103:
        return '생활/문화'
    elif key == 104:
        return '세계'
    elif key == 105:
        return 'IT/과학'
    else:
        return "???"

def crawl_category(category_info, contents):
    key = category_info
    category_name = get_category_name(key)
    url = f"https://news.naver.com/section/{key}"
    driver.get(url)
    
    print(f"{category_name} 카테고리 크롤링 중...")

    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    count = 0
    while True:
        try:
            button_xpath = '//*[@id="newsct"]//div[contains(@class, "section")]/div/div[2]/a'
            button = driver.find_element(By.XPATH, button_xpath)
            button.click()
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(0.1)
            count += 1

        except Exception as e:
            print("더보기 버튼 모두 눌림")
            break

    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.HOME)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    category_contents = []  

    for a_tag in soup.select("a strong"):
        title = a_tag.text.strip()
        contents.append({"title": title, "category": category_name})
        category_contents.append({"title": title, "category": category_name})

    print(f"{category_name} 카테고리 크롤링 완료")
    
    return category_contents

def get_all_contents():
    all_contents = []

    for key in category:
        category_contents = crawl_category(key, contents)
        all_contents.extend(category_contents)

    driver.quit()
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
        print(f"중복 제거 complete.. 총 headline count: {len(unique_lines)}")
        logging.info(f" 총 headline count: {len(unique_lines)}")

def open_notepad(all_headline):
    os.system(f"start notepad.exe {all_headline}")

if __name__ == "__main__":
    start_time = time.time()

    backup_time = datetime.now()
    backupdir = f'{backup_time.strftime("%y%m%d_%H%M")}'
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'headline_crawling_backup/{backupdir}'))
    backupfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'headline_crawling_backup/{backupdir}/{backupdir}.txt')
    all_headline = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'all_headline.txt')
    target_file_path = os.path.join("headlinedatatxt", "training_all_category.txt")

    print(f'{backupdir}백업폴더 생성 완료')

    contents = get_all_contents()
    save_to_text(contents, backupfile, all_headline)
    open_notepad(all_headline)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"총 걸린 시간: {elapsed_time:.2f}초")

    while True:
        user_input = input("training_all_category.txt 업데이트를 하시겠습니까? (y/n): ").strip().lower()
        if user_input == 'y':
            shutil.copyfile(all_headline, target_file_path)
            print("training_all_category 업데이트 완료")
            break
        elif user_input == 'n':
            print("업데이트를 하지 않습니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 입력해주세요.")