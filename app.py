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

# 2. 안전한 데이터 로드 함수 (절대로 에러를 뿜으며 죽지 않음)
@st.cache_data
def load_data():
    # 기본 백업 데이터 구조 세팅
    default_data = {
        "분류": ["농업기반", "농업기반", "농작물", "농작물", "농작물"],
        "순화 전 농업용어": ["관정", "몽리면적", "과경", "과숙", "포복경"],
        "순화 데이터(추천어)": ["우물", "물댈 면적", "열매꼭지", "농익음", "기는 줄기"],
        "한자": ["管井", "夢利面積", "果梗", "過熟", "匍匐莖"]
    }
    
    filename = "농업용어사전2.csv"
    
    # 만약 파일이 진짜 없으면 영어 이름 데이터 파일이 있는지 대조
    if not os.path.exists(filename) and os.path.exists("data.csv"):
        filename = "data.csv"
        
    if not os.path.exists(filename):
        return pd.DataFrame(default_data)
        
    # 한국어 인코딩 돌려가며 안전하게 읽기
    df = None
    for enc in ["utf-8-sig", "cp949", "euc-kr", "utf-8"]:
        try:
            df = pd.read_csv(filename, encoding=enc)
            df.columns = [str(c).strip() for c in df.columns]
            break
        except:
            continue
            
    # 읽어온 데이터 검증 및 열 이름 매칭 안전장치
    if df is not None:
        # 영문 열 이름을 한글로 변환
        rename_dict = {
            "LEGACY_WORD_NM": "순화 전 농업용어",
            "EASY_WORD_NM": "순화 데이터(추천어)",
            "CL_NM": "분류",
            "SRCLANG_NM": "한자"
        }
        df = df.rename(columns=rename_dict)
        
        # 필수 열이 하나라도 없으면 백업 데이터 반환
        if "순화 전 농업용어" not in df.columns or "순화 데이터(추천어)" not in df.columns:
            return pd.DataFrame(default_data)
        
        # '분류' 열이 없으면 기본값 채우기
        if "분류" not in df.columns:
            df["분류"] = "일반농업"
            
        return df
        
    return pd.DataFrame(default_data)

# 데이터 바인딩
try:
    df = load_data()
except:
    df = pd.DataFrame({
        "분류": ["일반"], 
        "순화 전 농업용어": ["데이터 에러"], 
        "순화 데이터(추천어)": ["파일을 확인해주세요"], 
        "한자": [""]
    })

# 3. 초성 추출 함수
def get_chosung(text):
    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    if not text or not isinstance(text, str):
        return ""
    code = ord(text[0]) - 44032
    if 0 <= code <= 11172:
        return CHOSUNG_LIST[code // 588]
    return text[0]

df['CHOSUNG'] = df['순화 전 농업용어'].apply(lambda x: get_chosung(str(x).strip()))

# 4. 헤더 및 UI
st.title("🌱 바른 농업용어 사전")
st.markdown(
    """
    <p style='color: #666666; font-size: 16px; margin-bottom: 25px;'>
    낯설고 어려운 농업 한자어와 전문 용어를 누구나 이해하기 쉬운 우리말로 풀이합니다. <br>
    농대생의 시선에서 단어의 가독성과 접근성을 높이기 위해 구축된 웹 사전입니다.
    </p>
    """, 
    unsafe_allow_html=True
)

search_query = st.text_input("🔍 검색할 농업 용어를 입력하세요 (예: 관정, 과숙 등)", "").strip()

st.markdown("---")
col1, col2 = st.columns([1, 2])

with col1:
    categories = ["전체"] + sorted(df['분류'].dropna().unique().tolist())
    selected_category = st.selectbox("📁 분류 선택", categories)

with col2:
    chosung_list = ["전체", "ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅅ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
    selected_chosung = st.select_slider("🔤 자음 필터", options=chosung_list, value="전체")

# 7. 데이터 필터링
filtered_df = df.copy()

if selected_category != "전체":
    filtered_df = filtered_df[filtered_df['분류'] == selected_category]

if selected_chosung != "전체":
    filtered_df = filtered_df[filtered_df['CHOSUNG'] == selected_chosung]

if search_query:
    filtered_df = filtered_df[
        filtered_df['순화 전 농업용어'].astype(str).str.contains(search_query, case=False, na=False) |
        filtered_df['순화 데이터(추천어)'].astype(str).str.contains(search_query, case=False, na=False)
    ]

st.markdown(f"**검색 결과:** 총 `{len(filtered_df)}`개의 단어가 검색되었습니다.")

if filtered_df.empty:
    st.info("검색 결과가 없습니다. 다른 단어를 입력하거나 필터를 변경해 보세요.")
else:
    for _, row in filtered_df.iterrows():
        hanja_text = f"({row['한자']})" if '한자' in row and pd.notna(row['한자']) and str(row['한자']).strip() != "" else ""
        
        with st.container():
            st.markdown(
                f"""
                <div style="background-color: #f9f9f9; padding: 18px; border-radius: 8px; border-left: 5px solid #2E7D32; margin-bottom: 12px;">
                    <span style="font-size: 12px; background-color: #E8F5E9; color: #2E7D32; padding: 3px 8px; border-radius: 4px; font-weight: bold;">{row['분류']}</span>
                    <h3 style="margin: 10px 0 5px 0; color: #111111;">
                        {row['순화 전 농업용어']} 
                        <span style="font-size: 14px; color: #888888; font-weight: normal;">{hanja_text}</span>
                    </h3>
                    <p style="margin: 5px 0 0 0; font-size: 16px; color: #2E7D32; font-weight: bold;">
                        💡 추천 순화어: <span style="font-size: 18px;">{row['순화 데이터(추천어)']}</span>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown("---")
st.caption("© 2026 바른 농업용어 사전 프로젝트. All rights reserved.")
