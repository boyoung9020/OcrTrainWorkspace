from easyocr.easyocr import *
import torch
import re
import os



# GPU 설정
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'


def get_files(path):
    file_list = []

    files = [f for f in os.listdir(path) if not f.startswith('.')]  # skip hidden file
    files.sort()
    abspath = os.path.abspath(path)
    for file in files:
        file_path = os.path.join(abspath, file)
        file_list.append(file_path)

    return file_list, len(file_list)


if __name__ == '__main__':

    # # Using default model
    # reader = Reader(['ko'], gpu=True)
    script_directory = os.path.dirname(__file__)
    # Using custom model
    reader = Reader(['ko'], gpu=True,
                    model_storage_directory=os.path.join(script_directory, "user_network_dir/"),
                    user_network_directory=os.path.join(script_directory, "user_network_dir/"),
                    recog_network='custom')

    files, count = get_files(os.path.join(script_directory, r".\deep-text-recognition-benchmark\demo_image"))

    # 정규식을 이용하여 파일명에서 숫자 부분을 추출하여 정렬
    sorted_files = sorted(files, key=lambda x: int(re.search(r'\d+', x).group()))
    print("GPU 사용 가능 여부:", torch.cuda.is_available())

    for file in sorted_files:
        filename = os.path.basename(file)

        # Output the filename only once for each image
        print(f"filename: '{filename}'")

        result = reader.readtext(file)

        for (bbox, string, confidence) in result:
            print("confidence: %.4f, string: '%s'" % (confidence, string))