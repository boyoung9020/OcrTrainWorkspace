import os
import easyocr
from PIL import Image
import re
import numpy as np
from natsort import natsort_keygen , natsorted




def contains_chinese_or_english(text):
    for char in text:
        if '\u4e00' <= char <= '\u9fff' or char.isalpha():
            return True
    return False

def contains_chinese_and_english(text):
    for char in text:
        if '\u4e00' <= char <= '\u9fff' and char.isalpha():
            return True
    return False

def contains_chinese_with_symbol(text):
    for i in range(len(text) - 1):
        if ('\u4e00' <= text[i] <= '\u9fff') and not text[i+1].isalnum():
            return True
    return False

def contains_english_with_symbol(text):
    for i in range(len(text) - 1):
        if text[i].isalpha() and not text[i+1].isalnum():
            return True
    return False

def save_to_text_file(text, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(text + "\n") 

def is_chinese(char):
    chinese_range = (0x4E00, 0x9FFF)  # 한자 범위
    return any(chinese_range[0] <= ord(c) <= chinese_range[1] for c in char)

def remove_special_characters(text):
    # 제거할 특수 문자 패턴 정의
    pattern = r'[\'"()_\\\/<>;|=:]'
    # 정규 표현식을 사용하여 특수 문자 제거
    clean_text = re.sub(pattern, '', text)
    return clean_text

    

def main() :
    sentence_list  = ""

    # 이미지 디렉토리 경로
    image_dir = r".\CRAFT-pytorch\output_segmentation"
    pth_dir = r".\ocr_model"

    reader = easyocr.Reader(['ch_tra', 'en'], gpu=True, model_storage_directory=pth_dir)
    after_reader = easyocr.Reader(['ko', 'en'], gpu=True, model_storage_directory=pth_dir)

    # 디렉토리 내의 모든 파일 목록 가져오기
    files = os.listdir(image_dir)

    # 이미지 파일만 필터링하여 처리
    image_files = [f for f in files if os.path.isfile(os.path.join(image_dir, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    image_groups = {}
    
    for file_name in image_files:
        group_number = int(file_name.split('_')[1])  # 파일 이름에서 그룹번호 추출하고 정수로 변환
        if group_number not in image_groups:
            image_groups[group_number] = []  # 새 그룹번호로 초기화
        image_groups[group_number].append(file_name)

    # 이미지 그룹을 번호순으로 정렬
    sorted_groups = natsorted(image_groups.items())

    # 각 그룹별로 파일들을 정렬
    for group_number, group_files in sorted_groups:
        # 파일들을 정렬: 파일명의 마지막 숫자에 대해 오름차순으로 정렬
        keygen = natsort_keygen(key=lambda x: x.split('_')[-1])
        group_files = natsorted(group_files, key=keygen)

        print(f"Results for group {group_number}:")
        sentence = ""

        for image_file in group_files:
            image_path = os.path.join(image_dir, image_file)
            img = Image.open(image_path)
            img_np = np.array(img)
            result = reader.readtext(img_np)
            hanja_list = set("色女官重氏郡田非情證免愛道酒對下農名市企軍父代京辰不宋與佛香訟獨龍多印協飛冬陰號全新藥現王公性弗太巨史黨盧朴母靑訴足前警株發天北視强順稅文半正韓高上檢明尹脫銀男濠産家賞苦災客行山二加可建年百過價作先月神兆丁有英訪車子硏才戰親來比野法心無南士李社美字亞手倍國中事日豊週大金曰故外弱式伊內淸質場甲說反癌誌")


            for detection in result:
                # 한글자이면서 한자이며 점수가 0.4 이상이고 해당 한자가 리스트에 있는 경우
                if len(detection[1]) == 1 and is_chinese(detection[1]) and detection[2] >= 0.4 and detection[1] in hanja_list: 
                    # print("1")
                    sentence += detection[1] + " "
                    # print(f"{detection[1]}  ({detection[2]:.2f})")
                elif contains_chinese_or_english(detection[1]):
                    # print("2")
                    # 검출된 문자가 score가 0.8이상이면서 한자나 영어일때 저장(한자 검출)
                    if detection[2] >= 0.8:
                        # print("3")
                                    
                        # 한문영어둘다 들어가있는경우
                        if contains_chinese_and_english(detection[1]):
                            # print("4")
                            # print(f"{detection[1]}  ({detection[2]:.2f})")
                            after_result = after_reader.readtext(img_np[detection[0][0][1]:detection[0][2][1], detection[0][0][0]:detection[0][1][0]])
                            for after_detection in after_result: 
                                # print(f"{after_detection[1]}  ({after_detection[2]:.2f})")
                                sentence += after_detection[1] + " "
                                
                        elif contains_chinese_and_english(detection[1]):
                            # print("4-1")
                            # print(f"{detection[1]}  ({detection[2]:.2f})")
                            after_result = after_reader.readtext(img_np[detection[0][0][1]:detection[0][2][1], detection[0][0][0]:detection[0][1][0]])
                            for after_detection in after_result: 
                                # print(f"{after_detection[1]}  ({after_detection[2]:.2f})")
                                sentence += after_detection[1] + " "         
                                
                        elif contains_english_with_symbol(detection[1]):
                            # print("4-2")
                            # print(f"{detection[1]}  ({detection[2]:.2f})")
                            after_result = after_reader.readtext(img_np[detection[0][0][1]:detection[0][2][1], detection[0][0][0]:detection[0][1][0]])
                            for after_detection in after_result: 
                                # print(f"{after_detection[1]}  ({after_detection[2]:.2f})")
                                sentence += after_detection[1] + " "   
                                
                        elif contains_chinese_with_symbol(detection[1]):
                            # print("5")
                            # print(f"{detection[1]}  ({detection[2]:.2f})")
                            after_result = after_reader.readtext(img_np[detection[0][0][1]:detection[0][2][1], detection[0][0][0]:detection[0][1][0]])
                            for after_detection in after_result: 
                                # print(f"{after_detection[1]}  ({after_detection[2]:.2f})")
                                sentence += after_detection[1] + " "
                                
                        
                        else : 
                            # print("6")
                            sentence += detection[1] + " "
                            # print(f"{detection[1]}  ({detection[2]:.2f})")
                        
                            
                    else: # 나머지 한글, 영어로 판단되는 문자는 after_reader로 돌림
                        # print("7")
                        # print(f"{detection[1]}  ({detection[2]:.2f})")
                        after_result = after_reader.readtext(img_np[detection[0][0][1]:detection[0][2][1], detection[0][0][0]:detection[0][1][0]])
                        for after_detection in after_result:
                            # print(f"{after_detection[1]}  ({after_detection[2]:.2f})")
                            sentence += after_detection[1] + " "
                # 한문과 특수문자가 붙어있을경우 after_reader로돌림
                elif contains_chinese_with_symbol(detection[1]):
                    # print("8")
                    # print(f"{detection[1]}  ({detection[2]:.2f})")
                    after_result = after_reader.readtext(img_np[detection[0][0][1]:detection[0][2][1], detection[0][0][0]:detection[0][1][0]])
                    for after_detection in after_result: 
                        # print(f"{after_detection[1]}  ({after_detection[2]:.2f})")
                        sentence += after_detection[1] + " "
                else: # 검출된 문자가 한글자이면서 한자이지만 리스트에 없는 경우, 또는 score가 0.8이상이지만 기호나 숫자일 때 after_reader로 돌림
                    # print("9")
                    # print(f"{detection[1]}  ({detection[2]:.2f})")
                    after_result = after_reader.readtext(img_np[detection[0][0][1]:detection[0][2][1], detection[0][0][0]:detection[0][1][0]])
                    for after_detection in after_result: 
                        # print(f"{after_detection[1]}  ({after_detection[2]:.2f})")
                        sentence += after_detection[1] + " "


        sentence = remove_special_characters(sentence)
        sentence_list += sentence
        
        save_to_text_file(sentence_list, "OCRresult.txt")

        print("Detected Sentence:", sentence)
        print()
        
        
if __name__ == "__main__":
    main()
