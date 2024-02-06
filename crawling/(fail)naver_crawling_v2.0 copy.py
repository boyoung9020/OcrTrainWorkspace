    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By  # Add this import line
    from bs4 import BeautifulSoup
    from multiprocessing import Pool
    import time
    import logging
    from datetime import datetime
    import os
    import subprocess
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC



    # Selenium 웹 드라이버 설정
    driver = webdriver.Chrome()


    category = [100, 101, 102, 103, 104, 105]

    # 웹 페이지 열기
    def crawl_category(category_info):
        key = category_info
        url = f"https://news.naver.com/section/{key}"
        driver.get(url)


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

    
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        wait = WebDriverWait(driver, 10)  # 최대 10초간 대기
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="newsct"]/div[4]/div/div[2]/a')))
        while True:
            try:      
                button_xpath = '//*[@id="newsct"]//div[contains(@class, "section")]/div/div[2]/a'
                button = driver.find_element(By.XPATH, button_xpath)
                button.click()
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(0.3) 

            except Exception as e:
                print(f"Exception: {e}")
                break

        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.HOME)



        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        unique_titles = set()
        contents = []

        for a_tag in soup.select("a strong"):
            title = a_tag.text.strip()
            if title not in unique_titles:
                unique_titles.add(title)
                contents.append(title)

        driver.quit()
        return contents 


    def get_all_contents():
        all_contents = []
        
        with Pool() as pool:
            results = pool.starmap(crawl_category, zip(category))
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