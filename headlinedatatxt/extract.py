def extract_chinese_characters(file_path):
    chinese_characters = set()  # 중복을 허용하지 않는 집합(set)을 사용하여 중복 제거

    # 파일 열기
    with open(file_path, 'r', encoding='utf-8') as file:
        # 파일의 각 줄에 대해 반복
        for line in file:
            # 각 줄에서 한자 추출 (예: 한자는 중국어, 일본어, 한국어 등 다양한 언어에서 사용되므로 정확한 패턴이 필요할 수 있음)
            characters = [char for char in line if '\u4e00' <= char <= '\u9fff']
            chinese_characters.update(characters)  # 추출된 한자를 집합에 추가

    return chinese_characters

# combine.txt 파일에서 추출된 한자 출력
file_path = r'C:\Users\gemiso\Desktop\EasyocrWorkspace\headlinedatatxt\combine.txt'
result = extract_chinese_characters(file_path)

# 결과 출력: 한자를 공백없이 붙여서 출력
print("추출된 한자:", ''.join(result))
