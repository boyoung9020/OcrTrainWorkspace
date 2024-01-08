from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import os
from datetime import datetime
import subprocess
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

backup_time = datetime.now()
backupdir = f'{backup_time.strftime("%y%m%d_%H%M")}'
os.makedirs(f'./headline_crawling_backup/{backupdir}')
print(f'{backupdir}백업폴더 생성 완료')


def clean_title(title):
    # 정규 표현식을 사용하여 괄호와 대괄호 안의 내용을 제거
    cleaned_title = re.sub(r'\([^)]*\)', '', title)
    cleaned_title = re.sub(r'\[[^\]]*\]', '', cleaned_title)
    return cleaned_title.strip()

# 정치       100       170페이지    198
# 경제       101       400페이지    340
# 사회       102       570페이지    482
# 생활/문화  103       80페이지     77
# 세계       104       100페이지    97  
# IT/과학    105       80페이지     70

category = {100: 2, 101: 4, 102: 6, 103: 9, 104: 1, 105: 9}

def get_naver_news_content(start_page=1):
    all_contents = []  # 각 카테고리의 결과를 모아서 반환할 리스트

    for key, value in category.items():
        base_url1 = f"https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={key}#&date=%2000:00:00&"
        base_url2 = "page={}"

        options = Options()
        options.add_argument("--headless")  # 백그라운드 모드로 실행 (창이 뜨지 않음)
        driver = webdriver.Chrome(options=options)

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
        else :  
            category_name = "???"    


        for page in tqdm(range(start_page, value + 1), desc=category_name, unit="page"):
            base_url = base_url1+base_url2
            url = base_url.format(page)
            driver.get(url)
            driver.implicitly_wait(10)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            for dt_tag in soup.select("dt:not(.photo) a"):
                title = dt_tag.text.strip()
                if title not in unique_titles:
                    unique_titles.add(title)
                    cleaned_title = clean_title(title)
                    item = {
                        "title": cleaned_title
                    }
                    
                    contents.append(item)
                
            
        driver.quit()  # 작업이 끝나면 드라이버 종료
        all_contents.extend(contents)  # 현재 카테고리의 결과를 전체 결과에 추가

    return all_contents  # 최종적으로 전체 결과 반환

def save_to_text(all_contents, filename=f"./headline_crawling_backup/{backupdir}/{backupdir}.txt"):
    # 백업용
    with open(filename, "w", encoding="utf-8") as file:
        for content in all_contents:
            file.write(f"{content['title']}\n")
    # 전체저장
    with open('all_headline.txt', 'a', encoding='utf-8') as file:
        for content in all_contents:
            file.write(f"{content['title']}\n")
        
    # 중복제거
    with open('all_headline.txt', 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    unique_lines = list(set(lines))
    # 다시쓰기
    with open('all_headline.txt', 'w', encoding='utf-8') as outfile:
        outfile.writelines(unique_lines)      
        print(f"중복제거 complete.. 총 headline count: {len(unique_lines)}")



def open_notepad(filename=f"./headline_crawling_backup/{backupdir}/{backupdir}.txt"):
    subprocess.run(["notepad.exe", filename], check=True)




if __name__ == "__main__":
    # 헤드라인 및 아티클 가져오기
    contents = get_naver_news_content()

    # 가져온 내용을 텍스트 파일에 저장
    save_to_text(contents)

    # 저장된 내용을 메모장으로 열기
    open_notepad()
