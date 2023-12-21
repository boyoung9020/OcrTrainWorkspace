import os
import torch
import re
import subprocess
import tkinter as tk
import threading
import shutil
from tkinter import messagebox


def create_datasets():
    
     # 지우기 전에 확인 메시지 표시
    confirm_message = "주의: 기존 데이터가 삭제됩니다. 계속하시겠습니까?"
    confirm = messagebox.askyesno("확인", confirm_message)
    
    if confirm:
        # 삭제 후 trdg 실행
        trdg()
        trdg2dtrb()
        dtrb()
        
        
    
    
    
def trdg():
    
    # 각 entry에서 값을 가져오기
    train_dataset_value = train_dataset_entry.get()
    validation_dataset_value = validation_dataset_entry.get()
    test_dataset_value = test_dataset_entry.get()
    w_entry_value = w_entry.get()

    # output_directory 경로 설정
    base_output_dir = r'C:\Users\gemiso\Desktop\EasyocrWorkspace\step1'
    train_output_dir = os.path.join(base_output_dir, 'training')
    validation_output_dir = os.path.join(base_output_dir, 'validation')
    test_output_dir = os.path.join(base_output_dir, 'test')
    
    clear_directories(train_output_dir,validation_output_dir,test_output_dir)

    # activate 가상환경
    activate_env_command = r'D:\anaconda3\envs\easyocrtrain38\Lib\venv\scripts\nt\activate'

    # trdg 명령어 설정
    create_train_command = f'cmd /C "cd /d {train_output_dir} && {activate_env_command} && trdg -l ko -c {train_dataset_value} -w {w_entry_value} --output_dir {train_output_dir}"'
    create_validation_command = f'cmd /C "cd /d {validation_output_dir} && {activate_env_command} && trdg -l ko -c {validation_dataset_value} -w {w_entry_value} --output_dir {validation_output_dir}"'
    create_test_command = f'cmd /C "cd /d {test_output_dir} && {activate_env_command} && trdg -l ko -c {test_dataset_value} -w {w_entry_value} --output_dir {test_output_dir}"'

    try:
        # activate 가상환경 실행
        subprocess.run(create_train_command, shell=True, check=True)
        subprocess.run(create_validation_command, shell=True, check=True)
        subprocess.run(create_test_command, shell=True, check=True)

        messagebox.showinfo("Success", "[setp1] Dataset 생성이 완료되었습니다.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"[setp1] Dataset 생성 중 오류가 발생했습니다: {e}")
        
        
def trdg2dtrb(): 
    
    os.chdir(r'C:\Users\gemiso\Desktop\EasyocrWorkspace\TRDG2DTRB')

    base_output_dir = r'C:\Users\gemiso\Desktop\EasyocrWorkspace\step2'
    train_output_dir = os.path.join(base_output_dir, 'training\kordata')
    validation_output_dir = os.path.join(base_output_dir, 'validation\kordata')
    test_output_dir = os.path.join(base_output_dir, 'test\kordata')
    
    clear_directories(train_output_dir,validation_output_dir,test_output_dir)

    # pcl 명령어 실행
    convert_train_command = r'python convert.py --input_path "C:\Users\gemiso\Desktop\EasyocrWorkspace\step1\training" --output_path "C:\Users\gemiso\Desktop\EasyocrWorkspace\step2\training\kordata"'
    convert_validation_command = r'python convert.py --input_path "C:\Users\gemiso\Desktop\EasyocrWorkspace\step1\validation" --output_path "C:\Users\gemiso\Desktop\EasyocrWorkspace\step2\validation\kordata"'
    convert_test_command = r'python convert.py --input_path "C:\Users\gemiso\Desktop\EasyocrWorkspace\step1\test" --output_path "C:\Users\gemiso\Desktop\EasyocrWorkspace\step2\test\kordata"'


    
    try:
        # activate 가상환경 실행
        subprocess.run(convert_train_command, shell=True, check=True)
        subprocess.run(convert_validation_command, shell=True, check=True)
        subprocess.run(convert_test_command, shell=True, check=True)

        messagebox.showinfo("Success", "[setp2] txt 생성이 완료되었습니다.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"[setp2] txt 생성 중 오류가 발생했습니다: {e}")
    

def dtrb():
    os.chdir(r'C:\Users\gemiso\Desktop\EasyocrWorkspace\deep-text-recognition-benchmark')

    base_output_dir = r'C:\Users\gemiso\Desktop\EasyocrWorkspace\step3'
    train_output_dir = os.path.join(base_output_dir, 'training\kordata')
    validation_output_dir = os.path.join(base_output_dir, 'validation\kordata') 
    test_output_dir = os.path.join(base_output_dir, 'test\kordata')

    clear_directories(train_output_dir,validation_output_dir,test_output_dir)

    # pcl 명령어 실행
    convertlmdb_train_command = r'python create_lmdb_dataset.py --inputPath "C:\Users\gemiso\Desktop\EasyocrWorkspace\step2\training\kordata" --gtFile "C:\Users\gemiso\Desktop\EasyocrWorkspace\step2\training\kordata\gt.txt" --outputPath "C:\Users\gemiso\Desktop\EasyocrWorkspace\step3\training\kordata"'
    convertlmdb_validation_command = r'python create_lmdb_dataset.py --inputPath "C:\Users\gemiso\Desktop\EasyocrWorkspace\step2\validation\kordata" --gtFile "C:\Users\gemiso\Desktop\EasyocrWorkspace\step2\validation\kordata\gt.txt" --outputPath "C:\Users\gemiso\Desktop\EasyocrWorkspace\step3\validation\kordata"'
    convertlmdb_test_command = r'python create_lmdb_dataset.py --inputPath "C:\Users\gemiso\Desktop\EasyocrWorkspace\step2\validation\kordata" --gtFile "C:\Users\gemiso\Desktop\EasyocrWorkspace\step2\test\kordata\gt.txt" --outputPath "C:\Users\gemiso\Desktop\EasyocrWorkspace\step3\test\kordata"'


    try:
        # activate 가상환경 실행
        subprocess.run(convertlmdb_train_command, shell=True, check=True)
        subprocess.run(convertlmdb_validation_command, shell=True, check=True)
        subprocess.run(convertlmdb_test_command, shell=True, check=True)

        messagebox.showinfo("Success", "[setp3] lmdb 생성이 완료되었습니다.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"[setp3] lmdb 생성 중 오류가 발생했습니다: {e}")
        
        
        
stop_learning_event = threading.Event()

        
def learning():
    # 스레드 생성 시 Event 객체를 전달
    learning_thread = threading.Thread(target=learning_task, args=(stop_learning_event,))
    learning_thread.start()

def learning_task(stop_event):
    os.chdir(r'C:\Users\gemiso\anaconda3\envs\easyocrtrain38\Lib\site-packages\deep-text-recognition-benchmark')
    # pcl 명령어 실행
    training_ocr = r'python train.py --train_data "C:/Users/gemiso/Desktop/EasyocrWorkspace/step3/training" --valid_data "C:/Users/gemiso/Desktop/EasyocrWorkspace/step3/validation" --workers 0 --select_data /  --batch_ratio 1 --Transformation None --FeatureExtraction "VGG" --SequenceModeling "BiLSTM" --Prediction "CTC" --input_channel 1 --output_channel 256 --hidden_size 256 --saved_model "C:/Users/gemiso/Desktop/EasyocrWorkspace/user_network_dir/custom.pth" --FT"'
    
    try:
        subprocess.run(training_ocr, shell=True, check=True)
        root.after(0, lambda: messagebox.showinfo("Success", "학습이 완료되었습니다."))
    except subprocess.CalledProcessError as e:
        if stop_event.is_set():
            root.after(0, lambda: messagebox.showinfo("Interrupted", "학습이 중단되었습니다."))
    else:
        root.after(0, lambda: messagebox.showerror("Error", f"학습 중 오류가 발생했습니다: {e}"))

    
    
    finally:
        # 스레드가 종료될 때 Event를 지워줌
        stop_event.clear()

def learning_interruption():
    # Event 객체를 설정하여 learning_task 스레드를 중지시킴
    stop_learning_event.set()
    print("Learning thread interrupted")
    



def clear_directories(train_output_dir,validation_output_dir,test_output_dir):    

    # 해당 디렉토리의 내용물을 모두 삭제
    for directory in [train_output_dir, validation_output_dir, test_output_dir]:
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")


def EasyOcrTest():
    try:
        # 변경된 가상환경 활성화
        activate_env_command = r'C:\Users\gemiso\anaconda3\envs\easyocrrun\Lib\venv\scripts\nt\activate'  # 가상환경 위치에 맞게 수정
        subprocess.run(f'cmd /C "{activate_env_command}"', shell=True, check=True)

        # 실행할 명령 및 결과 파일 경로 설정
        command = r'python C:\Users\gemiso\Desktop\EasyocrWorkspace\EasyOcr_test.py'
        output_file = r'C:\Users\gemiso\Desktop\EasyocrWorkspace\testouput\result.txt'

        # 명령 실행 및 결과 파일로 저장
        subprocess.run(f'{command} > {output_file}', shell=True, check=True)

        messagebox.showinfo("Success", "EasyOcrTest가 완료되었습니다.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"EasyOcrTest 실행 중 오류가 발생했습니다: {e}")
    finally:
        # 변경된 가상환경 비활성화
        deactivate_env_command = 'deactivate' if os.name != 'nt' else 'conda deactivate'
        subprocess.run(deactivate_env_command, shell=True, check=True)
        
        
def pth_substitution():
    source_path = r"C:\Users\gemiso\Desktop\EasyocrWorkspace\og_model\None-VGG-BiLSTM-CTC.pth"
    destination_path = r"C:\Users\gemiso\Desktop\EasyocrWorkspace\deep-text-recognition-benchmark\models"

    try:
        # 모델 폴더의 .pth 파일 삭제
        for file_name in os.listdir(destination_path):
            if file_name.endswith(".pth"):
                file_path = os.path.join(destination_path, file_name)
                os.remove(file_path)

        # 새로운 .pth 파일 복사
        shutil.copy(source_path, destination_path)

        print("pth 파일 교체 완료!")

    except Exception as e:
        print(f"pth 파일 교체 중 오류 발생: {e}")
        
        
        
    source_path = r"C:\Users\gemiso\Desktop\EasyocrWorkspace\user_network_dir\custom.pth"
    destination_path = r"C:\Users\gemiso\Desktop\EasyocrWorkspace\deep-text-recognition-benchmark\models\saved_models\None-VGG-BiLSTM-CTC-Seed1111\best_accuracy.pth"
    user_network_dir = r"C:\Users\gemiso\Desktop\EasyocrWorkspace\user_network_dir"

    try:
        # custom.pth 파일 삭제
        os.remove(source_path)

        # 새로운 파일 복사
        shutil.copy(destination_path, user_network_dir)

        # 파일 이름 변경
        new_file_path = os.path.join(user_network_dir, "custom.pth")
        os.rename(os.path.join(user_network_dir, "best_accuracy.pth"), new_file_path)

        print("custom.pth 파일 교체 및 이름 변경 완료!")

    except Exception as e:
        print(f"custom.pth 파일 교체 중 오류 발생: {e}")
        
    
            
        
# Tkinter 창 생성
root = tk.Tk()
root.title("Dataset and Text Input")

# row=0: 라벨 및 텍스트 입력 창 생성
train_dataset_label = tk.Label(root, text="Training Dataset")
train_dataset_label.grid(row=0, column=0, padx=10, pady=5)

validation_dataset_label = tk.Label(root, text="Validation Dataset")
validation_dataset_label.grid(row=0, column=1, padx=10, pady=5)

test_dataset_label = tk.Label(root, text="Test Dataset")
test_dataset_label.grid(row=0, column=2, padx=10, pady=5)

test_dataset_label = tk.Label(root, text="단어 갯수")
test_dataset_label.grid(row=0, column=3, padx=10, pady=5)

# default 값 설정
default_train_value = "1000"
default_validation_value = "100"
default_test_value = "100"
default_w_value = "3"
entry_width = "8"

train_dataset_entry = tk.Entry(root, width=entry_width)
train_dataset_entry.insert(0, default_train_value)
train_dataset_entry.grid(row=1, column=0, padx=10, pady=5)

validation_dataset_entry = tk.Entry(root, width=entry_width)
validation_dataset_entry.insert(0, default_validation_value)
validation_dataset_entry.grid(row=1, column=1, padx=10, pady=5)

test_dataset_entry = tk.Entry(root, width=entry_width)
test_dataset_entry.insert(0, default_test_value)
test_dataset_entry.grid(row=1, column=2, padx=10, pady=5)

w_entry = tk.Entry(root, width=entry_width)
w_entry.insert(0, default_w_value)
w_entry.grid(row=1, column=3, padx=10, pady=5) 

# 버튼 생성 및 배치
create_datasets_button = tk.Button(root, text="Dataset 생성", command=create_datasets)
create_datasets_button.grid(row=2, column=0, columnspan=3, pady=10)

# 버튼 생성 및 배치
learning_button = tk.Button(root, text="학습 시작", command=learning)
learning_button.grid(row=3, column=0, columnspan=3, pady=50)

# 버튼 생성 및 배치
learning_interruption_button = tk.Button(root, text="학습 중단", command=learning_interruption)
learning_interruption_button.grid(row=3, column=1, columnspan=3, pady=10)

learning_interruption_button = tk.Button(root, text="easyocr테스트", command=EasyOcrTest)
learning_interruption_button.grid(row=4, column=0, columnspan=3, pady=10)

learning_interruption_button = tk.Button(root, text="pth치환", command=pth_substitution)
learning_interruption_button.grid(row=4, column=1, columnspan=3, pady=10)

# Tkinter 루프 시작
root.mainloop()
