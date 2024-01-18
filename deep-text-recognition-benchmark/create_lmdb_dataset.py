import fire
import os
import lmdb
import cv2
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from PIL import Image
import time

def checkImageIsValid(imageBin):
    if imageBin is None:
        return False
    imageBuf = np.frombuffer(imageBin, dtype=np.uint8)
    img = cv2.imdecode(imageBuf, cv2.IMREAD_GRAYSCALE)
    imgH, imgW = img.shape[0], img.shape[1]
    return imgH * imgW != 0

def writeCache(args):
    env, cache = args
    with env.begin(write=True) as txn:
        for k, v in cache.items():
            txn.put(k, v)

def createDataset(inputPath, gtFile, outputPath, checkValid=True, chunksize=1000):
    os.makedirs(outputPath, exist_ok=True)
    start_time = time.time() 
    env_path = outputPath  # LMDB path
    env = lmdb.open(env_path, map_size=10000000000)
    cache = {}
    cnt = 1

    with open(gtFile, 'r', encoding='utf-8') as data:
        datalist = data.readlines()

    nSamples = len(datalist)
    with ThreadPoolExecutor(max_workers=4) as executor, tqdm(total=nSamples, ascii=True, desc='Creating LMDB') as pbar:
        args_list = []
        for i in range(0, nSamples, chunksize):
            chunk_data = datalist[i:i + chunksize]
            args_list = []
            for j, line in enumerate(chunk_data):
                imagePath, label = line.strip('\n').split('\t')
                imagePath = Path(inputPath) / imagePath

                if not imagePath.exists():
                    print('%s does not exist' % imagePath)
                    continue

                with open(imagePath, 'rb') as f:
                    imageBin = f.read()

                if checkValid and not checkImageIsValid(imageBin):
                    print('%s is not a valid image' % imagePath)
                    continue

                imageKey = f'image-{cnt:09d}'.encode()
                labelKey = f'label-{cnt:09d}'.encode()
                cache[imageKey] = imageBin
                cache[labelKey] = label.encode()

                cnt += 1

            executor.submit(writeCache, (env, cache.copy()))  # 각 청크 당 하나의 트랜잭션을 생성하도록 변경
            cache = {}

            pbar.update(len(chunk_data))

    nSamples = cnt - 1
    cache['num-samples'.encode()] = str(nSamples).encode()
    writeCache((env, cache))
    print(f'Created dataset with {nSamples} samples')
    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Total time taken: %.2f seconds' % elapsed_time)

if __name__ == '__main__':
    fire.Fire(createDataset)
