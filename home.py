import streamlit as st
st.set_page_config(layout="wide")
from streamlit_folium import st_folium
import folium
import datetime
#구글 스프래드 시트 정보 저장
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#민원수 plot
import pandas as pd
import altair as alt


# 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("global-wharf-462313-r1-15cf2a330dba.json", scope)
client = gspread.authorize(creds)

# 구글 시트 열기 (제목으로)
spreadsheet = client.open("민원 정보")
worksheet = spreadsheet.sheet1

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
    
def complaint_to_list(complaint: Complaint):
    return [
        complaint.author,
        complaint.content,
        str(complaint.coords),
        str(complaint.date)
    ]
    
if "complaints" not in st.session_state:
    st.session_state.complaints = []
            
# 지도 생성
m = folium.Map(
    location=[37.5650, 126.9426],
    zoom_start=15,
    min_zoom=15,
    max_zoom=18,
    max_bounds=True
)

for complaint in st.session_state.complaints:
    coords = complaint.coords
    folium.CircleMarker(
        location=[coords['lat'], coords['lng']],
        radius=7,
        color='blue',
        fill=True,
        fill_color='cyan',
        popup=(f"작성자: {complaint.author}<br>"
               f"내용: {complaint.content}<br>"
               f"날짜: {complaint.date}")
    ).add_to(m)

with left:
    st.write("지도를 클릭해서 민원을 시작하세요.")
    map_data = st_folium(m, height=400, width=700)

# 좌표 처리
clicked_coords = None
if map_data and map_data.get("last_clicked"):
    clicked_coords = map_data["last_clicked"]
    st.write(f"선택된 좌표: 위도 {clicked_coords['lat']}, 경도 {clicked_coords['lng']}")
    st.session_state.clicked_coords = clicked_coords

# 그 아래에서
clicked_coords = st.session_state.get('clicked_coords', None)

with right:
    st.subheader("민원 작성")
    author = st.text_input("작성자 이름을 입력하세요:")
    content = st.text_area("민원 내용을 입력하세요:")
    date = st.date_input("작성 날짜를 선택하세요:", value=datetime.date.today())

# 제출 처리
    submit_enabled = bool(clicked_coords and author and content)

    if submit_enabled:
        if st.button("민원 제출"):
            complaint_instance = Complaint(author, content, clicked_coords, date)
            st.session_state.complaints.append(complaint_instance)
            complaint_list = complaint_to_list(complaint_instance)
            worksheet.append_row(complaint_list)
            st.success("민원이 등록되었습니다.")
    else:
        st.button("민원 제출", disabled=True)

#민원 조회
st.markdown("---")
search_author = st.text_input("작성자 이름을 입력하여 민원 조회")

if search_author:
    filtered = [c for c in st.session_state.complaints if c.author == search_author]
    if filtered:
        for c in filtered:
            st.markdown(f"""
                - **작성자**: {c.author}  
                - **내용**: {c.content}  
                - **좌표**: 위도 {c.coords['lat']}, 경도 {c.coords['lng']}  
                - **날짜**: {c.date}
            """)
    else:
        st.info("해당 작성자의 민원이 없습니다.")


# 날짜별 민원수 plot
st.markdown("---")
st.subheader("날짜별 민원 수")

if st.session_state.complaints:
    # 민원 날짜 추출
    dates = [c.date for c in st.session_state.complaints]
    
    # 데이터프레임 생성 및 날짜별 민원 수 집계
    df = pd.DataFrame({'date': dates})
    counts = df.groupby('date').size().reset_index(name='count')
    
    max_count = counts['count'].max()
    
    # Altair 바 차트 생성 (y축 0부터 시작)
    chart = (
        alt.Chart(counts)
        .mark_bar()
        .encode(
            x=alt.X('date:T', title='날짜'),
            y=alt.Y('count:Q', title='민원 수', scale=alt.Scale(domain=[0, max_count])),
            tooltip=['date', 'count']
        )
        .properties(width=700, height=300)
    )
    
    st.altair_chart(chart)
else:
    st.info("등록된 민원이 없습니다.")