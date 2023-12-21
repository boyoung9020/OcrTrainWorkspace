from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import subprocess


def split_title(title):
    # title을 반으로 나누어서 반환
    middle = len(title) // 2
    first_half = title[:middle]
    second_half = title[middle:]

    # 만약 second_half가 ...이나 ...로 시작한다면 중간에 추가
    if second_half.startswith("…") or second_half.startswith("...") or second_half.startswith(".."):
        first_half += second_half[0]  # ... 또는 … 추가
        second_half = second_half[1:]

    # 만약 first_half가 ...이나 ...로 끝난다면 중간으로 이동
    if first_half.endswith("…") or first_half.endswith("...") or first_half.endswith(".."):
        first_half = first_half[:-1]
        second_half = first_half[-1] + second_half

    return first_half, second_half



def get_naver_news_content(start_page=1, end_page=104):
    base_url = "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=104#&date=%2000:00:00&page={}"

    options = Options()
    #options.add_argument("--headless")  # 백그라운드 모드로 실행 (창이 뜨지 않음)
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

                ######이거
                first_half, second_half = split_title(title)

                item = {
                    ###이거
                    #"title": title,
                    "title_first_half": first_half,
                    "title_second_half": second_half,
                }

                contents.append(item)

    driver.quit()  # 작업이 끝나면 드라이버 종료

    return contents
###문자열 자르기
def save_to_text(contents, filename="output.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        for content in contents:
            file.write(f"{content['title_first_half']}\n")
            file.write(f"{content['title_second_half']}\n")

### defualt
#def save_to_text(contents, filename="output.txt"):
#    with open(filename, "w", encoding="utf-8") as file:
#        for content in contents:
#            file.write(f"{content['title']}\n")


def open_notepad(filename="output.txt"):
    subprocess.run(["notepad.exe", filename], check=True)

# 헤드라인 및 아티클 가져오기
contents = get_naver_news_content()

# 가져온 내용을 텍스트 파일에 저장
save_to_text(contents)

# 저장된 내용을 메모장으로 열기
open_notepad()
