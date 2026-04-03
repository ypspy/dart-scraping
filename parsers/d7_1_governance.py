# -*- coding: utf-8 -*-
"""
References

1. 이미지 인식 참고 https://blog.daum.net/geoscience/1266 (Tesseract at UB Mannheim 설치 C:\Program Files\Tesseract-OCR)
2. CV2 설치 https://pypi.org/project/opencv-python/
3. tesseract 환경변수에 추가 https://joyhong.tistory.com/79
4. tesseract config 사용법 https://m.blog.naver.com/hn03049/221957851802
6. skimage 설치 https://scikit-image.org/docs/stable/install.html
7. 웹페이지 이미지를 다운로드 없이 이미지 링크로 array 직접 변환 https://stackoverflow.com/questions/21061814/how-can-i-read-an-image-from-an-internet-url-in-python-cv2-scikit-image-and-mah
8. 리스트를 뒤에서부터 읽기 https://stackoverflow.com/questions/529424/traverse-a-list-in-reverse-order-in-python
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import os
import random
import time
from bs4 import BeautifulSoup
from pytesseract import image_to_string
from skimage import io
from parsers.common import (
    load_config, build_path_list, preprocess_df, deduplicate_df,
)

config = load_config()
GOVERNANCE_DIR = config["paths"]["governance_dir"]
OUTPUT_DIR = config["paths"]["output_dir"]
REPORT_DIRS = config["paths"]["report_dirs"]


def governance_classifier(text_data):
    content = ''.join(text_data.split())
    matches_pos = ['감사위원회', '監査委員會']
    matches_neg = ['감사의선임', '감사는', '監事는']
    return_text = ''
    if any(x in content for x in matches_pos) and all(x not in content for x in matches_neg):
        return_text = "감사위원회"
    if any(x in content for x in matches_neg):
        return_text = "감사"
    return return_text


def img_parser(soup):
    ocr_config = ('-l kor --oem 3 --psm 4')
    imglist = soup.find_all("img")
    result = ''
    for i in imglist[::-1]:  # 감사위원회/감사 등은 뒤에서부터 찾는게 더 빠르다. https://stackoverflow.com/questions/529424/traverse-a-list-in-reverse-order-in-python
        link = r"http://dart.fss.or.kr/" + str(i["src"])
        try:
            image = io.imread(link)
        except ValueError:  # "이 파일은 서비스하지 않습니다!"라는 메시지가 뜨는 경우
            continue
        strings = image_to_string(image, config=ocr_config)
        result = governance_classifier(strings)
        if result:
            break
        time.sleep(random.uniform(0.8, 1)) # 이렇게 하면 블락 안당하나
    return result


# 1. 타겟 폴더에 있는 필요 문서 경로 리스트업
path_list = build_path_list(GOVERNANCE_DIR, REPORT_DIRS, "*정관_정관*.*")

# 2. 분리 (year filter)
path_list = (
    [x for x in path_list if "(2017." in x]
    + [x for x in path_list if "(2018." in x]
    + [x for x in path_list if "(2019." in x]
)

# 3. Preprocess
df = preprocess_df(path_list)
path_list_out = df["path"].tolist()

result = []
count = 0

for file in path_list_out:

    html = open(file, "r", encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    html.close()
    return_text = ""

    content = ''.join(soup.text.split())

    img = "text"  # 정관의 입력 형태
    return_text = img + "_" + governance_classifier(content)

    if soup.img:
        img = "image"
        return_text = img + "_" + img_parser(soup)

    result.append(return_text)
    count += 1
    print(count, return_text)

df["AC2"] = result

df = df.drop([0, 1, 14, "path", "duplc"], axis=1, errors="ignore")
df = deduplicate_df(
    df,
    sort_cols=[10, 5, "con", 2, 6, "amend"],
    key_cols=[5, 10],
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, "wp01.data20.output.csv"), sep="\t")
