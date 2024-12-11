import os
import subprocess
import sys
import threading
import time
import streamlit as st
# try:
#     from langchain_teddynote import logging
# except ModuleNotFoundError as e:
#     subprocess.Popen([f'{sys.executable} -m pip install git+https://${{GITHUB_TOKEN}}@github.com/teddylee777/langchain-teddynote.git'], shell=True)
#     time.sleep(90)
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


from langchain_core.messages.chat import ChatMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader

from modules.utils import initialize_logging, get_model_list
# from task_llm.task_manager import task_execute_llm





# 로그 설정
initialize_logging("streamlit", set_enable=False)

st.set_page_config(layout="wide")
st.html("""
    <style>
        html, body {
            font-size: 14px;
        }
    </style>
    """
)


st.title("E-약은요 자료 생성")
st.markdown(
    """
E 약은요 자료 생성 작업
"""
)
   

# 모델 리스트 및 초기화
models = get_model_list()

# 대화 초기화 버튼 추가
with st.sidebar:
    # 모델 선택 버튼
    selected_model_main = st.selectbox("LLM 선택", models, index=0)
    # 프롬프트 선택 
    selected_prompt = st.selectbox(" 프롬프트 선택", ["기본모드", "약정보"], index=0)






# 백그라운드 작업 함수 (무한 루프 작업)
def background_task():
    """백그라운드에서 수행할 작업 (예: 데이터베이스 확인, API 호출 등)"""
    current_thread_id = threading.get_ident()  # 현재 실행 중인 스레드 ID
    print(f"🧵 백그라운드 스레드 시작 - 스레드 ID: {current_thread_id}   session thread_id : {st.session_state.get('thread_id')}")
    # st.session_state['thread_id'] = current_thread_id  # 스레드 ID 저장
    
    

    # while st.session_state['thread_running']:
    #     # if st.session_state.get('thread_id') != current_thread_id:
    #     #     print(f"🛑 현재 스레드 {current_thread_id}가 종료됩니다. 새로운 스레드가 실행 중입니다.")
    #     #     break  # 스레드가 중복 실행되지 않도록 중단


    #     st.session_state['last_run'] = time.strftime("%Y-%m-%d %H:%M:%S")
    #     print(f"🔄 백그라운드 작업 실행 중... 현재 시간: {st.session_state.get('last_run')}")
    #     print(f"🔄 st.session_state.get('llm_running') : {st.session_state.get('llm_running')}")

    #     # LLM 작업이 실행 중이지 않으면 작업 시작
    #     if not st.session_state.get('llm_running', False): 
    #         task_execute_llm()

    #     time.sleep(10)  # 10초마다 반복


# 백그라운드 스레드 실행 여부 확인 및 시작
# if 'thread_running' not in st.session_state:
    
#     st.session_state['llm_running'] = False  # LLM 실행 플래그
#     background_thread = threading.Thread(target=background_task, daemon=True)
#     background_thread.start()
#     st.session_state['thread_running'] = True
#     st.session_state['thread_id'] = threading.get_ident()    # 스레드 실행 플래그 - thread_id

#     st.write("🚀 백그라운드 작업을 시작했습니다.")


# if st.session_state['thread_running']:
#     st.write(f"🚀 백그라운드 작업 진행중.")
# else:
#     st.write("🚀 백그라운드 작업을 중단했습니다.")

# Streamlit 메인 UI
# st.title("📋 Streamlit 앱 - 백그라운드 작업 수행 중")
# st.write(f"백그라운드 작업의 마지막 실행 시간: {st.session_state.get('last_run', '실행 중이 아님')}")



    

    




