import os
from PIL import Image, ImageDraw, ImageFont
import re
from tqdm import tqdm
import random
from itertools import islice
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


# def sanitize_filename(text):
#     return re.sub(r'[\\/:*?"<>|]', '_', text)


def create_text_images(words, font_path, save_output_path, counter):
    
        target_height_ratio = 0.9  # 이미지 배경 크기의 90%
        width = 1625
        height = int(120 * target_height_ratio)  # 텍스트 높이 설정
        max_font_size = 80  # 최대 폰트 크기

        image_paths = []  # 각 단어 이미지의 경로를 저장할 리스트
        labels = []  # 각 단어 이미지의 라벨을 저장할 리스트

        # 배경을 흰색(255)으로 하는 이미지 생성
        img = Image.new('L', (width, height), color=255)  # 'L' 모드는 8비트 흑백 이미지를 의미
        draw = ImageDraw.Draw(img)

        # 단어의 언어에 따라 폰트 선택
        if any('\u4e00' <= char <= '\u9fff' for char in words):
            font_size = max_font_size  # 폰트 크기를 최대 크기로 설정
            font = ImageFont.truetype(chinese_font_path, size=font_size)
        else:
            font_size = max_font_size  # 폰트 크기를 최대 크기로 설정
            font = ImageFont.truetype(font_path, size=font_size)

        # 텍스트의 너비 계산
        text_width, text_height = draw.textsize(words, font)
        print(text_width, text_height)

        # 텍스트의 간격을 동적으로 조절하여 이미지에 맞게 배치
        while text_width > width or text_height > height:
            font_size -= 1
            if font_size < 1:
                break  # 폰트 크기가 1보다 작아지면 종료
            font = ImageFont.truetype(font_path, size=font_size )
            text_width, text_height = draw.textsize(words, font)

        # 텍스트 위치 계산하여 조정
        position = ((width - text_width) // 2, ((height - text_height) // 2)-10)
        print((width - text_width) // 2, (height - text_height) // 2)

        # 폰트를 검은색(0)으로 설정하여 그리기
        draw.text(position, words, font=font, fill=0,spacing=25)  # 0은 팔레트에서의 검은색
    
        img = img.resize((1625, 120), Image.ANTIALIAS)

        # 이미지 저장
        output_path = os.path.join(save_output_path, f"images\image_{counter:04d}.png")
        img.save(output_path)
        image_paths.append(output_path.replace(os.path.join(save_output_path, ''), ''))
        labels.append(words)

        return image_paths, labels
    
    

def delete_files_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"파일 삭제 오류 {file_path}: {e}")


script_directory = os.path.dirname(__file__)

training_text_file_path = os.path.join(script_directory, "headlinedatatxt/all_category.txt")
training_split_text_file_path = os.path.join(script_directory, "headlinedatatxt/all_category_split.txt")
validation_text_file_path = os.path.join(script_directory, "headlinedatatxt/validation_all_category.txt")
validation_split_text_file_path = os.path.join(script_directory, "headlinedatatxt/validation_all_category_split.txt")
training_output_path = os.path.join(script_directory, "step2/training/kordata/")
test_output_path = os.path.join(script_directory, "step2/test/kordata/")
validation_output_path = os.path.join(script_directory, "step2/validation/kordata/")
test_text_file_path = os.path.join(script_directory, "headlinedatatxt/test_all_category.txt")
test_split_text_file_path = os.path.join(script_directory, "headlinedatatxt/test_all_category_split.txt")


chinese_font_path = os.path.join(script_directory, "font/SourceHanSansK-Regular.otf")
korean_font_path = os.path.join(script_directory, "font/malgunbd.ttf")
font_path =  os.path.join(script_directory, "font/malgunbd.ttf")


images_folder_path = os.path.join(training_output_path, 'images')
if not os.path.exists(images_folder_path):
    os.makedirs(images_folder_path)
    
images_folder_path = os.path.join(validation_output_path, 'images')
if not os.path.exists(images_folder_path):
    os.makedirs(images_folder_path)

delete_files_in_directory(training_output_path)
delete_files_in_directory(validation_output_path)
delete_files_in_directory(test_output_path)

def count_images_in_directory(output_path):
    count = 0
    images_folder_path = os.path.join(output_path, 'images')
    for filename in os.listdir(images_folder_path):
        file_path = os.path.join(images_folder_path, filename)
        if os.path.isfile(file_path) and file_path.lower().endswith('.jpg'):
            count += 1
    return count


def split_and_save(text_file_path, split_text_file_path):
    with open(text_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sentences = content.split()
    
    with open(split_text_file_path, 'w', encoding='utf-8') as f:
        for sentence in sentences:
            f.write(sentence + '\n')


split_and_save(training_text_file_path, training_split_text_file_path)
split_and_save(validation_text_file_path, validation_split_text_file_path)
split_and_save(test_text_file_path,test_split_text_file_path)


####### training데이터셋 생성
with open(training_split_text_file_path, 'r', encoding='utf-8') as file, open(os.path.join(training_output_path, 'gt.txt'), 'w', encoding='utf-8') as gt_file:
    lines = file.readlines()
    counter = 0
    for line in tqdm(lines, desc="training데이터셋 생성 진행 중"):
        line = line.strip()
        image_paths, labels = create_text_images(line, font_path, training_output_path, counter)
        for image_path, label in zip(image_paths, labels):
            gt_file.write(f"{image_path}\t{label}\n")
        counter += 1

        



######## validation데이터셋 생성
with open(validation_split_text_file_path, 'r', encoding='utf-8') as file, open(os.path.join(validation_output_path, 'gt.txt'), 'w', encoding='utf-8') as gt_file:
    total_images = count_images_in_directory(training_output_path)
    validation_images_count = int(total_images*0.01)
    lines = file.readlines()
    random.shuffle(lines)
    counter = 0
    for line in tqdm( lines, desc="validation데이터셋 생성 진행 중"):
        line = line.strip()
        if len(line) <32 :
            image_paths, labels = create_text_images(line, font_path, validation_output_path, counter)
            for image_path, label in zip(image_paths, labels):
                gt_file.write(f"{image_path}\t{label}\n")
            counter += 1
        

        if counter > 10:
            break


######## test데이터셋 생성
with open(test_split_text_file_path, 'r', encoding='utf-8') as file, open(os.path.join(test_output_path, 'gt.txt'), 'w', encoding='utf-8') as gt_file:
    lines = file.readlines()
    random.shuffle(lines)
    counter = 0
    for line in tqdm( lines, desc="test데이터셋 생성 진행 중"):
        line = line.strip()
        if len(line) <32 :
            image_paths, labels = create_text_images(line, font_path, test_output_path, counter)
            for image_path, label in zip(image_paths, labels):
                gt_file.write(f"{image_path}\t{label}\n")
            counter += 1
        
   










print(f"training 데이터셋이 {total_images}개 생성되었습니다.")
print(f"validation데이터셋 데이터셋이 {validation_images_count}개 생성되었습니다.")