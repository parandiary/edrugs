import os
import sys
import streamlit as st
from urllib.parse import parse_qs
import time
# 모듈 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# DB 연결 및 데이터 조회 함수 불러오기
from modules.database import get_db_connection, get_task_by_id, get_complated_tasks

st.set_page_config(layout="wide")
st.html("""
    <style>
        html, body {
            font-size: 14px;
        }
    </style>
    """
)

# 🔥 메인 앱 시작
st.title("💊 E-Drug 정보 페이지")

# 레이아웃 설정: 두 개의 컬럼 (왼쪽과 오른쪽)
col1, col2 = st.columns([1, 2])  # 왼쪽은 1, 오른쪽은 2의 비율로 설정

# task 조회
tasks = get_complated_tasks()




def generate_pdf(selected_task):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=selected_task[14])
    pdf.output("output.pdf", "F")

def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM task_list WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()

    st.success(f"Task with ID {task_id} has been deleted.")

def update_task_status(task_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE task_list SET status = %s WHERE id = %s", (status, task_id))
    conn.commit()
    conn.close()

    st.success(f"Task with ID {task_id} has been updated to {status}.")

    




# 스타일 설정
st.markdown("""
    <style>
        .col1-container {
            height: 600px;
            overflow-y: scroll;
        }
        .col2-container {
            height: 600px;
            overflow-y: scroll;
        }
        .stButton > button {
            width: 100% !important;  /* 버튼을 부모의 100% 너비로 설정 */
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# 첫 번째 컬럼: 약 목록 표시
with col1:
    st.header("🔍 의약품 목록")
    # col1에 스크롤 추가
    # with st.container():
    # st.markdown('<div class="col1-container">', unsafe_allow_html=True, key="col1-container")
    for task in tasks:
        task_id, drug_code, drug_name, drug_company, crawal_text, parse_content, drug_url, status, answer1, answer2, answer3, answer4, answer5, answer6, answer = task
        task_info = f"{drug_name} ({drug_code}) - {drug_company}"

        # 버튼 스타일링
        st.markdown("""
            <style>
                .stButton > button {
                    width: 100% !important;  /* 버튼을 부모의 100% 너비로 설정 */
                    font-size: 16px;
                }
            </style>
        """, unsafe_allow_html=True)

        # 버튼 클릭 시 선택된 항목을 세션에 저장
        if st.button(task_info, key=f"task_{task_id}"):
            st.session_state.selected_task = task  # 클릭된 작업을 세션에 저장
    # st.markdown('</div>', unsafe_allow_html=True)

# Divider: 두 컬럼 사이에 구분선 추가
# st.markdown("<hr>", unsafe_allow_html=True)

# 두 번째 컬럼: 선택된 항목의 상세 내용 표시
with col2:
    # st.markdown('<div class="col2-container">', unsafe_allow_html=True)

    # 카드 스타일 적용
    st.markdown("""
        <style>
            .card {
                border: 2px solid #007bff;
                border-radius: 10px;
                padding: 20px;
                background-color: #f8f9fa;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
        </style>
    """, unsafe_allow_html=True)

    # 카드 시작
    # st.markdown('<div class="card">', unsafe_allow_html=True)

    # 오른쪽: 선택된 항목의 상세 내용 표시
    if 'selected_task' in st.session_state:
        selected_task = st.session_state.selected_task
        st.header(f"📄 {selected_task[2]} 상세 정보")  # 약물 이름
        col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])

        with col2:
            # PDF 생성 버튼
            if st.button("📄 PDF 생성"):
                generate_pdf(selected_task)
        with col3:
            # 편집 버튼 (단순히 텍스트 편집 모드로 보여줌)
            if st.button("✏️ 편집"):
                st.text_area("편집하기", value=selected_task[14], height=150)
        with col4:
            # 저장 버튼 (저장 처리 - 실제 구현 필요)
            if st.button("💾 저장"):
                st.success("저장되었습니다.")

        with col5:
            # 삭제 버튼 (작업 삭제 - 실제 구현 필요)
            if st.button("❌ 삭제"):
                # print(f"삭제 버튼 클릭됨. 작업 ID: {selected_task[0]}")
                # @st.dialog("삭제하시겠습니까?")
                delete_task(selected_task[0])  # 삭제 함수 구현 필요
                st.session_state.selected_task = None  # 삭제 후 세션에서 항목 제거

                # st.popover(f"작업 ID {selected_task[0]}가 삭제되었습니다.")
                # st.success(f"작업 ID {selected_task[0]}가 삭제되었습니다.")
            

        st.write(f"**약물 코드**: {selected_task[1]}")  # 약물 코드
        st.write(f"**제조사**: {selected_task[3]}")  # 제조사
        st.write(f"**상세 내용**: {selected_task[14]}")  # 상세 내용
        
    else:
        st.write("🔍 목록에서 항목을 클릭하여 상세 정보를 확인하세요.")

    # 카드 닫기
    # st.markdown('</div>', unsafe_allow_html=True)
    # st.markdown('</div>', unsafe_allow_html=True)  # col2 스크롤 영역 닫기
    

