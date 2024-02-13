import os
from pathlib import Path
import lmdb
import io
from PIL import Image

def read_lmdb(lmdb_path, key):
    # 입력된 lmdb 경로를 절대 경로로 변환
    lmdb_path = Path(lmdb_path).resolve()
    if not lmdb_path.exists():
        print(f"Error: {lmdb_path} does not exist")
        return

    env = lmdb.open(str(lmdb_path), readonly=True, lock=False)
    with env.begin() as txn:
        value = txn.get(key)
        if value is not None:
            print(f"Key: {key}, Value: {value.decode()}")  # 레이블 값 출력
            image_bytes = txn.get(b'image-001500000')  # 이미지 바이트 가져오기
            if image_bytes:
                image = Image.open(io.BytesIO(image_bytes))  # 이미지 열기
                image.show()  # 이미지 창에 표시
            else:
                print("No image found for the given key.")
        else:
            print(f"No value found for key: {key}")
    env.close()

if __name__ == "__main__":
    lmdb_dir_path = "./step3/training/kordata/"  # LMDB 디렉토리의 경로
    key_to_check = b"label-001500000"  # 확인하고자 하는 키
    read_lmdb(lmdb_dir_path, key_to_check)
