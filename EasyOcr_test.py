from easyocr.easyocr import Reader
import torch
import re
import os
import numpy as np
import cv2

# GPU 설정
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'

def get_files(path):
    file_list = []

    files = [f for f in os.listdir(path) if not f.startswith('.')]  # skip hidden files
    files.sort()
    abspath = os.path.abspath(path)
    for file in files:
        file_path = os.path.join(abspath, file)
        file_list.append(file_path)

    return file_list, len(file_list)

def draw_bounding_box(image, result):
    for bbox, string, confidence in result:
        points = bbox
        points = [(int(x), int(y)) for x, y in points]
        points = [np.array(points, dtype=np.int32)]
        image = cv2.polylines(image, points, isClosed=True, color=(0, 0, 255), thickness=2) 
        #cv2.polylines 함수의 color 매개변수는 (B, G, R) 형식의 튜플로 색상을 지정합니다. 
        #여기서 B는 파란색, G는 녹색, R은 빨간색을 나타냅니다. 따라서 빨간색을 사용하려면 (0, 0, 255)로 설정해야 합니다.
    return image


 

if __name__ == '__main__':
    script_directory = os.path.dirname(__file__)

    # Using custom model
    reader = Reader(['ko'], gpu=True,
                    model_storage_directory=os.path.join(script_directory, "user_network_dir/"),
                    user_network_directory=os.path.join(script_directory, "user_network_dir/"),
                    recog_network='custom')

    files, count = get_files(os.path.join(script_directory, r".\deep-text-recognition-benchmark\demo_image"))

    # 정규식을 이용하여 파일명에서 숫자 부분을 추출하여 정렬
    sorted_files = sorted(files, key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)
    print("GPU 사용 가능 여부:", torch.cuda.is_available())

    for file in sorted_files:
        filename = os.path.basename(file)
        result = reader.readtext(file)

        # 이미지를 읽어옵니다.
        image = cv2.imread(file)

        # bbox 그리기
        image_with_bbox = draw_bounding_box(image.copy(), result)

        # bbox가 그려진 이미지를 저장합니다.
        output_path = os.path.join(script_directory, r".\deep-text-recognition-benchmark\demo_image2", filename)
        cv2.imwrite(output_path, image_with_bbox)

        bbox = ' '.join([' '.join(map(str, bbox)) for bbox, _, _ in result])
        concatenated_string = ' '.join([string for bbox, string, _ in result])
        confidence_score = ''.join([str(confidence) for _, _, confidence in result])

        print(f"filename: '{filename}'      {bbox}      {concatenated_string}        {confidence_score}")