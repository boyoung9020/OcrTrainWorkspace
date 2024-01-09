# ocrTrain
deep-text-recognition-benchmark를 이용한 OCR 사용자모델 학습

dependency : torch, lmdb, torchvision, nltk, natsort, pillow, requests, opencv-python, tqdm, fire (use `pip install [library]` command)

# 1. 학습 데이터 생성

### naver_crawling.py
* 네이버 뉴스종합 홈에서 정치/경제/사회/생활/문화/IT/과학/세계 category의 headline을 페이지끝까지 crawling해 필요없는 특수문자들을 걸러서 종합한다.
* crawling후 결과는 다음 두 txt 파일로 나뉘어서 저장된다.
  

  * crawling한 결과를 일자별로 저장
  * 매일 crawling한 뉴스기사를 가져와서 이전날의 headline과 중복을 제거한 .txt
  


<img src="https://github.com/boyoung9020/OcrTrainWorkspace/assets/154112385/191ddce1-d970-4629-8e6f-87a4c804f8ad" width="400" height="500"/>

<br>
<br>

# 2. 가져온 healine을 공백 기준 단어로 잘라 데이터화
 * 학습단어 약 100만개 생성

### images/ 속 .jpg 이미지들을 생성, gt.txt파일에 이미지 path와 headline 텍스트로 key/value값을 작성후 저장

<br>
 
![gt파일](https://github.com/boyoung9020/OcrTrainWorkspace/assets/154112385/d6bb1f8f-8506-4e55-901e-e23c961ab84e)


<br>
<br>

# 3. lmdb 포맷으로 데이터셋 생성


### deep-text-recognition-benchmark의 create_lmdb_dataset.py 모듈로 lmdb셋 생성

command

```bash
$ cd ../../..
$ python create_lmdb_dataset.py
--inputPath ".\OcrTrainWorkspace\step2\training\kordata"
--gtFile ".\OcrTrainWorkspace\step2\training\kordata\gt.txt"
--outputPath ".\OcrTrainWorkspace\step3\training\kordata"
```
```bash
$ python create_lmdb_dataset.py
--inputPath ".\OcrTrainWorkspace\step2\validation\kordata"
--gtFile ".\OcrTrainWorkspace\step2\validation\kordata\gt.txt"
--outputPath ".\OcrTrainWorkspace\step3\validation\kordata"
```


### stage2 디렉토리 구조
다음과 같은 디렉토리 구조가 형성된다.
```bash
/stage2
├── /training
│     └── kordata
│           ├── data.mdb
│           └── lock.mdb
│
└── /validation
       └── kordata
             ├── data.mdb
             └── lock.mdb
```

<br>

# 4. 사용자 모델 학습(training)
여기서부턴 gpu 환경에서만 가능하다.

### NONE-VGG-BILSTM-CTC Scartch 학습

```bash
$ cd deep-text-recognition-benchmark
$ python train.py
--train_data ".\OcrTrainWorkspace\step3\training"
--valid_data ".\OcrTrainWorkspace\step3\validation"
--Transformation None --FeatureExtraction "VGG" --SequenceModeling "BiLSTM" --Prediction "CTC" 
```
<br>

### NONE-VGG-BILSTM-CTC FT 학습

```bash
$ cd deep-text-recognition-benchmark
$ python train.py
--train_data ".\OcrTrainWorkspace\step3\training"
--valid_data ".\OcrTrainWorkspace\step3\validation"
--Transformation None --FeatureExtraction "VGG" --SequenceModeling "BiLSTM" --Prediction "CTC"
--saved_model ".\OcrTrainWorkspace\deep-text-recognition-benchmark\models\None-VGG-BiLSTM-CTC.pth" --FT
```
<br>

### TPS-RESNET-BILSTM-ATTN Scartch 학습

```bash
$ cd deep-text-recognition-benchmark
$ python train.py
--train_data ".\OcrTrainWorkspace\step3\training"
--valid_data ".\OcrTrainWorkspace\step3\validation"
--Transformation "TPS" --FeatureExtraction "ResNet" --SequenceModeling "BiLSTM" --Prediction "Attn"
```
<br>

### TPS-RESNET-BILSTM-ATTN FT 학습

```bash
$ cd deep-text-recognition-benchmark
$ python train.py
--train_data ".\OcrTrainWorkspace\step3\training"
--valid_data ".\OcrTrainWorkspace\step3\validation"
--Transformation "TPS" --FeatureExtraction "ResNet" --SequenceModeling "BiLSTM" --Prediction "Attn"
--saved_model ".\OcrTrainWorkspace\deep-text-recognition-benchmark\models\TPS-RESNET-BILSTM-ATTN
.pth" --FT

```
<br>

### 학습 옵션
train.py의 옵션을 커스텀해 학습 가능하다.
- `--train_data` : path to training dataset
- `--valid_data` : path to validation dataset
- `--select_data`: directories to use as training dataset(default = 'basic-skew')
- `--batch_ratio` 
- `--Transformation` : choose one - None|TPS
- `--FeatureExtraction`: choose one - VGG|RCNN|ResNet 
- `--SequenceModeling`: choose one - None|BiLSTM
- `--Prediction` : choose one - CTC|Attn
- `--data_filtering_off` : skip data filtering when creating LmdbDataset
- `--valInterval` : Interval between each validation
- `--workers` :  number of data loading workers
- `--distributed`
- `--imgW` : the width of the input image
- `--imgH` : the height of the input image

<br>

### 학습 모습

<img src="https://github.com/boyoung9020/OcrTrainWorkspace/assets/154112385/8a01396c-df4e-4359-bcfe-4ef49831394c" width="500" height="400"/>

<br>

### 학습 결과
- ocr_dtrb/deep-text-recognition-benchmark/saved_models 디렉토리에 학습시킨 모델별 일자별로 `current_accuracy.pth`, `best_accuracy.pth`, `best_norem_ED.pth`,`log_train.txt` 파일이 저장된다.
- log_train.txt에서는 iteration마다 best_accuracy와 loss 값이 어떻게 변하는지 확인 가능하다.
- pth 파일을 이용해 demo.py로 테스트가 가능하다. 

<br>

# 5. 사용자 모델 테스트(demo.py)

- 본 학습의 목표는 headline인식 이기에 EasyOcr에 있는 CRAFT가 중요하지 않을것 같아 demo.py으로 테스트를 먼저 진행한다.  
  
### 커맨드
```
$ python demo.py
--Transformation None
--FeatureExtraction VGG --SequenceModeling BiLSTM --Prediction CTC
--image_folder demo_image/
--saved_model ./models/current_accuaracy.pth
```

- 
  

<br>




# Acknowledgements
[deep-text-recognition-benchmark](https://github.com/clovaai/deep-text-recognition-benchmark) , [TextRecognitionDataGenerator](https://github.com/Belval/TextRecognitionDataGenerator)
