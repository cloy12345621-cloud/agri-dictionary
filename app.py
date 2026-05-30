import streamlit as st
import pandas as pd
import os

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="바른 농업용어 사전",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 데이터 자동 탐색 및 로드 함수 (이름이 달라도 무조건 찾아옴)
@st.cache_data
def load_data():
    df = None
    target_file = None
    
    # 깃허브 폴더에 들어있는 모든 파일을 뒤집니다.
    all_files = os.listdir(".")
    
    # 1순위: '농업용어'나 'data'가 들어간 CSV/엑셀 파일을 찾습니다.
    for f in all_files:
        if ("농업" in f or "data" in f or "사전" in f) and (f.endswith(".csv") or f.endswith(".xlsx")):
            target_file = f
            break
            
    # 2순위: 못 찾았다면 폴더 내의 아무 CSV나 엑셀 파일이나 잡습니다.
    if not target_file:
        for f in all_files:
            if f.endswith(".csv") or f.endswith(".xlsx"):
                if f != "requirements.txt": # 설정 파일은 제외
                    target_file = f
                    break

    # 파일을 찾았다면 강제로 읽어들이기 시작합니다.
    if target_file:
        encodings = ["utf-8-sig", "cp949", "euc-kr", "utf-8"]
        for enc in encodings:
            try:
                if target_file.endswith(".csv"):
                    df = pd.read_csv(target_file, encoding=enc)
                else:
                    df = pd.read_excel(target_file)
                
                # 열 이름에 맞게 데이터 컬럼 정제 (한글 깨짐 및 공백 방지)
                df.columns = [c.strip() for c in df.columns]
                break
            except:
                continue

    # 3순위: 만약 파일 읽기가 실패했거나 컬럼이 안 맞으면 작동할 백업 샘플 데이터
    if df is None or not any(col in df.columns for col in ["순화 전 농업용어", "LEGACY_WORD_NM"]):
        data = {
            "분류": ["농업기반", "농업기반", "농작물", "농작물", "농작물"],
            "순화 전 농업용어": ["관정", "몽리면적", "과경", "과숙", "포복경"],
            "순화 데이터(추천어)": ["우물", "물댈 면적", "열매꼭지", "농익음", "기는 줄기"]
        }
        df = pd.DataFrame(data)
    else:
        # 엑셀 파일 열 이름을 코드와 통일시키는 안전장치
        rename_dict = {
            "LEGACY_WORD_NM": "순화 전 농업용어",
            "EASY_WORD_NM": "순화 데이터(추천어)",
            "CL_NM": "분류"
        }
        df = df.rename(columns=rename_dict)
        
    return df

df = load_data()

# 3. 초성 추출 함수
def get_chosung(text):
    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    if not text or not isinstance(text, str):
        return ""
    code = ord(text[0]) - 44032
    if 0 <= code <= 11172:
        return CHOSUNG_LIST[code // 588]
    return text[0]

# 안정적으로 존재하는 열을 기준으로 초성 생성
col_target = "순화 전 농업용어" if "순화 전 농업용어" in df.columns else df.columns[1]
df['CHOSUNG'] = df[col_target].apply(lambda x: get_chosung(str(x).strip()))

# 4
