import os
import sys
import time
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.database import get_db_connection, save_to_database, get_task_list, delete_task, reserv_task, get_reserve_task_list
from modules.drug_info_crawler import fetch_drug_info
from modules.utils import display_task_list, display_reserv_task_list


st.set_page_config(layout="wide")
st.html("""
    <style>
        html, body {
            font-size: 14px;
        }
    </style>
    """
)

# 상태별 색상 정의
STATUS_COLORS = {
    'RESERVE': '#cce5ff',  # 파란색 (INFO)
    'PROCESSING': '#ece5ff',  # 
    'COMPLETE': '#d4edda',  # 녹색 (SUCCESS)
    'DEFAULT': '#ffffff'  # 기본 흰색
}




st.sidebar.title("🔧 작업 옵션")
llm_model = st.sidebar.selectbox("🧠 LLM 모델 선택", ["GPT-4", "GPT-3.5", "Custom Model"], index=0)
prompt_option = st.sidebar.selectbox("📝 프롬프트 선택", ["기본 프롬프트", "분석 프롬프트", "요약 프롬프트"], index=0)

st.sidebar.write(f"**선택된 모델:** {llm_model}")
st.sidebar.write(f"**선택된 프롬프트:** {prompt_option}")


# sidebar에 상태가 RESERVE의 작업 목록을 5개 표시
# st.sidebar.header("📝 예약 작업 목록")
st.sidebar.title("📅 예약된 작업 목록")
reserve_tasks = get_reserve_task_list()
# 최대 5개의 작업만 표시
for i, task in enumerate(reserve_tasks[:5]):
    task_id, drug_code, drug_name, company, status = task

    background_color = STATUS_COLORS.get(status, STATUS_COLORS['DEFAULT'])

    st.sidebar.markdown(f"""
    <div style="
        background-color: {background_color}; 
        border-radius: 8px; 
        padding: 10px; 
        margin-bottom: 10px; 
        border: 1px solid #007bff;
        font-size: 0.9rem;
    ">
        <strong>🧾 {drug_name}</strong><br>
        <small>💊 코드: {drug_code}</small><br>
        <small>🏢 제조사: {company}</small>
    </div>
    """, unsafe_allow_html=True)



# with st.sidebar.form(key='reserve_task_form'):
#     reload_button = st.form_submit_button(label='🔄',help= '새로고침')

# if reload_button:
#     reserve_tasks = get_reserve_task_list()
#     # 최대 5개의 작업만 표시
#     for i, task in enumerate(reserve_tasks[:5]):
#         task_id, drug_code, drug_name, company, status = task

#         background_color = STATUS_COLORS.get(status, STATUS_COLORS['DEFAULT'])

#         st.sidebar.markdown(f"""
#         <div style="
#             background-color: {background_color}; 
#             border-radius: 8px; 
#             padding: 10px; 
#             margin-bottom: 10px; 
#             border: 1px solid #007bff;
#             font-size: 0.9rem;
#         ">
#             <strong>🧾 {drug_name}</strong><br>
#             <small>💊 코드: {drug_code}</small><br>
#             <small>🏢 제조사: {company}</small>
#         </div>
#         """, unsafe_allow_html=True)







# 작업 대상 코드 입력 폼
st.title("💊 의약품 작업 목록")
with st.form(key='drug_form'):
    drug_code = st.text_input('약 코드 입력 (예: 200300406)', '')
    submit_button = st.form_submit_button(label='🔍 정보 조회 및 저장')

if submit_button:
    if not drug_code:
        st.error("약 코드를 입력하세요.")
    else:
        st.info(f"💡 {drug_code}의 의약품 정보를 가져오는 중...")
        drug_info = fetch_drug_info(drug_code)
        
        if drug_info:
            st.write("### 📝 의약품 정보")
            st.write(f"**약 이름:** {drug_info['drug_name']}")
            st.write(f"**제조사:** {drug_info['company']}")
            st.write(f"**URL:** [링크로 이동하기]({drug_info['url']})")
            
            save_to_database(drug_code, drug_info['drug_name'], drug_info['company'], drug_info['url'], drug_info['crawal_text'], drug_info['parse_content'])


# 작업 목록 표시
st.subheader("📋 작업 목록")
# 🔍 **검색 조건 입력 영역**
# st.title("📋 작업 목록 조회 및 검색")
with st.form(key='search_form'):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        search_drug_code = st.text_input("🔍 약 코드", placeholder="예: 2003")
    with col2:
        search_drug_name = st.text_input("🔍 약 이름", placeholder="예: 타이레놀")
    with col3:
        search_company = st.text_input("🏢 제조사", placeholder="예: 한국제약")
    with col4:
        search_status = st.selectbox("📋 상태", options=["", "RESERVE", "DONE", "COMPLETE", "DEFAULT"], index=0)
    
    search_button = st.form_submit_button(label='🔍 검색')

if search_button:
    tasks = get_task_list(
        drug_code=search_drug_code.strip() if search_drug_code else None,
        drug_name=search_drug_name.strip() if search_drug_name else None,
        company=search_company.strip() if search_company else None,
        status_filter=search_status if search_status else None
    )
else:
    tasks = get_task_list()  # 기본 전체 작업 목록


# 🔍 사이드바에 상태 필터 추가
# status_filter = st.selectbox(
#     "📂 작업 상태 필터",
#     ["전체", "RESERVE", "DONE", "DEFAULT"],
#     index=0
# )
# tasks = get_task_list(status_filter=None if status_filter == "전체" else status_filter)


# `reload_tasks`가 True일 경우 작업 목록을 갱신
if "reload_tasks" not in st.session_state:
    st.session_state.reload_tasks = False

# 작업 목록이 갱신된 상태라면 다시 로드
if st.session_state.reload_tasks:
    tasks = get_task_list(status_filter=None if status_filter == "전체" else status_filter)  # 작업 목록 갱신
    st.session_state.reload_tasks = False  # 플래그 리셋





# display_task_list(tasks)
if tasks:
    for task in tasks:
        task_id, drug_code, drug_name, company, status = task
        
        # 상태에 따라 배경색을 동적으로 변경
        #set_expander_background_color_v2(status)
        background_color = STATUS_COLORS.get(status, STATUS_COLORS['DEFAULT'])

        st.markdown(f"""
            <style>
            .expander-{task_id} > div:first-child {{
                background-color: {background_color} !important;
            }}
            .stExpander > details {{
                background-color: {background_color} !important;
            }}
            </style>
        """, unsafe_allow_html=True)

        with st.expander(f"🧾 **ID:** {task_id} | **약 코드:** {drug_code} | **이름:** {drug_name} | **상태:** {status}"):
            st.write(f"**약 이름:** {drug_name}  |  **상태:** {status}")
            st.write(f"**제조사:** {company}")
            st.write(f"**URL:** [링크로 이동하기](https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={drug_code})")

            # 버튼 레이아웃 (같은 행에 요약정보 생성 버튼과 삭제 버튼을 추가)
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])  # 비율로 칸의 크기를 조절 ([2, 1]로 하면 col1이 더 넓음)

            with col2:
                # 요약정보 생성 버튼
                view_drug_info_button = st.button(f"📝 E약은요정보", key=f"view_edrug_info_{task_id, drug_code}")
            
            with col3:
                # 요약정보 생성 버튼
                reserve_task_button = st.button(f"📝 요약생성 예약", key=f"reserve_task_{task_id, drug_code}")
            
            with col4:
                # 삭제 버튼
                delete_button = st.button(f"❌ 삭제", key=f"delete_{task_id}")

            

            # 삭제 버튼 클릭 시 처리
            if delete_button:
                delete_task(task_id)
                st.success(f"작업 ID {task_id}가 삭제되었습니다.")

                # 삭제 후 작업 목록 새로 고침
                st.session_state.reload_tasks = True  # 새로 고침 플래그 설정
                time.sleep(1)  # 잠시 대기 후 새로 고침
                st.rerun()

            # 요약정보 생성 버튼 클릭 시 처리
            if reserve_task_button:
                # st.info(f"작업 ID {task_id}의 요약정보를 생성 중입니다...")
                reserv_task(task_id, drug_code)  # 요약정보 생성 함수 호출
                # st.success(f"작업 ID {task_id}의 요약정보가 생성되었습니다.")
                
            if view_drug_info_button:
                # e-drug정보 페이지로 이동
                # st.Page("e-grug")
                st.rerun()
                # st.experimental_set_query_params(page="e-drug", task_id=task_id)
                # st.query_params(page="e-drug", task_id=task_id)
                # st.rerun()

                
                #st.write(f"**URL:** [링크로 이동하기](https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={drug_code})")
                
                
                

                
else:
    st.info("작업 목록이 없습니다.")


refreshrate =10
refreshrate = int(refreshrate)
# driver = webdriver.Chrome(executable_path="C:\\Users\\z0044wmy\\Desktop\\chromedriver_win32\\chromedriver.exe")

while True:
    time.sleep(refreshrate)
    reserve_tasks = get_reserve_task_list()

    # reload_button trigger
    # st.session_state.reload_reserve = True


    # driver.refresh()