import logging
import streamlit as st

def initialize_logging(module_name, set_enable=True):
    """로깅 초기화."""
    logging.basicConfig(level=logging.INFO)
    logging.getLogger(module_name).setLevel(logging.INFO if set_enable else logging.ERROR)

def get_model_list():
    """모델 목록을 반환합니다."""
    return [
        "EEVE-Korean-Instruct-10.8B-v1.0-Q5_0:latest",
        "llama3.2",
        "gpt-4o", 
        "gpt-4-turbo", 
        "gpt-4o-mini"
    ]

def display_task_list(tasks):
    """작업 목록을 Streamlit에 표시합니다."""
    for task_id, drug_code, drug_name, drug_company in tasks:
        with st.expander(f"🧾 **ID:** {task_id} | **약 코드:** {drug_code} | **이름:** {drug_name}"):
            st.write(f"**약 이름:** {drug_name}")
            st.write(f"**제조사:** {drug_company}")
            st.write(f"**URL:** [링크로 이동하기](https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail?itemSeq={drug_code})")

# 예약된 작업 목록 출력
def display_reserv_task_list(tasks):
    """예약 작업 목록을 Streamlit에 표시합니다."""
    for task_id, drug_code, drug_name, drug_company, status in tasks:
        st.sidebar.expander(f"🧾 **ID:** {task_id} | **약 코드:** {drug_code} | **이름:** {drug_name}")
        # with st.sidebar.expander(f"🧾 **ID:** {task_id} | **약 코드:** {drug_code} | **이름:** {drug_name}"):
            # st.sidebar.write(f"**약 이름:** {drug_name}")
            # st.sidebar.write(f"**제조사:** {drug_company}")
            # # 약 상세 정보 페이지로 이동
            # st.sidebar.write(f"[상세정보이동](/task-detail?id={task_id})")
