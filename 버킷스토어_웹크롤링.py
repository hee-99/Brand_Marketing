# 필요한 모듈 불러오기
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

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# 제품명/ 할인가/ 원가를 가져오는 코드

options = Options()
##
# 크롬 브라우저 동작방식 설정
options.add_argument("--start-maximized") # 브라우저 전체화면
options.add_experimental_option("detach", True) # 셀레니움이 종료되어도 창이 자동으로 닫히지 않게 함.
options.add_argument("--disable-blink-features=AutomationControlled")
##

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = 'https://bucketstore.com/goods/list/4?order_type=best' # 버킷스토어 홈페이지
driver.get(url)
time.sleep(2)
driver.find_element(By.XPATH, value='/html/body/main/section[1]/section[1]/section/section/section[2]/div[2]').click() # 성별 클릭
time.sleep(1)
driver.find_element(By.XPATH, value='/html/body/main/section[1]/section[1]/section/section/section[3]/div[1]/span').click() # 여성 클릭
time.sleep(1)
driver.find_element(By.XPATH, value='/html/body/main/section[1]/section[3]/div/section/section[1]/div[3]/button').click() # 여성을 클릭한 창 안에서 스크롤이 되기 때문에 view more 클릭하기 
time.sleep(1)

for i in range(1000): # 스크롤 내리기
    driver.find_element(By.TAG_NAME,value="body").send_keys(Keys.PAGE_DOWN) 
    time.sleep(1.5)

soup = BeautifulSoup(driver.page_source, 'html.parser') # 파씽
products = soup.find_all('div', 'Goods_name__EZ1Lc Goods_nameLine2__hMCQc') # 제품명
price = soup.find_all('div','Goods_priceWrapper__0EbDO') # 할인율과 원가

product_1 = [] # 제품명
price_discounted = []  # 할인된 가격
price_original = []  # 원래 가격

for i in products[8:]:
    product_1.append({'제품명': i.text.strip()})
for prices in price[8:]:
    # 할인 가격 찾기
    discounted = prices.find('div', 'Goods_salePrice__iSxT6')  # 예: 할인 가격 클래스
    if discounted:
        price_discounted.append({'할인가': discounted.text.strip()})
    else:
        price_discounted.append({'할인가': None})

    # 원래 가격 찾기
    original = prices.find('div', 'Goods_tagPrice__VtznB')  # 예: 원래 가격 클래스
    if original:
        price_original.append({'원가': original.text.strip()})
    else:
        price_original.append({'원가': None})

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

product_1 # 제품명 딕셔너리
price_discounted # 할인가 딕셔너리
price_original # 제품 가격 딕셔너리

# 3개의 딕셔너리를 데이터 프레임으로 만들어서 하나의 데이터 프레임으로 합체
df = pd.DataFrame(product_1)
df_1 = pd.DataFrame(price_discounted)
df_2 = pd.DataFrame(price_original)
df_3 = pd.concat([df, df_1, df_2], axis=1)


# 할인가 보다는 할인율이 필요하기 때문에 원가에서 할인가를 뺀 값을 원가로 나누기
# 그리고 그 값을 퍼센트로 나타내기 위해 곱하기 100

# 원래 가격과 할인 가격을 숫자로 변환
# 계산을 위해서 ','기호는 제거하고 데이터 타입을 숫자로 변경
df_3['원가'] = df_3['원가'].str.replace(",", '').astype(int)
df_3['할인가'] = df_3['할인가'].str.replace(",", '').astype(int)

# 할인율 계산
df_3['할인율'] = ((df_3['원가'] - df_3['할인가']) / df_3['원가']) * 100

# 할인율 소수점 제거 및 % 기호 추가
df_3['할인율'] = df_3['할인율'].astype(int).astype(str) + '%'

# 다시 ',' 포함된 형식으로 변환
df_3['원가'] = df_3['원가'].apply(lambda x: f"{x:,}")
df_3['할인가'] = df_3['할인가'].apply(lambda x: f"{x:,}")

# 할인가 열은 지워주기
df_3 = df_3.drop(['할인가'],axis=1)

# csv 파일로 저장하기
df_3.to_csv('버킷스토어_제품명_가격.csv')

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# 리뷰를 가져오는 함수

def burket(name):
    try:            
        # 돋보기 클릭
        driver.find_element(By.XPATH, value='/html/body/nav[2]/section/section[3]/div[1]').click() 
        time.sleep(0.5)

        # 검색창 클릭
        driver.find_element(By.XPATH, value='/html/body/section[3]/section/div/section/div/div[1]/div').click() 
        time.sleep(0.5)

        # 검색어 입력
        driver.find_element(By.XPATH, value='/html/body/section[3]/section/div/section/div/div[1]/div/input').send_keys(name, Keys.RETURN) 
        time.sleep(3)

        # 제품클릭
        driver.find_element(By.CSS_SELECTOR, value='body > main > section.baseContents_innerSizeFull___BVbJ > section > div > div > div > div.SearchResultGoods_resultWrapper__ld4Y1 > div.SearchResultGoods_wrapper__OIW6s > div.SearchResultGoods_scroll__GdCkq > div.SearchResultGoods_goodsWrapper__dgFvc > section > section > div:nth-child(1) > div > div.Goods_thumbnailWrapper__nynPo').click() 
        time.sleep(0.5)

        # 스크롤 내리기
        for i in range(9):
            driver.find_element(By.TAG_NAME,value="body").send_keys(Keys.PAGE_DOWN) 
            time.sleep(1)

        # 리뷰더보기 클릭
        driver.find_element(By.XPATH, value='//*[@id="review"]/div[2]/button').click() 
        time.sleep(0.5)

        # 스크롤 내리기
        for i in range(5):
            driver.find_element(By.TAG_NAME,value="body").send_keys(Keys.PAGE_DOWN) 
            time.sleep(1)

        # 리뷰 더보기 창 나가는 (x)버튼 클릭
        driver.find_element(By.XPATH, value='/html/body/section[3]/section/div/div/div[2]').click() 
        time.sleep(0.5)

        # 파씽
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        review = soup.find_all('div', 'customerReviewContents_text__YKiJb')
 

        reviews = [j.text.strip() for j in review]
        return reviews
    except:
        pass

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

options = Options()
##
# 크롬 브라우저 동작방식 설정
options.add_argument("--start-maximized") # 브라우저 전체화면
options.add_experimental_option("detach", True) # 셀레니움이 종료되어도 창이 자동으로 닫히지 않게 함.
options.add_argument("--disable-blink-features=AutomationControlled")
##

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = 'https://bucketstore.com/'
driver.get(url)
time.sleep(1)
driver.find_element(By.XPATH, value='/html/body/section[3]/section/div[2]/div[1]').click() # 하루동안 열지않기 팝업닫기
time.sleep(0.5)

burket_review = []

try:
    for i in df_3['제품명']:
        print(f"현재 처리 중인 제품명: {i}")  # 현재 처리 중인 제품명 출력
        
        review_1 = burket(i)
        print(f"review_1 결과: {review_1}")  # burket 함수의 반환값 확인
        
        if review_1:  # 리뷰가 있는 경우에만 처리
            print(f"리뷰 개수: {len(review_1)}")  # 리뷰 개수 확인
            for single_review in review_1:  # 각 리뷰를 개별적으로 처리
                print(f"개별 리뷰: {single_review}")  # 개별 리뷰 내용 확인
                burket_review.append({'제품명': i, '리뷰': single_review})
        else:
            print("리뷰가 없거나 None이 반환됨")
            
except:
    print(f"에러 발생")
finally:
    print(f"최종 수집된 리뷰 개수: {len(burket_review)}")  # 최종 수집된 리뷰 개수 확인
    review_df = pd.DataFrame(burket_review)
    review_df.to_csv('버킷스토어_남성_리뷰_최종.csv', index=False, encoding='utf-8-sig')