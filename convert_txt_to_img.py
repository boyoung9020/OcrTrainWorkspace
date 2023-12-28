import os
from PIL import Image, ImageDraw, ImageFont
import re
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

# def sanitize_filename(text):
#     return re.sub(r'[\\/:*?"<>|]', '_', text)


def create_text_images(text, font_path, validation_output_path, counter):
    words = text.split()  # 공백을 기준으로 단어 분리
    height = 120
    width = 1625

    image_paths = []  # 각 단어 이미지의 경로를 저장할 리스트
    labels = []  # 각 단어 이미지의 라벨을 저장할 리스트

    for word in words:
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)

        # 단어의 언어에 따라 폰트 선택
        if any('\u4e00' <= char <= '\u9fff' for char in word):
            font = ImageFont.truetype(chinese_font_path, size=70)
        else:
            font = ImageFont.truetype(korean_font_path, size=65)

        # 이미지에 단어 그리기
        text_size = draw.textsize(word, font)
        text_width, text_height = text_size
        position = ((width - text_width) // 2, (height - text_height) // 2)
        draw.text(position, word, font=font, fill='black')

        # 이미지 저장
        output_path = os.path.join(training_output_path, f"images\image_{counter:04d}.jpg")
        img.save(output_path)
        image_paths.append(output_path.replace(os.path.join(validation_output_path, ''), ''))
        labels.append(word)

        counter += 1

    return image_paths, labels


def create_text_image(text, font_path, validation_output_path, counter):
    # if len(text) < 30:
        height = 120

        # 기본 넓이 설정
        base_width = 1625
        img = Image.new('RGB', (base_width, height), color='white')
        draw = ImageDraw.Draw(img)

        # 한글 및 한문 폰트 경로
        chinese_font_path = os.path.join(script_directory, "font/SourceHanSansK-Regular.otf")
        korean_font_path = os.path.join(script_directory, "font/malgunbd.ttf")

        # 텍스트가 한문인 경우 한문 폰트 사용
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            font = ImageFont.truetype(chinese_font_path, size=70)
        else:
            font = ImageFont.truetype(korean_font_path, size=65)

        # 텍스트 그리기
        text_size = draw.textsize(text, font)

        # 텍스트 길이에 따라 동적으로 넓이 조정
        text_width, text_height = text_size
        width = max(base_width, text_width + 20)  # 최소 넓이는 기본 넓이보다 크게 설정
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)

        position = ((width - text_width) // 2, (height - text_height) // 2)
        draw.text(position, text, font=font, fill='black')

        output_path = os.path.join(validation_output_path, f"images/image_{counter:04d}.jpg")
        img.save(output_path)

        return output_path.replace(os.path.join(validation_output_path, ''), ''), text

    # return None




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

font_path = os.path.join(script_directory, "ko/malgunbd.ttf")
korean_font_path = os.path.join(script_directory, "font/malgunbd.ttf")
chinese_font_path = os.path.join(script_directory, "font/SourceHanSansK-Regular.otf")
text_file_path = os.path.join(script_directory, "headlinedatatxt/combine.txt")
validation_text_file_path = os.path.join(script_directory, "headlinedatatxt/all_category.txt")
training_output_path = os.path.join(script_directory, "step2/training/kordata/")
validation_output_path = os.path.join(script_directory, "step2/validation/kordata/")


images_folder_path = os.path.join(training_output_path, 'images')
if not os.path.exists(images_folder_path):
    os.makedirs(images_folder_path)
    
images_folder_path = os.path.join(validation_output_path, 'images')
if not os.path.exists(images_folder_path):
    os.makedirs(images_folder_path)

delete_files_in_directory(training_output_path)
delete_files_in_directory(validation_output_path)

with open(text_file_path, 'r', encoding='utf-8') as file, open(os.path.join(training_output_path, 'gt.txt'), 'w', encoding='utf-8') as gt_file:
    lines = file.readlines()
    counter = 0
    for line in tqdm(lines, desc="training데이터셋 생성 진행 중"):
        line = line.strip()
        image_paths, labels = create_text_images(line, font_path, training_output_path, counter)
        for image_path, label in zip(image_paths, labels):
            gt_file.write(f"{image_path}\t{label}\n")
        counter += 1
        

def count_images_in_directory(output_path):
    count = 0
    images_folder_path = os.path.join(output_path, 'images')
    for filename in os.listdir(images_folder_path):
        file_path = os.path.join(images_folder_path, filename)
        if os.path.isfile(file_path) and file_path.lower().endswith('.jpg'):
            count += 1
    return count



with open(validation_text_file_path, 'r', encoding='utf-8') as file, open(os.path.join(validation_output_path, 'gt.txt'), 'w', encoding='utf-8') as gt_file:
    total_images = count_images_in_directory(training_output_path)
    lines = file.readlines()
    counter = 0
    for line in tqdm(lines, desc="validation데이터셋 생성 진행 중"):
        line = line.strip()
        result = create_text_image(line, font_path, validation_output_path, counter)
        if result:
            image_path, text_content = result
            gt_file.write(f"{image_path}\t{text_content}\n")
            counter += 1

        ######## 이미지 생성 갯수 초과 여부 확인 #########
        if counter > int(total_images*0.4):
            break

            total_images*0.4

print(f"training 데이터셋이 {total_images}개 생성되었습니다.")
print(f"validation데이터셋 데이터셋이 {int(total_images*0.4)}개 생성되었습니다.")