import streamlit as st
st.set_page_config(layout="wide")
from streamlit_folium import st_folium
import folium
import datetime

# 제목
st.title("민원 등록 시스템")

#지도1.5:입력창1
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

# 지도 생성
m = folium.Map(
    location=[37.5658, 126.9386],
    zoom_start=15,
    min_zoom=15,           # 사용자가 zoom 12보다 더 축소하지 못함
    max_zoom=18,           # (선택사항) 확대 가능한 최대 수준 설정
    max_bounds=True #연세대밖으로 못나가게
)

#왼쪽 배치
with left:
    st.write("🗺️ 지도를 클릭해서 민원을 시작하세요.")
    map_data = st_folium(m, height=400, width=700)

# 좌표 처리
clicked_coords = None
if map_data and map_data["last_clicked"]:
    clicked_coords = map_data["last_clicked"]
    st.success(f"📍 선택된 좌표: {clicked_coords}")

# 민원 정보 입력 & 오른쪽 배치
with right:
    st.subheader("✍️ 민원 작성")
    author = st.text_input("작성자 이름을 입력하세요:")
    content = st.text_area("민원 내용을 입력하세요:")
    date = st.date_input("작성 날짜를 선택하세요:", value=datetime.date.today())
    # 제출 처리
    if st.button("📨 민원 제출"):
        if not clicked_coords:
            st.error("지도를 클릭해서 위치를 선택해주세요.")
        elif not author or not content:
            st.error("작성자와 내용을 모두 입력해주세요.")
        else:
            complaint = Complaint(author, content, clicked_coords, date)
            st.subheader("📄 제출된 민원 정보")
            st.text(str(complaint))  # 문자열 변환 및 출력