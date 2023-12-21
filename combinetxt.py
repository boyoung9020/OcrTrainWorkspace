import os

# 합쳐질 파일들의 경로
directory = r'C:\Users\gemiso\Desktop\EasyocrWorkspace\headlinedatatxt'

# 결과를 저장할 파일 경로 및 이름
output_file_path = r'C:\Users\gemiso\Desktop\EasyocrWorkspace\headlinedatatxt\combine.txt'

# 디렉토리 내의 모든 txt 파일 가져오기
txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]

# 모든 파일의 내용을 하나의 파일에 합치기
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    for txt_file in txt_files:
        file_path = os.path.join(directory, txt_file)
        with open(file_path, 'r', encoding='utf-8') as input_file:
            output_file.write(input_file.read() + '\n')

print(f'파일이 성공적으로 합쳐졌습니다. 경로: {output_file_path}')
