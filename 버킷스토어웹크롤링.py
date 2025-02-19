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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# 제품명, 가격, 할인가, 브랜드 가져오는 코드

options = Options()
##
# 크롬 브라우저 동작방식 설정
options.add_argument("--start-maximized") # 브라우저 전체화면
options.add_experimental_option("detach", True) # 셀레니움이 종료되어도 창이 자동으로 닫히지 않게 함.
options.add_argument("--disable-blink-features=AutomationControlled")
##

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = 'https://bucketstore.com/search/goods?search_keyword_list=%ED%95%91&order_type=best'
driver.get(url)
time.sleep(2)

for i in range(1000):
    driver.find_element(By.TAG_NAME,value="body").send_keys(Keys.PAGE_DOWN) # 스크롤 한번 내리기
    time.sleep(1.5)
soup = BeautifulSoup(driver.page_source, 'html.parser')
products = soup.find_all('div', 'Goods_name__EZ1Lc Goods_nameLine2__hMCQc')
price = soup.find_all('div','Goods_priceWrapper__0EbDO')
brand = soup.find_all('div', 'Goods_brand__X1tv4')

# 중복 제거를 위한 set 활용
product_set = set()
product_list = []
price_discounted = []  # 할인된 가격
price_original = []  # 원래 가격
brand_list = []

for i, prod in enumerate(products):
    prod_name = prod.text.strip()
    if prod_name not in product_set:  # 중복이 아닐 경우만 추가
        product_set.add(prod_name)
        product_list.append(prod_name)
        brand_list.append(brand[i].text.strip() if i < len(brand) else None)

        # 가격 정보 가져오기
        discounted = price[i].find('div', 'Goods_salePrice__iSxT6') if i < len(price) else None
        original = price[i].find('div', 'Goods_tagPrice__VtznB') if i < len(price) else None

        price_discounted.append(discounted.text.strip() if discounted else None)
        price_original.append(original.text.strip() if original else None)

# 데이터프레임 생성
ping = pd.DataFrame({'제품명': product_list, '브랜드': brand_list, '원가': price_original, '할인된 가격': price_discounted})
ping
# 출력
ping.to_csv('버킷스토어_핑의류데이터_250131.csv', index=False, encoding='utf-8-sig')

# 제품명 10자 이내는 잘못들어온 데이터이기 때문에 제거하는 코드
ping = ping[~ping['제품명'].str[:10].duplicated(keep='first')]

# 제품명 데이터 저장
ping.to_csv('버킷스토어_핑의류데이터_250131.csv', index=False, encoding='utf-8-sig')

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2

# 제품에 따른 리뷰 가져오는 함수

def burket(name):
    try:            
        url = f'https://bucketstore.com/search/goods?search_keyword_list={name}'
        driver.get(url)
        time.sleep(5)
        
        driver.find_element(By.TAG_NAME, value="body").send_keys(Keys.PAGE_DOWN)  # 스크롤 한 번 내리기
        time.sleep(1.5)

        driver.find_element(By.CSS_SELECTOR, value='body > main > section.baseContents_innerSizeFull___BVbJ > section > div > div > div > div.SearchResultGoods_resultWrapper__ld4Y1 > div.SearchResultGoods_wrapper__OIW6s > div.SearchResultGoods_scroll__GdCkq > div.SearchResultGoods_goodsWrapper__dgFvc > section > section > div:nth-child(1) > div > div.Goods_thumbnailWrapper__nynPo').click()  # 제품 클릭
        time.sleep(2)

        #  리뷰 더보기 버튼이 나올 때까지 스크롤
        max_scroll_attempts = 15  # 최대 스크롤 횟수 설정 (페이지에 따라 조정 가능)
        scroll_count = 0

        while scroll_count < max_scroll_attempts:
            try:
                review_button = driver.find_element(By.XPATH, value='/html/body/main/section[1]/section/div/section[2]/section[2]/div[3]/div[2]/button')
                if review_button.is_displayed():
                    review_button.click()
                    time.sleep(1)
                    break  # 버튼을 클릭했으면 루프 종료
            except:
                driver.find_element(By.TAG_NAME, value="body").send_keys(Keys.PAGE_DOWN)  # 스크롤 다운
                time.sleep(1)
                scroll_count += 1

        if scroll_count == max_scroll_attempts:
            print(f"'{name}' 리뷰 버튼 없음, 다음 제품으로 이동")
            return None  # 리뷰 버튼이 끝까지 안 나왔으면 종료

        #  HTML 가져오기
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        review = soup.find_all('div', 'customerReviewContents_text__YKiJb')
        score = soup.find_all('span', 'customerReviewContents_starRateValue__qsPa0')
        user = soup.find_all('div', 'customerReviewContents_reviewFooter__2tTin')

        # 사용자 ID만 추출하는 함수
        def extract_user_id(text):
            return re.sub(r'\d{4}\.\d{2}\.\d{2}', '', text).strip()  # YYYY.MM.DD 형식의 날짜 제거

        # 중복 확인을 위한 set 생성
        seen_users = set()
        unique_reviews = []
        unique_scores = []
        unique_users = []

        # 데이터 수집 및 중복 제거
        for j, i, s in zip(review, score, user):
            user_id = extract_user_id(s.text.strip())  # 사용자 ID 추출
            if user_id not in seen_users:  # 중복되지 않은 사용자만 추가
                seen_users.add(user_id)
                unique_reviews.append(j.text.strip())
                unique_scores.append(i.text.strip())
                unique_users.append(user_id)

        #  닫기 버튼 클릭
        try:
            close_button = driver.find_element(By.XPATH, value='/html/body/section[3]/section/div/div/div[2]')
            close_button.click()
            time.sleep(0.5)
        except:
            print("닫기 버튼을 찾을 수 없음")

        #  데이터프레임 생성
        asd = pd.DataFrame({'리뷰': unique_reviews, '별점': unique_scores, '사용자': unique_users})
        
        return asd

    except Exception as e:
        print("오류 발생:", e)
        return None


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2

# 함수 실행하는 코드

import os

# 로그인하는 코드
options = Options()
##
# 크롬 브라우저 동작방식 설정
options.add_argument("--start-maximized") # 브라우저 전체화면
options.add_experimental_option("detach", True) # 셀레니움이 종료되어도 창이 자동으로 닫히지 않게 함.
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-popup-blocking")# 팝업차단 비활성화
##
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)



all_reviews = []

# 중간 저장 파일 경로
output_file = '버킷스토어_핑_의류_리뷰_250131.csv'

# # 기존 저장된 파일 확인 후 로드
if os.path.exists(output_file):
    final_reviews_df = pd.read_csv(output_file)
    processed_items = set(final_reviews_df['제품명'])  # 이미 처리된 제품명 목록
else:
    final_reviews_df = pd.DataFrame()
    processed_items = set()
# 리뷰 수집
# 
# 리뷰 수집
for i in ping['제품명']:
    if i in processed_items:
        print(f"Skipping already processed item: {i}")
        continue

    try:
        reviews_df = burket(i)
        reviews_df['제품명'] = i
        all_reviews.append(reviews_df)

        # 중간 저장
        temp_df = pd.concat([final_reviews_df] + all_reviews, ignore_index=True)
        temp_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Saved progress for: {i}")

        # 기존 데이터프레임에 추가 및 리스트 초기화
        final_reviews_df = temp_df
        all_reviews = []
    except Exception as e:
        print(f"Error processing {i}: {e}")