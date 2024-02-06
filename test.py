import os
from PIL import Image, ImageDraw, ImageFont
import re
from tqdm import tqdm
import random
from concurrent.futures import ProcessPoolExecutor
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


def create_text_images(args):
    line, font_path, save_output_path, counter, image_paths, labels = args

    target_height_ratio = 0.98
    width = 1625
    height = 120
    image_size = (width, height)
    font_size = 90

    img = Image.new('L', (width, height), color=238)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, size=font_size)

    filtered_words = ''.join(char for char in line if char not in '!#$()*/:;<>=?@[]^{/}|~')
    text_width, text_height = draw.textsize(filtered_words, font)
    x_position = ((image_size[0] - text_width) // 2) + 80
    y_position = ((image_size[1] - text_height) // 2) - 11

    character_spacing = -7
    current_x_position = x_position
    
    for char in filtered_words:
        char_width, _ = draw.textsize(char, font=font)
        draw.text((current_x_position, y_position), char, font=font, fill="black")
        current_x_position += char_width + character_spacing

    img = img.resize((1625, 120), Image.ANTIALIAS)

    output_path = os.path.join(save_output_path, f"images\image_{counter:04d}.jpg")
    img.save(output_path)
    image_paths.append(output_path.replace(os.path.join(save_output_path, ''), ''))
    labels.append(filtered_words)

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
    print(f"{directory} 삭제")


script_directory = os.path.dirname(__file__)

training_text_file_path = os.path.join(script_directory, "crawling/headlinedatatxt/training_all_category.txt")
training_split_text_file_path = os.path.join(script_directory, "crawling/headlinedatatxt/training_all_category_split.txt")
training_output_path = os.path.join(script_directory, "step2/training/kordata/")
font_path = os.path.join(script_directory, "font/malgunbd.ttf")

images_folder_path = os.path.join(training_output_path, 'images')
if not os.path.exists(images_folder_path):
    os.makedirs(images_folder_path)


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
        for sentence in tqdm(sentences, desc='Splitting', unit='sentence'):
            f.write(sentence + '\n')


def create_training_dataset():
    print(f"{training_split_text_file_path} 읽는중.....")
    with open(training_split_text_file_path, 'r', encoding='utf-8') as file, open(os.path.join(training_output_path, 'gt.txt'), 'w', encoding='utf-8') as gt_file:
        lines = file.readlines()
        counter = 0
        image_paths = []
        labels = []

        args_list = [
            (line.strip(), font_path, training_output_path, counter, image_paths, labels)
            for line in lines if len(line.strip()) < 26
        ]
        
        print("이미지 생성 들어감")
        with ProcessPoolExecutor() as executor:
            results = list(
                tqdm(
                    executor.map(create_text_images, args_list),
                    total=len(args_list),
                    desc="training데이터셋 생성 진행 중",
                )
            )

        for result in results:
            for image_path, label in zip(result[0], result[1]):
                gt_file.write(f"{image_path}\t{label}\n")
            counter += 1


if __name__ == '__main__':
    delete_files_in_directory(training_output_path)
    split_and_save(training_text_file_path, training_split_text_file_path)
    create_training_dataset()
