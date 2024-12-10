import requests
import re
from bs4 import BeautifulSoup
# from drug_info_parser import *

def fetch_drug_info(drug_code):
    """의약품 정보를 크롤링합니다."""
    url = f"https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={drug_code}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            drug_name = soup.find("th", string="제품명").find_next("td").get_text(strip=True)
            company = soup.find("th", string="업체명").find_next("button").get_text(strip=True)

            # 크롤링된 원본 텍스트 저장
            # crawal_text = soup.get_text(separator=' ', strip=True)

            # 각 항목별 데이타 추출
            parse_content = parse_html_content(soup)
            print(f"parse_content : {parse_content}")


            return {
                'drug_name': drug_name,
                'company': company,
                'url': url,
                'crawal_text': soup.get_text(separator=' ', strip=True),
                'parse_content': parse_content
            }
        else:
            return None
    except Exception as e:
        return None
    


# =========== html에서 각 항목별 데이터 추출 함수 ===================

def extract_basic_info(soup):
    """기본정보 추출"""
    basic_info = {}
    table = soup.find('h2', string='기본정보').find_next('table')
    # print(f"table: {table}")
    for row in table.find_all('tr'):
        key_elem = row.find('th')
        value_elem = row.find('td')
        if key_elem and value_elem:
            key = key_elem.get_text(strip=True)
            value = value_elem.get_text(strip=True)
            basic_info[key] = value
        else:
            # th 또는 td가 없으면 건너뛰기
            continue
    
    # print(f"basic_info: {basic_info}")
    return basic_info


def extract_ingredient_and_quantity(soup):
    """원료약품 및 분량 추출"""
    ingredient_info = []
    sections = soup.find_all('h3', string='원료약품 및 분량')
    for section in sections:
        table = section.find_next('table')
        if table:
            for row in table.find_all('tr')[1:]:  # 헤더 제외
                cells = row.find_all('td')
                if len(cells) > 1:
                    ingredient = {
                        '순번': cells[0].get_text(strip=True),
                        '성분명': cells[1].get_text(strip=True),
                        '분량': cells[2].get_text(strip=True),
                        '단위': cells[3].get_text(strip=True),
                        '규격': cells[4].get_text(strip=True),
                        '성분정보': cells[5].get_text(strip=True),
                        '비교': cells[6].get_text(strip=True) if len(cells) > 6 else ''
                    }
                    ingredient_info.append(ingredient)
    return ingredient_info


def extract_efficacy(soup):
    """효능효과 추출"""
    # id : _ee_doc 의 내용
    efficacy_div = soup.find('div', id='_ee_doc')
    
    if efficacy_div:
        # 해당 div의 텍스트 추출
        efficacy_text = efficacy_div.get_text(strip=True)
        return efficacy_text
    return ''

def extract_dosage(soup):
    """용법용량 추출"""
    find_div = soup.find('div', id='_ud_doc')
    
    if find_div:
        # 해당 div의 텍스트 추출
        find_text = find_div.get_text(strip=True)
        return find_text
    return ''


def extract_precautions(soup):
    """사용상의 주의사항 추출"""
    find_div = soup.find('div', id='_nb_doc')
    
    if find_div:
        # 해당 div의 텍스트 추출
        find_text = find_div.get_text(strip=True)
        return find_text
    return ''


def extract_reexamination_info(soup):
    """재심사, RMP, 보험, 기타정보 추출"""
    section = soup.find('h3', string=re.compile('재심사, RMP, 보험, 기타정보'))
    # print(f"section: {section}")
    table = section.find_next('table')
    # print(f"table: {table}")

    # section = soup.find('div', class_='info_sec', id='scroll_07')

    if table:
        # 테이블 안의 각 항목 추출
        info = {}
        rows = table.find_all('tr')

        
        for row in rows:
            # 각 행에서 'th'와 'td'를 찾기
            th = row.find('th')
            td = row.find('td')
            
            if th and td:
                key = th.get_text(strip=True)
                value = td.get_text(strip=True)
                info[key] = value
            
        # print(f"reexamination : {info}")
        return info
    return {}


def extract_production_performance(soup):
    """생산실적 추출"""
    # production_section = soup.find('h3', string='생산실적')
    # print(f"production_section : {production_section}")
    # table = production_section.find_next('table')
    # print(f"table : {table}")

    section = soup.find('div', class_='info_sec', id='scroll_08')
    # print(f"section : {section}")

    if section:
        # 테이블 안의 각 행 추출
        production_data = []
        rows = section.find_all('tr')
        
        for row in rows[1:]:  # 첫 번째 행은 제목이므로 제외
            cells = row.find_all('td')
            if len(cells) == 2:
                year = cells[0].get_text(strip=True)
                production_value = cells[1].get_text(strip=True)
                production_data.append({'year': year, 'production_value': production_value})

        # print(f"production_data : {production_data}")
        return production_data
    return []


def parse_html_content(soup):
    """HTML 전체 파싱 및 각 항목별 데이터 추출"""
    # soup = BeautifulSoup(html_content, 'html.parser')
    result = {
        '기본정보': extract_basic_info(soup),
        '원료약품 및 분량': extract_ingredient_and_quantity(soup),
        '효능효과': extract_efficacy(soup),
        '용법용량': extract_dosage(soup),
        '사용상의 주의사항': extract_precautions(soup),
        '재심사, RMP, 보험, 기타정보': extract_reexamination_info(soup),
        '생산실적': extract_production_performance(soup)
    }
    return result


