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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import UnexpectedAlertPresentException
import re
from selenium.webdriver.common.action_chains import ActionChains

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2

# 제품명 가져오는 코드

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 웹사이트 접속
url = 'https://www.changegolf.co.kr/'  # 정확한 URL을 입력해 주세요
driver.get(url)
time.sleep(1)

driver.find_element(By.XPATH, value='//*[@id="header"]/div[1]/div[2]/div[1]/a/span').click()  # 로그인 클릭
time.sleep(1)

driver.find_element(By.XPATH, value='//*[@id="mem_userid"]').send_keys('id입력')  # 아이디입력
time.sleep(1)

driver.find_element(By.XPATH, value='//*[@id="flogin"]/div[1]/div[2]/div/input').send_keys('password입력')  # 비번 입력
time.sleep(1)

driver.find_element(By.XPATH, value='//*[@id="flogin"]/div[1]/div[4]/button').click()  # 로그인하기
time.sleep(1)


driver.find_element(By.XPATH, value='//*[@id="gnb"]/ul/li[3]/a').click()  # 골프 리뷰 & 평가 클릭
time.sleep(1)

for i in range(8):
    driver.find_element(By.TAG_NAME, value="body").send_keys(Keys.PAGE_DOWN)
    time.sleep(1)

# 첫 번째 더보기 클릭
driver.find_element(By.XPATH, value='//*[@id="listSection"]/div/div/div[3]/button').click()
time.sleep(1)


# 최종 데이터를 저장할 딕셔너리
pd_dict = []
golf_type = []
brand_name = []
review_count = []
product_title = []

for i in range(97):  # 반복 횟수를 2로 설정
    for _ in range(6):  # 내부 루프에서 j 대신 _ 사용
        driver.find_element(By.TAG_NAME, value="body").send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
    # "더보기" 버튼 클릭
    driver.find_element(By.XPATH, value='//*[@id="listSection"]/div/div/div[3]/button').click()
    time.sleep(1)

    # 페이지 소스 업데이트 및 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')  # 매번 최신 HTML로 업데이트
    # 전체 항목을 가져오도록 find_all()로 변경
    prot_title_wrap = soup.find_all('div', 'product-title-wrap')  # product-title-wrap 선택
    golf = soup.find_all('span', 'badge badge-club')
    brand = soup.find_all('span', 'brand')
    review_1 = soup.find_all('span', 'info')

    # 각각의 요소에서 데이터를 추출
    for i in prot_title_wrap:
        title = i.find('div', class_='title')
        if title:
            product_title.append(title.text.strip())  # 공백 제거

    for j in golf:
        golf_type.append(j.text.strip())

    for k in brand:
        brand_name.append(k.text.strip())

    for l in review_1:
        match = re.search(r'평가 (\d+)', l.text)
        review_count.append(match.group(1) if match else '0')

# 중복되지 않는 제품명만 저장
for titl, gol, bran, revie in zip(product_title, golf_type, brand_name, review_count):
    pd_dict.append({
        '제품명': titl,
        '클럽유형': gol,
        '브랜드': bran,
        '리뷰개수': revie,
    })
pd_dict

# 데이터 저장하기
a = pd.DataFrame(pd_dict)
a_cleaned = a.drop_duplicates(subset=['제품명']).reset_index(drop=True)
a_cleaned.info()
a_cleaned.to_csv('골프클럽_데이터_250115.csv', encoding='utf-8-sig')

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2

# 제품에 따른 성능 평점, 연령대 비율 가져오는 함수



def product(name):
    try:   
        url_1 = f'https://www.changegolf.co.kr/search?skeyword={name}'
        driver.get(url_1)
        time.sleep(1)
        

        driver.find_element(By.XPATH, value='//*[@id="contents"]/section/div/div[1]/div[1]/div[1]/div/h5/a[1]').click()  # 제품 클릭
        time.sleep(0.5)

        for i in range(1):
            driver.find_element(By.TAG_NAME, value="body").send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
        try:    
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            tt = soup.find('div', 'review-progress-wrap')
            # 스펙 데이터를 행 단위로 딕셔너리에 저장
            specs_dict2 = {}
            # 스펙 테이블에서 label과 avg 값을 찾아 딕셔너리에 추가
            labels1 = tt.find_all('span', 'label')  # label 요소들 찾기
            avgs1 = tt.find_all('span', 'avg')  # avg 요소들 찾기
            # 평점 데이터 가져오기
            rating = soup.find('h3', text='평점').find_next_sibling('span').find('em').text.strip()

            # 두 리스트를 순회하면서 데이터를 딕셔너리에 저장
            for label2, avg2 in zip(labels1, avgs1):
                key2 = label2.text.strip()  # label 텍스트에서 공백 제거
                value2 = avg2.text.strip()  # avg 텍스트에서 공백 제거
                specs_dict2['평점'] = rating
                specs_dict2[key2] = value2  # 딕셔너리에 추가
        except:
            specs_dict2 = {}
        try:
            driver.find_element(By.XPATH, value='//*[@id="contents"]/div[1]/div[2]/div[3]/ul/li[1]/a').click()  # 유저 데이터
            time.sleep(1)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            # '연령대' 섹션을 선택하기 위한 기준 설정
            age_section = soup.find('h4', text='연령대').find_parent('div')  # '연령대' 텍스트를 포함한 부모 div 찾기
            spe_table = age_section.find('div', 'review-progress-wrap')




            driver.find_element(By.XPATH, value='//*[@id="wrapper"]/div[8]/div[2]/button').click()  # 닫기 클릭
            time.sleep(1)

            # 스펙 데이터를 행 단위로 딕셔너리에 저장
            specs_dict1 = {}
            # 스펙 테이블에서 label과 avg 값을 찾아 딕셔너리에 추가
            labels = spe_table.find_all('span', 'label')  # label 요소들 찾기
            avgs = spe_table.find_all('span', 'avg')  # avg 요소들 찾기

            # 두 리스트를 순회하면서 데이터를 딕셔너리에 저장
            for label, avg in zip(labels, avgs):
                key = label.text.strip()  # label 텍스트에서 공백 제거
                value = avg.text.strip()  # avg 텍스트에서 공백 제거
                specs_dict1[key] = value  # 딕셔너리에 추가
        except:
            specs_dict1 = {}

        
        df1 = pd.DataFrame([specs_dict1])
        df2 = pd.DataFrame([specs_dict2])
        df3 = pd.concat([df2,df1],axis=1)
        
        return df3

    except Exception as e:
        print(f"Error occurred: {e}")
        return None


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2

# 함수 실행시키는 코드

# 로그인하는 코드
options = Options()
##
# 크롬 브라우저 동작방식 설정
options.add_argument("--start-maximized") # 브라우저 전체화면
options.add_experimental_option("detach", True) # 셀레니움이 종료되어도 창이 자동으로 닫히지 않게 함.
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-popup-blocking")# 팝업차단 비활성화
##


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = 'https://www.changegolf.co.kr/'  # 정확한 URL을 입력해 주세요
driver.get(url)
time.sleep(1)


driver.find_element(By.XPATH, value='//*[@id="header"]/div[1]/div[2]/div[1]/a/span').click()  # 로그인 클릭
time.sleep(1)

driver.find_element(By.XPATH, value='//*[@id="mem_userid"]').send_keys('id입력')  # 아이디입력
time.sleep(1)

driver.find_element(By.XPATH, value='//*[@id="flogin"]/div[1]/div[2]/div/input').send_keys('password입력')  # 비번 입력
time.sleep(1)

driver.find_element(By.XPATH, value='//*[@id="flogin"]/div[1]/div[4]/button').click()  # 로그인하기
time.sleep(1)

product_정보 = []  # 모든 제품 정보를 저장할 리스트

# 제품명을 하나씩 반복하며 크롤링 실행
for i in a_cleaned['제품명']:
    # 'product' 함수 호출
    review = product(i)  # review는 DataFrame 형식으로 반환

    # 크롤링 결과가 비어 있지 않을 경우에만 추가
    if review is not None and not review.empty:
        # DataFrame을 딕셔너리로 변환 후 리스트에 추가
        review_dict = review.to_dict(orient='records')[0]  # 첫 번째 행만 딕셔너리로 추가
        review_dict['제품명'] = i  # 제품명을 딕셔너리에 추가
        product_정보.append(review_dict)
    else:
        # 빈 값인 경우 처리 (예: '정보없음' 추가)
        product_정보.append({'제품명': i, '상세정보': '정보없음'})

# 최종 결과를 DataFrame으로 변환
result_df = pd.DataFrame(product_정보)

# 열 순서를 '제품명'이 첫 번째로 오도록 변경
result_df = result_df[['제품명'] + [col for col in result_df.columns if col != '제품명']]

result_df.to_csv('골프클럽_정보_250115.csv', encoding='utf-8-sig')
result_df.info()


# 누락 데이터 지우기
df_selc =  result_df.drop(['','상세정보'],axis=1)
df_selc.info()

# 데이터 저장하기
df_selc.to_csv('골프클럽_정보_250115.csv', encoding='utf-8-sig', index=False)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# 데이터 로드하기
a_cleaned = pd.read_csv('골프클럽_데이터_250115.csv')

# 제품에 따른 리뷰, 리뷰 작성자, 작성자의 평가를 가져오는 함수
# 제품 리뷰와 작성자의 정보를 가져오는 함수
def riview(name):
    url_1 = f'https://www.changegolf.co.kr/search?skeyword={name}'
    driver.get(url_1)
    time.sleep(1)
    
    # 제품 클릭
    driver.find_element(By.XPATH, '//*[@id="contents"]/section/div/div[1]/div[1]/div[1]/div/h5/a[1]').click()
    time.sleep(1)
    
    
    
        # 결과를 저장할 리스트 초기화
    reviews_data = []  # 리뷰와 작성자 정보를 함께 저장
        # 스크롤 반복
    for _ in range(30):    
        last_position = driver.execute_script("return window.pageYOffset")
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(1.5)
        new_position = driver.execute_script("return window.pageYOffset")
        if new_position == last_position:
            print("페이지 끝에 도달했습니다.")
            break
    # 'box-item' 클래스를 가진 div의 id 속성만 추출
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    review_ids = [box.get('id') for box in soup.find_all('div', class_='box-item') if box.get('id')]
    clicked_ids = set()

    # 각 리뷰 ID에 대해 버튼 클릭
    for review_id in review_ids:
        if review_id not in clicked_ids:  # 중복 여부 확인
            clicked_ids.add(review_id)  # 클릭한 ID를 집합에 추가
        # HTML 파싱
        try:
            review_content = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[4]/div/div[2]').text.strip()  # 정확한 클래스 이름으로 대체
            
            # 작성자 정보 (연령대, 타수 등)
            user_info = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[3]').text.strip()  # 정확한 클래스 이름으로 대체
            
            # 리뷰 내용
            user_id = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[1]/span[1]').text.strip()  # 정확한 클래스 이름으로 대체

            sco_1 = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[2]/span').text.strip()

            sco_2 = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[2]/ul/li[1]/span[1]').text.strip()

            sco_3 = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[2]/ul/li[2]/span[1]').text.strip()

            sco_4 = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[2]/ul/li[3]/span[1]').text.strip()

            sco_5 = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[2]/ul/li[4]/span[1]').text.strip()

            sco_6 = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[2]/ul/li[5]/span[1]').text.strip()

            sco_2_1 = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[2]/ul/li[1]/span[2]').text.strip()

            sco_3_1 = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[2]/ul/li[2]/span[2]').text.strip()

            sco_4_1 = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[2]/ul/li[3]/span[2]').text.strip()

            sco_5_1 = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[2]/ul/li[4]/span[2]').text.strip()

            sco_6_1 = driver.find_element(By.XPATH, value=f'//*[@id="{review_id}"]/div[1]/div[2]/ul/li[5]/span[2]').text.strip()
                
            # 데이터를 저장
            reviews_data.append({
                '사용자 ID': user_id,
                '사용자 나이': user_info[2:4],
                '리뷰뷰': review_content,
                '평가':sco_1,
                sco_2_1:sco_2,
                sco_3_1:sco_3,
                sco_4_1:sco_4,
                sco_5_1:sco_5,
                sco_6_1:sco_6,
            })
        except:
            reviews_data = []

    return reviews_data

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2

# 함수 실행하는 코드

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

# 웹사이트 접속
url = 'https://www.changegolf.co.kr/'  # 정확한 URL을 입력해 주세요
driver.get(url)
time.sleep(1)

driver.find_element(By.XPATH, value='//*[@id="header"]/div[1]/div[2]/div[1]/a/span').click()  # 로그인 클릭
time.sleep(1)

driver.find_element(By.XPATH, value='//*[@id="mem_userid"]').send_keys('jh1022wns@naver.com')  # 아이디입력
time.sleep(1)

driver.find_element(By.XPATH, value='//*[@id="flogin"]/div[1]/div[2]/div/input').send_keys('wnsghks6!')  # 비번 입력
time.sleep(1)

driver.find_element(By.XPATH, value='//*[@id="flogin"]/div[1]/div[4]/button').click()  # 로그인하기
time.sleep(1)
# 리뷰 데이터를 저장할 리스트
all_reviews = []

# 각 제품명에 대해 riview 함수 실행
for product_name in a_cleaned['제품명']:    
    reviews = riview(product_name)  # riview 함수 실행
    for review in reviews:
        review['제품명'] = product_name  # 제품명을 추가
    all_reviews.extend(reviews)  # 모든 리뷰 데이터 합치기


# 결과를 DataFrame으로 변환
df_reviews = pd.DataFrame(all_reviews)


df_reviews

# 데이터 저장
df_reviews.to_csv('골프클럽_리뷰_250117.csv',index=False, encoding='utf-8-sig')

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# 다나와에서 가격 가져오는 함수
def danawa_scraping(df_chage):
        # 브라우저 옵션 설정
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)


    all_results = []

    # df_chage의 각 행에 대해 반복
    for idx, row in df_chage.iterrows():
        try:
            search_term = f"{row['브랜드']} {row['제품명']} {row['클럽유형']}"

            url = f'https://search.danawa.com/dsearch.php?query={search_term}'
            driver.get(url)
            time.sleep(1)
            


            soup = BeautifulSoup(driver.page_source, 'html.parser')
            product1 = soup.find_all('div', 'spec_list')
            price = soup.find_all('p', 'price_sect')
            product_name = soup.find_all('p', 'prod_name')

            result_dict = {}
            # 제품명(검색어) 추가
            result_dict['제품명'] = row['제품명']

            # 파싱된 제품 이름 추가 및 관련성 체크
            if product_name:
                parsed_name = product_name[0].text.strip()
                # 검색어의 주요 키워드가 제품명에 포함되어 있는지 확인
                if any(keyword in parsed_name.lower() for keyword in row['제품명'].lower().split()):
                    result_dict['제품이름'] = parsed_name
                else:
                    result_dict['제품이름'] = "일치하지 않음"
            else:
                result_dict['제품이름'] = "정보 없음"

            # 제품 정보가 있는 경우 스펙 처리
            if product1:
                specs = product1[0].text.strip().split('/')
                specs = [spec.strip() for spec in specs if spec.strip()]
                
                # 기본 스펙 처리 연식
                spec_names = ['연식']
                for i, name in enumerate(spec_names):
                    if i < len(specs):
                        result_dict[name] = specs[i]
                    else:
                        result_dict[name] = "정보 없음"

                # 가격 처리
                for spec in specs:
                    if ':' in spec:
                        key, value = spec.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if '출시가' in key:
                            price_match = re.search(r'([0-9,]+)원', value)
                            if price_match:
                                result_dict['출시가'] = price_match.group(1) + '원'
                        else:
                            pass

            # 가격 처리 (제품 정보와 관계없이)
            if price:
                price_text = price[0].text.strip()
                price_value = re.search(r'([0-9,]+)원', price_text)
                if price_value:
                    result_dict['최저가'] = price_value.group(1) + '원'
                else:
                    result_dict['최저가'] = "가격 정보 없음"
            else:
                result_dict['최저가'] = "가격 정보 없음"

            all_results.append(result_dict)

        except Exception as e:
            print(f"Error processing {search_term}: {str(e)}")
            continue

    driver.quit()
    
    # 데이터프레임 생성
    df = pd.DataFrame(all_results)
    
    # 열 순서 정렬 (로프트각 열을 따로 정렬)
    columns = ['제품명', '제품이름', '연식']
    other_columns = [col for col in df.columns if col not in columns + ['최저가', '출시가']]
    final_columns = columns + other_columns + ['최저가', '출시가']
    
    return df[final_columns]

# 함수 실행
df_danawa_final = danawa_scraping(a_cleaned)

# 데이터 저장
df_danawa_final.to_csv('골프클럽_가격_250117.csv', index=False, encoding='utf-8-sig')