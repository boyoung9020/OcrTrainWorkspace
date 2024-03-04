import os
import easyocr
from PIL import Image
import pytesseract
import re
import numpy as np

def contains_chinese(text):
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

def notcontains_chinese(text):
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return True




# 이미지 디렉토리 경로
image_dir = r".\CRAFT-pytorch\output_segmentation"
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'

# EasyOCR 인스턴스 생성
reader = easyocr.Reader(['en', 'ko'], gpu=False)
after_reader = easyocr.Reader(['ch_sim','en'], gpu=False)

# 디렉토리 내의 모든 파일 목록 가져오기
files = os.listdir(image_dir)

# 이미지 파일만 필터링하여 처리
image_files = [f for f in files if os.path.isfile(os.path.join(image_dir, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# 유효한 문자들을 필터링하는 정규 표현식
valid_chars_pattern = re.compile(r'[\uac00-\ud7af\uf900-\ufaff\u4e00-\u9fff\w\s%&-.]')


# 이미지 파일 그룹화
image_groups = {}
for image_file in image_files:
    prefix = image_file.split('_')[1]  # 파일 이름에서 그룹 식별자 추출
    if prefix not in image_groups:
        image_groups[prefix] = []
    image_groups[prefix].append(image_file)

# 이미지 그룹별로 텍스트 인식
for group_id, group_files in image_groups.items():
    print(f"Results for group {group_id}:")
    sentence= ""

    for image_file in group_files:
        # 이미지 경로
        image_path = os.path.join(image_dir, image_file)
        
        # 이미지 열기
        img = Image.open(image_path)
        
        # 이미지를 NumPy 배열로 변환
        img_np = np.array(img)
        
        # 이미지에서 텍스트 인식
        result = reader.readtext(img_np)

        for detection in result:
            if detection[2] <= 0.4:
                
                # confidence score가 0.3 이하인 경우 Tesseract로 다시 처리
                text = pytesseract.image_to_string(img, lang='kor+eng+chi_tra')
                tesseract_filtered_text = ''.join(re.findall(valid_chars_pattern, text))
                
                if tesseract_filtered_text.strip():  # 빈 문자열이 아니면 실행
                    if len(tesseract_filtered_text.replace('\n', '').replace('.','').replace(' ','')) >= 3:                        #3글자 이상이거나 개행문자
                        print("3글자 이상이거나 개행문자")
                        print(len(tesseract_filtered_text.replace('\n', '').replace('.','').replace(' ','')))
                        print(detection[1],tesseract_filtered_text.replace('\n', '').replace(".","").replace(" ",""))
                        # print(f"easyocr:  {detection[1]}({detection[2]:.2f}) {tesseract_filtered_text}")
                        
                        sentence += detection[1]+" "
                    
                    else:
                        
                        if any('\u4e00' <= char <= '\u9fff' for char in tesseract_filtered_text):
                            # 중국어가 포함되이는경우
                            print("중국어 포함_____________________")         
                            print(f"easyocr:  {detection[1]} , {detection[2]}   tesseract:  {tesseract_filtered_text}")
                            
                            sentence += tesseract_filtered_text.strip() +" "                      

                        else : 
                            print("중국어 포함안됌")
                            print(detection)
                            print(f"easyocr:  {detection[1]}({detection[2]:.2f}) {tesseract_filtered_text}")   
                            
                            sentence += detection[1] + " "                      
                        
                elif len(detection[1]) > 3:
                    print("4글자 이상감지")
                    print(f"{detection[1]}({detection[2]:.2f})")
                    sentence += detection[1]+ " "
                            
                else: # 빈 문자열일경우 실행
                    after_result = after_reader.readtext(img_np)
                    if after_result[0][2] > 0.7:
                        after_filtered_text = after_result[0][1] if after_result else ""
                        print(f"easyocr:  {detection[1]} , {detection[2]}   tesseract:  {tesseract_filtered_text}  after_easyocr: {after_filtered_text}")
                        
                        sentence += after_filtered_text+" "
                    else :
                        sentence += detection[1]+" "



            else:
                print("normal")
                # 유효한 문자만 필터링하여 출력
                filtered_text = ''.join(re.findall(valid_chars_pattern, detection[1]))
                print(f"{filtered_text}({detection[2]:.2f})")
                
                sentence += filtered_text+" "
                
    print()
    sentence = sentence.replace("'", "").replace('"', '')
    print ("완성된 문장 : " +sentence)

    print()
