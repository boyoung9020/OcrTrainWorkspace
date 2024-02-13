import os
from PIL import Image, ImageDraw, ImageFont , ImageOps
import re
from tqdm import tqdm
import random
import warnings
from concurrent.futures import ProcessPoolExecutor
import argparse
import sys
sys.path.append('.\deep-text-recognition-benchmark')
from create_lmdb_dataset import createDataset


warnings.filterwarnings("ignore", category=DeprecationWarning)

def create_text_images(args):
    line, font_directory, save_output_path, counter, tilt, full = args 

    try:
        height = 120  # 이미지의 높이 고정
        base_font_size = 80
        font_sizes = list(range(base_font_size - 10, base_font_size + 9))  
        font_size = random.choice(font_sizes)
        # print(f"fs={font_size} {line}")
       
        image_paths = []
        labels = []

        font_paths = get_all_fonts_in_directory(font_directory)
        selected_font_path = random.choice(font_paths)
        font = ImageFont.truetype(selected_font_path, size=font_size)
        text_width, text_height = font.getsize(line)

        if full:
            target_font_height = 105  # 원하는 폰트 세로 길이

            # 원하는 폰트 세로 길이를 얻기 위해 폰트 크기를 조정
            scale_factor = target_font_height / text_height
            font = ImageFont.truetype(selected_font_path, size=int(font_size * scale_factor))

        text_width, text_height = font.getsize(line)

        width = text_width + 40  
        image_size = (width, height)

        img = Image.new('RGB', image_size, color=(238, 238, 238))  
        draw = ImageDraw.Draw(img)

        filtered_words = ''.join(char for char in line if char not in '!#$()*/:;<>=?@[]^{/}|~')
        x_position = 60  
        y_position = (height - text_height) // 2

        character_spacing = -3 * scale_factor if full else -3
        current_x_position = x_position
        for char in filtered_words:
            char_width, _ = draw.textsize(char, font=font)
            draw.text((current_x_position, y_position), char, font=font, fill="black")
            current_x_position += char_width + character_spacing
    
        rotation_angle = 0
        tilt_probability = random.uniform(0, 1)  

        if tilt:
            if tilt_probability <= 0.7:   # 텍스트 회전 확률
                if len(filtered_words) == 1:
                    rotation_angle = random.uniform(-0.3, 0.3)
                elif 10 < len(filtered_words) < 30:
                    rotation_angle = random.randint(-1, 1)
                elif len(filtered_words) < 10:
                    rotation_angle = random.randint(-6, 6)
                elif font_size >= 80 or len(filtered_words) > 28:
                    rotation_angle = random.uniform(-0.3, 0.3)
                else:
                    rotation_angle = random.randint(-6, 6)

                img = img.rotate(rotation_angle, resample=Image.BICUBIC, expand=True, fillcolor=(238, 238, 238))  # resample=Image.BICUBIC을 추가하여 이미지를 회전할 때 Bicubic 보간

                img_height = img.size[1]
                if img_height > height:
                    upper = (img_height - height) // 2
                    lower = upper + height
                    img = img.crop((0, upper, width, lower))
                img = img.crop((50, 0, width - 28, height))

            else:
                rotation_angle = 0
        else:
            rotation_angle = 0

        # print(len(filtered_words),rotation_angle)

        output_path = os.path.join(save_output_path, f"images\image_{counter:04d}.jpg")
        img.save(output_path)
        image_paths.append(output_path.replace(os.path.join(save_output_path, ''), ''))
        labels.append(filtered_words)

        return image_paths, filtered_words  
    
    except Exception as e:
        print(f"Exception: {e}")
        raise

def delete_files_in_directory(directory):
    print(f"{directory} 삭제중...")
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"파일 삭제 오류 {file_path}: {e}")

def count_images_in_directory(output_path):
    print(f"{output_path} count 중.. ")
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
    sentences = list(filter(None, sentences))  # 빈 문자열을 제거


    with open(split_text_file_path, 'w', encoding='utf-8') as f:
        for sentence in tqdm(sentences, desc='Splitting', unit='sentence'):
            f.write(sentence + '\n')


def create_training_dataset(args):
    print("-" * 40, "training_data 생성", "-" * 40)
    tilt = args.tilt
    full = args.full
    print("tilt: ",tilt) 
    print("full: ",full)     
    training_text_file_path = args.training_text_file_path
    training_split_text_file_path = args.training_split_text_file_path
    training_output_path = args.training_output_path
    font_directory = args.font_directory

    split_and_save(training_text_file_path, training_split_text_file_path)
    
    print(f"{training_split_text_file_path} 읽는중.....")
    with open(training_split_text_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    delete_files_in_directory(training_output_path)

    with open(training_split_text_file_path, 'r', encoding='utf-8') as file, open(os.path.join(training_output_path, 'gt.txt'), 'w', encoding='utf-8') as gt_file:
        
        with ProcessPoolExecutor() as executor:
            results = list(tqdm(executor.map(create_text_images, [(line, font_directory, training_output_path, counter, tilt, full) for counter, line in enumerate(lines, start=1)], chunksize=50), total=len(lines), desc='Creating Training Data', unit='image'))

            for result in results:
                image_paths_str = ', '.join(result[0])  # 쉼표로 구분된 문자열로 변환
                gt_file.write(f"{image_paths_str}\t{result[1]}")
    print('-' * 102)


def create_validation_dataset(args):
    print("-" * 40, "validation_data 생성", "-" * 40)
    tilt = args.tilt
    full = args.full
    print("tilt: ",tilt) 
    print("full: ",full) 
    validation_text_file_path = args.training_text_file_path
    validation_split_text_file_path = args.validation_split_text_file_path
    validation_output_path = args.validation_output_path
    font_directory = args.font_directory
    
    split_and_save(validation_text_file_path, validation_split_text_file_path)
    print(f"{validation_split_text_file_path} 읽는중.....")
    with open(validation_split_text_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        random.shuffle(lines) 
    delete_files_in_directory(validation_output_path)
        
    with open(validation_split_text_file_path, 'r', encoding='utf-8') as file, open(os.path.join(validation_output_path, 'gt.txt'), 'w', encoding='utf-8') as gt_file:
        total_images = count_images_in_directory(args.training_output_path)
        validation_images_count = int(total_images*0.001)
        with ProcessPoolExecutor() as executor:
            results = list(tqdm(executor.map(create_text_images, [(line, font_directory, validation_output_path, counter, tilt,full) for counter, line in enumerate(lines, start=1) if counter <= validation_images_count], chunksize=50), total=validation_images_count, desc='Creating Validation Data', unit='image'))
            for result in results:
                image_paths_str = ', '.join(result[0])  # 쉼표로 구분된 문자열로 변환
                gt_file.write(f"{image_paths_str}\t{result[1]}")
    print('-' * 102)
                         

def create_test_dataset(args):
    print("-" * 40, "test_data 생성", "-" * 40)
    tilt = args.tilt
    full = args.full
    print("tilt: ",tilt) 
    print("full: ",full)     
    new_test_text_file_path = args.new_test_text_file_path
    test_output_path = args.test_output_path
    font_directory = args.font_directory
    
    print(f"{new_test_text_file_path} 읽는중.....")
    with open(new_test_text_file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()] 
    delete_files_in_directory(test_output_path)
    
    with open(new_test_text_file_path, 'r', encoding='utf-8') as file, open(os.path.join(test_output_path, 'gt.txt'), 'w', encoding='utf-8') as gt_file:
        filtered_lines = [line.strip() for line in lines if len(line.strip()) <= 30]  # 앞뒤 공백 제거 후 길이가 30 이하인 줄만 선택
        with ProcessPoolExecutor() as executor:
            results = list(tqdm(executor.map(create_text_images, [(filtered_lines, font_directory, test_output_path, counter, tilt , full) for counter, filtered_lines in enumerate(filtered_lines, start=1) ], chunksize=50), total=len(filtered_lines), desc='Creating Training Data', unit='image'))
            
            for result in results:
                image_paths_str = ', '.join(result[0])  # 쉼표로 구분된 문자열로 변환
                gt_file.write(f"{image_paths_str}\t{result[1]}\n")  
    print('-' * 102)



def get_all_fonts_in_directory(font_directory):
    font_paths = [os.path.join(font_directory, file) for file in os.listdir(font_directory) if file.lower().endswith(('.ttf', '.otf'))]
    return font_paths


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some integers.')
    script_directory = os.path.dirname(__file__)
    
    parser.add_argument(
        '-t',
        '--tilt',
        action='store_true',
        help='tilt value of text'
    )

    parser.add_argument(
        '-td',
        '--training_data',
        action='store_true',
        help='create training dataset'
    )
    parser.add_argument(
        '-vd',
        '--validation_data',
        action='store_true',
        help='create validation dataset'
    )
    parser.add_argument(
        '-tdvd',
        '--training_validation_data',
        action='store_true',
        help='create test dataset'
    )
    parser.add_argument(
        '-ttd',
        '--test_data',
        action='store_true',
        help='create test dataset'
    )
    parser.add_argument(
        '-lmdb',
        '--create_lmdb',
        action='store_true',
        help='create lmdb'
    )
    parser.add_argument(
        '-f',
        '--full',
        action='store_true',
        help='set font height size'
    )
    parser.add_argument(
        '--training_gt_file_path',
        default=os.path.join(script_directory, "step2/training/kordata/gt.txt"),
        help='path to training text file'
    )
    parser.add_argument(
        '--training_lmdb_output_path',
        default=os.path.join(script_directory, "step3/training/kordata/"),
        help='path to training text file'
    )
    parser.add_argument(
        '--validation_gt_file_path',
        default=os.path.join(script_directory, "step2/validation/kordata/gt.txt"),
        help='path to training text file'
    )
    parser.add_argument(
        '--validation_lmdb_output_path',
        default=os.path.join(script_directory, "step3/validation/kordata/"),
        help='path to training text file'
    )
    parser.add_argument(
        '--training_text_file_path',
        default=os.path.join(script_directory, "crawling/headlinedatatxt/training_all_category.txt"),
        help='path to training text file'
    )
    parser.add_argument(
        '--training_split_text_file_path',
        default=os.path.join(script_directory, "crawling/headlinedatatxt/training_all_category_split.txt"),
        help='path to training split text file'
    )
    parser.add_argument(
        '--validation_text_file_path',
        default=os.path.join(script_directory, "crawling/headlinedatatxt/validation_all_category.txt"),
        help='path to validation text file'
    )
    parser.add_argument(
        '--validation_split_text_file_path',
        default=os.path.join(script_directory, "crawling/headlinedatatxt/validation_all_category_split.txt"),
        help='path to validation split text file'
    )
    parser.add_argument(
        '--training_output_path',
        default=os.path.join(script_directory, "step2/training/kordata/"),
        help='path to training output directory'
    )
    parser.add_argument(
        '--test_output_path',
        default=os.path.join(script_directory, "step2/test/kordata/"),
        help='path to test output directory'
    )
    parser.add_argument(
        '--validation_output_path',
        default=os.path.join(script_directory, "step2/validation/kordata/"),
        help='path to validation output directory'
    )
    parser.add_argument(
        '--test_text_file_path',
        default=os.path.join(script_directory, "crawling/headlinedatatxt/test_all_category.txt"),
        help='path to test text file'
    )
    parser.add_argument(
        '--new_test_text_file_path',
        default=os.path.join(script_directory, "crawling/headlinedatatxt/new_test_all_category.txt"),
        help='path to new test text file'
    )
    parser.add_argument(
        '--test1_text_file_path',
        default=os.path.join(script_directory, "crawling/headlinedatatxt/test1.txt"),
        help='path to test1 text file'
    )
    parser.add_argument(
        '--words_text_file_path',
        default=os.path.join(script_directory, "crawling/headlinedatatxt/words.txt"),
        help='path to words text file'
    )
    parser.add_argument(
        '--test_split_text_file_path',
        default=os.path.join(script_directory, "crawling/headlinedatatxt/test_all_category_split.txt"),
        help='path to test split text file'
    )
    parser.add_argument(
        '--chinese_font_path',
        default=os.path.join(script_directory, "font/SourceHanSansK-Regular.otf"),
        help='path to chinese font file'
    )
    parser.add_argument(
        '--korean_font_path',
        default=os.path.join(script_directory, "font/malgunbd.ttf"),
        help='path to korean font file'
    )
    parser.add_argument(
        '--font_path',
        default=os.path.join(script_directory, "font/KoreanGD17R.ttf"),
        help='path to font file'
    )
    parser.add_argument(
        '--font_directory',
        default=os.path.join(script_directory, "font"),
        help='path to font directory'
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    for output_path in [args.training_output_path, args.validation_output_path, args.test_output_path]:
        args.images_folder_path = os.path.join(output_path, 'images')
        if not os.path.exists(args.images_folder_path):
            os.makedirs(args.images_folder_path)
            
    if args.training_data:
        create_training_dataset(args)
    elif args.validation_data:
        create_validation_dataset(args)
    elif args.test_data:
        create_test_dataset(args)
    elif args.training_validation_data:
        create_training_dataset(args)
        create_validation_dataset(args)
    else:
        print("No dataset type specified")

    if args.create_lmdb:
        createDataset(args.training_output_path,args.training_gt_file_path,args.training_lmdb_output_path)
        createDataset(args.validation_output_path,args.validation_gt_file_path,args.validation_lmdb_output_path)
    else:
        print("no create_lmdb")    


if __name__ == "__main__":
    # split_and_save(test_text_file_path, test_split_text_file_path)
    main()
