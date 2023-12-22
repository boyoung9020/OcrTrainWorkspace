from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import subprocess
import re

# def split_title(title):
#     # title을 4등분하여 반환
#     quarter = len(title) // 4
#     first_quarter = title[:quarter]
#     second_quarter = title[quarter:2*quarter]
#     third_quarter = title[2*quarter:3*quarter]
#     fourth_quarter = title[3*quarter:]

#     # 각 등분에서 ...이나 ...로 시작하는 부분 처리
#     if second_quarter.startswith("…") or second_quarter.startswith("...") or second_quarter.startswith(".."):
#         first_quarter += second_quarter[0]  # ... 또는 … 추가
#         second_quarter = second_quarter[1:]

#     if fourth_quarter.startswith("…") or fourth_quarter.startswith("...") or fourth_quarter.startswith(".."):
#         third_quarter += fourth_quarter[0]  # ... 또는 … 추가
#         fourth_quarter = fourth_quarter[1:]

#     # 각 등분에서 ...이나 ...로 끝나는 부분 처리
#     if first_quarter.endswith("…") or first_quarter.endswith("...") or first_quarter.endswith(".."):
#         first_quarter = first_quarter[:-1]
#         second_quarter = first_quarter[-1] + second_quarter

#     if third_quarter.endswith("…") or third_quarter.endswith("...") or third_quarter.endswith(".."):
#         third_quarter = third_quarter[:-1]
#         fourth_quarter = third_quarter[-1] + fourth_quarter

#     return first_quarter, second_quarter, third_quarter, fourth_quarter

def clean_title(title):
    # 정규 표현식을 사용하여 괄호와 대괄호 안의 내용을 제거
    cleaned_title = re.sub(r'\([^)]*\)', '', title)
    cleaned_title = re.sub(r'\[[^\]]*\]', '', cleaned_title)
    return cleaned_title.strip()

# 정치       100       170페이지
# 경제       101       400페이지
# 사회       102       570페이지
# 생활/문화  103       80페이지
# 세계       104       100페이지
# IT/과학    105       80페이지


def get_naver_news_content(start_page=1, end_page=80):
    base_url = "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=105#&date=%2000:00:00&page={}"

    options = Options()
    # options.add_argument("--headless")  # 백그라운드 모드로 실행 (창이 뜨지 않음)
    driver = webdriver.Chrome(options=options)

    unique_titles = set()
    contents = []

    for page in tqdm(range(start_page, end_page + 1), desc="Progress", unit="page"):
        url = base_url.format(page)
        driver.get(url)

        # 페이지가 로딩될 때까지 기다릴 수 있는 코드 추가 (예: 10초)
        driver.implicitly_wait(10)

        # 현재 페이지의 내용 가져오기
        soup = BeautifulSoup(driver.page_source, "html.parser")

        for content in soup.select(".type06 li"):
            title = content.select_one("dt:not(.photo) a").text.strip()

            # 중복된 title은 무시
            if title not in unique_titles:
                unique_titles.add(title)

                cleaned_title = clean_title(title)

                # split_title 함수 사용
                # first_quarter, second_quarter, third_quarter, fourth_quarter = split_title(title)

                item = {
                    # "title_first_quarter": first_quarter,
                    # "title_second_quarter": second_quarter,
                    # "title_third_quarter": third_quarter,
                    # "title_fourth_quarter": fourth_quarter,
                    "title": cleaned_title
                }

                contents.append(item)

    driver.quit()  # 작업이 끝나면 드라이버 종료

    return contents


def save_to_text(contents, filename="output.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        for content in contents:
            # file.write(f"{content['title_first_quarter']}\n")
            # file.write(f"{content['title_second_quarter']}\n")
            # file.write(f"{content['title_third_quarter']}\n")
            # file.write(f"{content['title_fourth_quarter']}\n")
            file.write(f"{content['title']}\n")

def open_notepad(filename="output.txt"):
    subprocess.run(["notepad.exe", filename], check=True)


# 헤드라인 및 아티클 가져오기
contents = get_naver_news_content()

# 가져온 내용을 텍스트 파일에 저장
save_to_text(contents)

# 저장된 내용을 메모장으로 열기
open_notepad()
