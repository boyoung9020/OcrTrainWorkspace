import os
from PIL import Image, ImageDraw, ImageFont
import re
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

def sanitize_filename(text):
    return re.sub(r'[\\/:*?"<>|]', '_', text)

def create_text_image(text, font_path, output_directory, counter):
    if ' ' in text and len(text) <= 30:
        height = 120
        width = 1625

        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)

        # 한글 및 한문 폰트 경로

        # 텍스트가 한문인 경우 한문 폰트 사용
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            font = ImageFont.truetype(chinese_font_path, size=65)
        else:
            font = ImageFont.truetype(korean_font_path, size=65)

        # 텍스트 그리기
        text_size = draw.textsize(text, font)
        text_width, text_height = text_size
        position = ((width - text_width) // 2, (height - text_height) // 2)
        draw.text(position, text, font=font, fill='black')

        sanitized_text = sanitize_filename(text)

        output_path = os.path.join(output_directory, f"images\image_{counter:04d}.jpg")
        img.save(output_path)

        return output_path.replace(os.path.join(output_directory, ''), ''), text

    return None

def delete_files_in_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"파일 삭제 오류 {file_path}: {e}")

font_path = "C:/Users/gemiso/Desktop/EasyocrWorkspace/ko/malgunbd.ttf"
korean_font_path = "C:/Users/gemiso/Desktop/EasyocrWorkspace/font/malgunbd.ttf"
chinese_font_path = "C:/Users/gemiso/Desktop/EasyocrWorkspace/font/SourceHanSansK-Regular.otf"  # 적절한 중국어(한문) 폰트 경로로 변경
text_file_path = "C:/Users/gemiso/Desktop/EasyocrWorkspace/headlinedatatxt/combine.txt"
output_directory = "C:/Users/gemiso/Desktop/EasyocrWorkspace/headlinedataimg/"
gt_file_path = "C:/Users/gemiso/Desktop/EasyocrWorkspace/headlinedataimg/gt.txt"

# Create the 'images' folder if it doesn't exist
images_folder_path = os.path.join(output_directory, 'images')
if not os.path.exists(images_folder_path):
    os.makedirs(images_folder_path)

delete_files_in_directory(images_folder_path)

with open(text_file_path, 'r', encoding='utf-8') as file, open(gt_file_path, 'w', encoding='utf-8') as gt_file:
    lines = file.readlines()
    counter = 0
    for line in tqdm(lines, desc="이미지 생성 진행 중"):
        line = line.strip()
        result = create_text_image(line, font_path, output_directory, counter)
        if result:
            image_path, text_content = result
            gt_file.write(f"{image_path}\t{text_content}\n")
            counter += 1

        ######## 이미지생성 갯수#########
        if counter == 5000:
            break    

print(f"이미지와 텍스트 파일이 '{output_directory}'와 '{gt_file_path}'로 저장되었습니다.")
