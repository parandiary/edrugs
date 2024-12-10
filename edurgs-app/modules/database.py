import json
import psycopg2
import streamlit as st

DB_CONFIG = {
    'host': 'localhost',
    'port': 15432,
    'database': 'edrugs',
    'user': 'docmost',
    'password': 'STRONG_DB_PASSWORD'
}

def get_db_connection():
    """데이터베이스 연결을 생성합니다."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        st.error(f"데이터베이스 연결에 실패했습니다: {e}")
        return None

def save_to_database(drug_code, drug_name, company, url, crawal_text, parse_content):
    """데이터베이스에 의약품 정보를 저장합니다."""
    conn = get_db_connection()
    if conn is None:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO task_list (drug_code, drug_name, drug_company, drug_url, crawal_text, parse_content) VALUES (%s, %s, %s, %s, %s, %s)",
                (drug_code, drug_name, company, url, crawal_text,  json.dumps(parse_content),)
            )
        conn.commit()
        st.success(f"✅ 데이터베이스에 {drug_code}가 성공적으로 저장되었습니다!")
    except Exception as e:
        st.error(f"데이터베이스에 저장하는 중 오류가 발생했습니다: {e}")
    finally:
        conn.close()

# 작업대상 목록을 가져오는 함수
def get_task_list(drug_code=None, drug_name=None, company=None, status_filter=None):
    """
    작업 목록을 가져오는 함수.
    
    Args:
        drug_code (str, optional): 검색할 약 코드 (부분 검색 가능).
        drug_name (str, optional): 검색할 약 이름 (부분 검색 가능).
        company (str, optional): 검색할 회사명 (부분 검색 가능).
        status_filter (str, optional): 필터링할 작업의 상태 (RESERVE, COMPLETE, DEFAULT). 
                                        None일 경우 모든 작업을 가져옵니다.
    
    Returns:
        list: 작업 목록 리스트 (id, drug_code, drug_name, drug_company, status)
    """
    try:
        conn = get_db_connection()
        if conn is None:
            return []

        cursor = conn.cursor()

        # 🛠️ WHERE 조건을 동적으로 구성
        query = "SELECT id, drug_code, drug_name, drug_company, status FROM task_list"
        where_clauses = []  # 조건을 저장할 리스트
        params = []  # 쿼리 파라미터

        # 🔍 조건이 있는 경우 WHERE 절에 추가
        if drug_code:
            where_clauses.append("drug_code LIKE %s")
            params.append(f"%{drug_code}%")  # 부분 검색을 위해 % 추가
        
        if drug_name:
            where_clauses.append("drug_name LIKE %s")
            params.append(f"%{drug_name}%")  # 부분 검색을 위해 % 추가
        
        if company:
            where_clauses.append("drug_company LIKE %s")
            params.append(f"%{company}%")  # 부분 검색을 위해 % 추가
        
        if status_filter:
            if status_filter == "DEFAULT":
                where_clauses.append("coalesce(status, '') = ''")
            elif status_filter == "COMPLATE":
                status_filter = "DONE"  # COMPLATE를 DONE으로 변경
                where_clauses.append("status = %s")
            else:
                where_clauses.append("status = %s")

            # where_clauses.append("status = %s")
            params.append(status_filter)  # 정확한 상태 일치 검색

        # WHERE 조건이 하나라도 있다면 추가
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        # 정렬 기준 추가
        query += " ORDER BY id DESC"

        # 🛠️ 쿼리 실행
        cursor.execute(query, tuple(params))
        
        tasks = cursor.fetchall()
        return tasks
    except Exception as e:
        st.error(f"작업 목록을 가져오는 중 오류가 발생했습니다: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()


# 예약 상태인 작업 목록을 가져오는 함수
def get_reserve_task_list():
    try:
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute("SELECT id, drug_code, drug_name, drug_company, status FROM task_list WHERE status in ('PROCESSING','RESERVE') ORDER BY status, id ASC LIMIT 5")
        tasks = cursor.fetchall()
        return tasks
    except Exception as e:
        st.error(f"작업 목록을 가져오는 중 오류가 발생했습니다: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

# 수행 할 task 조회
def get_task():
    try:
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute("""select
                            id,
                            drug_code,
                            drug_name,
                            drug_company,
                            crawal_text,
                            parse_content::text,
                            drug_url,
                            status,
                            answer1,
                            answer2,
                            answer3,
                            answer4,
                            answer5,
                            answer6,
                            answer
                        from
                            task_list
                        where status = 'RESERVE'
                        order by id asc 
                        limit 1""")
        tasks = cursor.fetchall()
        return tasks
    except Exception as e:
        # st.error(f"작업 목록을 가져오는 중 오류가 발생했습니다: {e}")
        print(f"작업 목록을 가져오는 중 오류가 발생했습니다: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()


def get_complated_tasks():
    try:
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute("""select
                            id,
                            drug_code,
                            drug_name,
                            drug_company,
                            crawal_text,
                            parse_content::text,
                            drug_url,
                            status,
                            answer1,
                            answer2,
                            answer3,
                            answer4,
                            answer5,
                            answer6,
                            answer
                        from
                            task_list
                        where status = 'DONE'
                        order by id asc 
                        """)
        tasks = cursor.fetchall()
        return tasks
    except Exception as e:
        # st.error(f"작업 목록을 가져오는 중 오류가 발생했습니다: {e}")
        print(f"작업 목록을 가져오는 중 오류가 발생했습니다: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_task_by_id(task_id):
    """특정 task_id에 해당하는 작업 정보를 DB에서 조회"""
    try:
        conn = get_db_connection()
        if conn is None:
            st.error("데이터베이스 연결에 실패했습니다.")
            return None

        cursor = conn.cursor()
        cursor.execute("""
            SELECT id,
                    drug_code,
                    drug_name,
                    drug_company,
                    status,
                    crawal_text,
                    parse_content::text,
                    drug_url,
                    answer1,
                    answer2,
                    answer3,
                    answer4,
                    answer5,
                    answer6,
                    answer
            FROM task_list 
            WHERE id = %s
        """, (task_id,))
        task = cursor.fetchone()
        return task
    except Exception as e:
        st.error(f"작업 정보를 가져오는 중 오류가 발생했습니다: {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()



def delete_task(task_id):
    """작업 삭제 함수 (데이터베이스에서 해당 작업을 삭제)"""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        cursor.execute("DELETE FROM task_list WHERE id = %s", (task_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"작업을 삭제하는 중 오류가 발생했습니다: {e}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

# 상태정보 변경 - 예약
def reserv_task(task_id, drug_code):
    """E약은요 자료 생성 작업 예약"""
    conn = get_db_connection()
    if conn is None:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE task_list set status='RESERVE' WHERE id = %s",
                (task_id,)
            )
        conn.commit()
        st.success(f"✅ {drug_code}에 대한 작업에 예약되었습니다.")
    except Exception as e:
        st.error(f"데이터베이스에 변경하는 중 오류가 발생했습니다: {e}")
    finally:
        conn.close()

def update_task_status(task_id, status):
    """작업 상태 변경"""
    conn = get_db_connection()
    if conn is None:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE task_list set status=%s WHERE id = %s",
                (status, task_id,)
            )
        conn.commit()
        print(f"✅ {task_id}에 대한 작업이 변경({status})되었습니다.")
    except Exception as e:
        print(f"데이터베이스에 변경하는 중 오류가 발생했습니다: {e}")
    finally:
        conn.close()



# 답변 저장
def save_task_answer(task_id, drug_code, answer):
    """E약은요 자료 생성 작업 결과 저장"""
    conn = get_db_connection()
    if conn is None:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE task_list set answer=%s, status='DONE' WHERE id = %s",
                (answer, task_id,)
            )
        conn.commit()
        # st.success(f"✅ {drug_code}에 대한 작업이 처리되었습니다.")
        print(f"✅ {drug_code}에 대한 작업이 처리되었습니다.")
    except Exception as e:
        # st.error(f"데이터베이스에 변경하는 중 오류가 발생했습니다: {e}")
        print(f"데이터베이스에 변경하는 중 오류가 발생했습니다: {e}")
    finally:
        conn.close()