

# 스트림렛 실행
streamlit run app.py



# 백그라운드 수행
nohup python task_manager.py &

# 상태확인
ps aux | grep task_manager.py

# 중지
kill <pid>


# 화면에서 sub process로 실행 시킨 다음 종료 시키는 방법 활용
command 프로그램으로 실행 시키는 방법


우선 별도 프로그램으로 만들자