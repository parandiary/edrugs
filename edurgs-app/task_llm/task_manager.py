import os
import sys
import time

import psycopg2


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.database import get_task, save_task_answer, update_task_status

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import load_prompt
from langchain.schema import Document

# 진행 상태 변수
llm_running = False


def run_task():
    while True:
        print("🚀 작업이 실행 중...")
        # 작업 대상 목록 조회
        task_list = get_task()
        print("작업 대상 목록:", len(task_list))
        # print("작업 대상 목록:", task_list)

        # task_list가 비어있지 않은 경우에만 작업 수행
        if task_list:
            for task in task_list:
                task_id, drug_code, drug_name, drug_company, crawal_text, parse_content, drug_url, status, answer1, answer2, answer3, answer4, answer5, answer6, answer = task
                try:
                    print(f"✅ 작업 처리 중 {drug_name}")
                    # 상태를 작업중으로 변경
                    update_task_status(task_id, "PROCESSING")

                    # print(f"✅ crawal_text {crawal_text}")
                    document = Document(page_content=crawal_text, metadata={"source": drug_url, "drug": drug_name, "company": drug_company })
                    response = process_task_llm(drug_name, document)  # 각 작업을 처리하는 함수 호출
                    # 결과 저장
                    save_task_answer(task_id, drug_code, response)
                    print(f"Task {drug_name} save ok ")

                except Exception as e:
                    print(f"❌ 작업 처리 중 오류 발생: {e}")

        time.sleep(10)  # 5초마다 반복

            
def process_task_llm(drug_name, document):
    print("process_task")

    # task_id, drug_code, drug_name, drug_company, crawal_text, parse_content, status, answer1, answer2, answer3, answer4, answer5, answer6, answer = task

    # 크롤링된 원본 텍스트 분리
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents([document])
    # # splits = text_splitter.split_documents(task.parse_content)
    print(f"Task {drug_name} > {len(splits)}")

    # vector store 정의
    vectorstore = FAISS.from_documents(documents=splits, embedding=FastEmbedEmbeddings())

    # retriever 설정
    retriever = vectorstore.as_retriever(search_type="similarity")
    # 유사도 검색 테스트
    # query = "약을 제조하는 업체명은 뭐야?"
    # search_result = retriever.get_relevant_documents(query)
    # print(search_result)

    # LLM 생성
    # llm = ChatOllama(model="EEVE-Korean-Instruct-10.8B-v1.0-Q5_0:latest", temprature=0)
    llm = ChatOllama(model="EEVE-Korean-Instruct-10.8B-v1.0-Q4_K_M", temprature=0)

    # 프롬프트 로드
    prompt = load_prompt("prompts/drugs.yaml", encoding="utf-8")
    print(prompt.format(context=retriever, drug=drug_name))

    # 단계 8: 체인(Chain) 생성
    chain = (
        {"context": retriever, "drug": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print(f"Task {drug_name} > response wait ... ")
    response = chain.invoke(drug_name)
    print(f"Task {drug_name} reaponse : {response}")

    return response

    

def init_llm():
    global llm_running
    llm_running = False

    # llm = ChatOllama(model="llama3.2", temprature=0)
    # llm = ChatOllama(model="EEVE-Korean-Instruct-10.8B-v1.0-Q5_0:latest", temprature=0)
        



if __name__ == "__main__":
    print("🚀 작업 시작")
    run_task()



