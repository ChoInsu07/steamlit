import streamlit as st
st.set_page_config(layout="wide")
from streamlit_folium import st_folium
import folium
import datetime

# 제목
st.title("민원 등록 시스템")

# 지도1.5:입력창1
left, right = st.columns([1.5, 1])

# 민원 클래스 정의
class Complaint:
    def __init__(self, author, content, coords, date):
        self.author = author
        self.content = content
        self.coords = coords
        self.date = date

    def __str__(self):
        return (f"민원자: {self.author}\n"
                f"민원 내용: {self.content}\n"
                f"좌표: {self.coords}\n"
                f"날짜: {self.date}")

def show_custom_modal(complaint: Complaint):
    modal_html = f"""
    <style>
    .modal-background {{
        position: fixed; 
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: rgba(0,0,0,0.5);
        display: flex; 
        justify-content: center; 
        align-items: center;
        z-index: 9999;
    }}
    .modal-content {{
        background-color: white; 
        padding: 20px; 
        border-radius: 10px; 
        width: 90%; max-width: 500px;
        white-space: pre-wrap;
        font-family: Arial, sans-serif;
    }}
    .modal-content h3 {{
        margin-top: 0;
    }}
    .info-item {{
        margin-bottom: 10px;
    }}
    </style>
    <div class="modal-background">
        <div class="modal-content">
            <h3>민원 제출 확인</h3>
            <div class="info-item"><strong>민원자:</strong> {complaint.author}</div>
            <div class="info-item"><strong>민원 내용:</strong> {complaint.content}</div>
            <div class="info-item"><strong>좌표:</strong> {complaint.coords}</div>
            <div class="info-item"><strong>날짜:</strong> {complaint.date}</div>
        </div>
    </div>
    """
    st.markdown(modal_html, unsafe_allow_html=True)


            
# 지도 생성
m = folium.Map(
    location=[37.5658, 126.9386],
    zoom_start=15,
    min_zoom=15,
    max_zoom=18,
    max_bounds=True
)

with left:
    st.write("지도를 클릭해서 민원을 시작하세요.")
    map_data = st_folium(m, height=400, width=700)

# 좌표 처리
clicked_coords = None
if map_data and map_data["last_clicked"]:
    clicked_coords = map_data["last_clicked"]
    st.success(f"선택된 좌표: {clicked_coords}")

with right:
    st.subheader("민원 작성")
    author = st.text_input("작성자 이름을 입력하세요:")
    content = st.text_area("민원 내용을 입력하세요:")
    date = st.date_input("작성 날짜를 선택하세요:", value=datetime.date.today())
#------------------------------여기까지 초기 화면
# 제출 처리
    submit_enabled = bool(clicked_coords and author and content)

    if submit_enabled:
        if st.button("민원 제출"):
            complaint_instance = Complaint(author, content, clicked_coords, date)
            show_custom_modal(complaint_instance)
    else:
        st.button("민원 제출", disabled=True)