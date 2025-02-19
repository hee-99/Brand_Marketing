# 모듈 로드하기
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
from openpyxl import *
import pandas as pd
import subprocess

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# 제품 가져오는 코드

    # 크롬 디버깅 모드
subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chromeCookie"')
# url = 'https://naver.com' #일단 네이버로 들어간뒤 무신사로 들어가 제품정보까지 직접 접근합니다.
# 무신사 URL 및 옵션 설정
url = f"https://www.musinsa.com/brand/musinsastandard?gf=A&sortCode=REVIEW"
option = Options()
option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
option.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)
# 페이지 접속
driver.get(url)
time.sleep(1)


unique_products = set() # 중복 제거를 위한 코드
pd_list, pr_list, li_list, gr_list, re_list,sale_list = [], [], [], [], [], [] # 리스트로 받기 위해 빈리스트 생성

# 스크롤 내리기   
for i in range(500):
     driver.find_element(By.TAG_NAME,value="body").send_keys(Keys.PAGE_DOWN) 
     time.sleep(0.3)

        # 페이지 내릴때마다 크롤링
     soup = BeautifulSoup(driver.page_source, 'html.parser') # html 파싱
     block = soup.find('div','sc-f39157-1 dqBVvr')
     if not block :
         break

     products = block.find_all('span',class_= 'text-body_13px_reg sc-eDLKkx sc-gLLuof bnDFEJ fRGBNZ font-pretendard') # 제품명
     for pd in products:
         if pd.text not in unique_products:
            pd_list.append(pd.text)
            unique_products.add(pd.text) # 제품명이 중복되는 데이터를 제외하고 가져오기 위한 코드

     prices = block.find_all('span', class_='text-body_13px_semi sc-hLQSwg iXeGsA font-pretendard') # 가격
     for pr in prices:
        if len(pr_list) < len(pd_list):
            pr_list.append(pr.text)

     sale = block.find_all('span', 'text-body_13px_semi sc-hLQSwg iXeGsA text-red font-pretendard') # 할인가
     for sa in sale:
        if len(sale_list) < len(pd_list):
            sale_list.append(sa.text)

     likes = soup.find_all('span', class_='text-etc_11px_reg text-red font-pretendard') # 좋아요수
     for li in likes:
        if len(li_list) < len(pd_list):
            li_list.append(li.text)

     gradereview = soup.find_all('span', 'text-etc_11px_reg text-yellow font-pretendard') # 리뷰개수
     for j in range(0, len(gradereview), 2):
        if len(gr_list) < len(pd_list):
            gr_list.append(gradereview[j].text)

        if len(re_list) < len(pd_list):
            re_list.append(gradereview[j+1].text)

     time.sleep(1)

# 데이터 프레임으로 변경하기 위해 딕셔너리 형태로 변환
data = {
    "제품명": pd_list,
    "가격": pr_list,
    "좋아요수": li_list,
    "별점": gr_list,
    "리뷰수": re_list,
    "할인가": sale_list
}


# 데이터 프레임으로 변환
a = pd.DataFrame(data)
a

# 필요없다고 판단되는 데이터 제거
a = a[~a['제품명'].str.contains('벨트|팬티|브라|슈즈|커버|양말|드로즈|부츠|지갑|스니커즈|쉐이빙|향수|우산|삭스', na=False)]

# 데이터 저장
a.to_csv('무신사제품명크롤링_250117.csv',index=False, encoding='utf-8-sig')

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# 제품에 따른 리뷰 가져오는 함수
def musinsa_review(name):
    option = Options()
    option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    option.add_argument("--disable-blink-features=AutomationControlled")
    option.add_argument("--disable-popup-blocking")  # 팝업차단 비활성화
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=option)

    product_name = '무신사 스탠다드' + name

    url = f"https://www.musinsa.com/search/goods?keyword={product_name}"
    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        try: 
            item_id = soup.find('div', class_ = 'sc-fmKFGs fObkCV')
            if not item_id :
                raise AttributeError(f"'{name}'의 상품ID를 찾을 수 없습니다.")
            item_id = item_id.find('a')['data-item-id'] # 상품 ID 추출
            review_url = 'https://www.musinsa.com/review/goods/' + item_id
            driver.get(review_url)
            time.sleep(0.5)
        except AttributeError as e :
            print(f"'{name}'의 후기 페이지를 찾을 수 없습니다. : {e}")
            
        # 데이터 수집
        user_list = []
        star_list = []
        review_list = []
        gender_list = []
        height_list = []
        weight_list = []
        seen_users = set()  # 유저 중복 체크

            # 스크롤 반복
            # 페이지 끝에 도착하면 바로 넘어가게 만든 코드
        for _ in range(30):    
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(0.7)

            soup_2 = BeautifulSoup(driver.page_source, 'html.parser')
            review_box = soup_2.find('div', class_='GoodsReviewListSection__Container-sc-1x35scp-0 dMdlme')
            if not review_box:
                print(f"'{name}'의 리뷰 데이터를 찾을 수 없습니다.")
                break

            # 리뷰, 사용자, 별점, 성별/키/몸무게 정보 추출
            reviews = review_box.find_all('div', class_='ExpandableContent__Container-sc-gj5b23-0 cBDQQC')
            users = review_box.find_all('span', class_='text-body_13px_med text-black font-pretendard')
            stars = review_box.find_all('span', class_='text-body_13px_semi font-pretendard')
            us_data = review_box.find_all('div', class_='UserInfoGoodsOptionSection__Container-sc-1p4ukac-0 bRbsmH')

            for review, user, star, extra_data in zip(reviews, users, stars, us_data):
                # 리뷰 텍스트 정제
                text = review.text.strip()
                while text.endswith('더보기'):
                    text = text[:-3]
                while text.endswith('...'):
                    text = text[:-3]

                # 유저 중복 체크
                user_id = user.text.strip()
                if user_id not in seen_users:
                    seen_users.add(user_id)

                # # 리뷰 중복 체크
                # if text not in seen_reviews:
                #     seen_reviews.add(text)
                      # 유저를 중복 체크에 추가
                    review_list.append(text)
                    user_list.append(user_id)
                    star_list.append(star.text.strip())

                    # 성별, 키, 몸무게 분리 (첫 번째 span만 선택)
                    first_span = extra_data.find('span', class_='text-body_13px_reg text-gray-600 font-pretendard')
                    if first_span:
                        extra_info = first_span.text.strip().split("·")
                        gender = extra_info[0].strip() if len(extra_info) > 0 else "NaN"
                        height = extra_info[1].strip().replace("cm", "") if len(extra_info) > 1 else "NaN"
                        weight = extra_info[2].strip().replace("kg", "") if len(extra_info) > 2 else "NaN"
                    else:
                        gender, height, weight = "NaN", "NaN", "NaN"

                    gender_list.append(gender)
                    height_list.append(height)
                    weight_list.append(weight)

        # DataFrame 생성
        review_data = pd.DataFrame({
            "유저": user_list,
            "별점": star_list,
            "리뷰": review_list,
            "성별": gender_list,
            "키": height_list,
            "몸무게": weight_list
        })
        
    except:
        pass

    return review_data


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# 함수 실행하는 코드

import os

subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chromeCookie"')

all_reviews = []

# 중간 저장 파일 경로
output_file = '무탠다드리뷰_250118.csv'

# # 기존 저장된 파일 확인 후 로드
if os.path.exists(output_file):
    final_reviews_df = pd.read_csv(output_file)
    processed_items = set(final_reviews_df['제품명'])  # 이미 처리된 제품명 목록
else:
    final_reviews_df = pd.DataFrame()
    processed_items = set()
# 리뷰 수집

# 리뷰 수집
for i in a['제품명']:
    if i in processed_items:
        print(f"Skipping already processed item: {i}")
        continue

    try:
        reviews_df = musinsa_review(i)
        reviews_df['제품명'] = i
        all_reviews.append(reviews_df)

        # 중간 저장
        temp_df = pd.concat([final_reviews_df] +all_reviews, ignore_index=True)
        temp_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Saved progress for: {i}")

        # 기존 데이터프레임에 추가 및 리스트 초기화
        final_reviews_df = temp_df
        all_reviews = []
    except Exception as e:
        print(f"Error processing {i}: {e}")