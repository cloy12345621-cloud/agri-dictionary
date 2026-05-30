import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정 (가독성 중심의 깔끔한 테마)
st.set_page_config(
    page_title="바른 농업용어 사전",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 데이터 불러오기 함수 (한국어 인코딩 깨짐 및 예외 처리 완벽 방어)
@st.cache_data
def load_data():
    # 윈도우 엑셀 CSV의 다양한 인코딩 형식을 순차적으로 시도합니다.
    encodings = ["utf-8-sig", "cp949", "euc-kr", "utf-8"]
    df = None
    
    for enc in encodings:
        try:
            df = pd.read_csv("농업용어사전2.csv", encoding=enc)
            # 파일은 읽었으나 실제 데이터 열이 정상인지 검증
            if "순화 전 농업용어" in df.columns:
                break
        except:
            continue
            
    # 모든 인코딩 시도가 실패하거나 파일이 없을 경우 작동할 백업 샘플 데이터
    if df is None or "순화 전 농업용어" not in df.columns:
        data = {
            "분류": ["농업기반", "농업기반", "농작물", "농작물", "농작물"],
            "순화 전 농업용어": ["관정", "몽리면적", "과경", "과숙", "포복경"],
            "순화 데이터(추천어)": ["우물", "물댈 면적", "열매꼭지", "농익음", "기는 줄기"]
        }
        df = pd.DataFrame(data)
    return df

df = load_data()

# 3. 초성 추출 함수 (한글 자음 필터링용)
def get_chosung(text):
    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    if not text or not isinstance(text, str):
        return ""
    code = ord(text[0]) - 44032
    if 0 <= code <= 11172:
        return CHOSUNG_LIST[code // 588]
    return text[0]

# 실제 엑셀 파일의 '순화 전 농업용어' 열을 기준으로 초성을 만듭니다.
df['CHOSUNG'] = df['순화 전 농업용어'].apply(get_chosung)

# 4. 헤더 및 기획 의도 소개
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

# 5. 검색창 UI
search_query = st.text_input("🔍 검색할 농업 용어를 입력하세요 (예: 관정, 과숙 등)", "").strip()

# 6. 카테고리(분류) 및 자음 필터
st.markdown("---")
col1, col2 = st.columns([1, 2])

with col1:
    # 엑셀의 '분류' 열 데이터를 연동합니다.
    categories = ["전체"] + sorted(df['분류'].dropna().unique().tolist())
    selected_category = st.selectbox("📁 분류 선택", categories)

with col2:
    chosung_list = ["전체", "ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅅ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
    selected_chosung = st.select_slider("🔤 자음 필터", options=chosung_list, value="전체")

# 7. 데이터 필터링 로직
filtered_df = df.copy()

if selected_category != "전체":
    filtered_df = filtered_df[filtered_df['분류'] == selected_category]

if selected_chosung != "전체":
    filtered_df = filtered_df[filtered_df['CHOSUNG'] == selected_chosung]

if search_query:
    filtered_df = filtered_df[
        filtered_df['순화 전 농업용어'].str.contains(search_query, case=False, na=False) |
        filtered_df['순화 데이터(추천어)'].str.contains(search_query, case=False, na=False)
    ]

# 8. 결과 출력 (사전식 UI 카드 배치)
st.markdown(f"**검색 결과:** 총 `{len(filtered_df)}`개의 단어가 검색되었습니다.")

if filtered_df.empty:
    st.info("검색 결과가 없습니다. 다른 단어를 입력하거나 필터를 변경해 보세요.")
else:
    for _, row in filtered_df.iterrows():
        # 파일에 한자 열이 없을 수도 있으므로 안전하게 처리합니다.
        hanja_text = f"({row['한자']})" if '한자' in row and pd.notna(row['한자']) else ""
        
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

# 후면 푸터
st.markdown("---")
st.caption("© 2026 바른 농업용어 사전 프로젝트. All rights reserved.")
