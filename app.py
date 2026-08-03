import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import datetime

st.set_page_config(page_title="황금 채널 발굴기", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")

# ⬇️ 아래 따옴표 사이에 본인의 정확한 YouTube API 키를 넣어주세요!
MY_API_KEY = "AIzaSyD9NBQdPmHPmxKuuAC01d3r6ehdmxS1XBo"

if "api_key" not in st.session_state:
    st.session_state["api_key"] = MY_API_KEY

st.markdown("""
<style>
    .stApp {
        background-color: #12141C;
        color: #FFFFFF;
    }
    .stRadio label {
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }
    .stMarkdown p, .stMarkdown span {
        color: #FFFFFF;
    }
    .stButton > button {
        border-radius: 20px !important;
        border: 1px solid #2A2E3D !important;
        background-color: #1E2230 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        padding: 6px 16px !important;
        width: 100% !important;
        margin-bottom: 8px !important;
    }
    .stButton > button:hover {
        border-color: #4B6BFB !important;
        color: #4B6BFB !important;
    }
    .channel-card {
        background-color: #1A1D29;
        border: 1px solid #2A2E3D;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .channel-card a {
        text-decoration: none;
        color: inherit;
    }
    .channel-card a:hover h4 {
        color: #4B6BFB !important;
    }
    .metric-box {
        background-color: #12141C;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        border: 1px solid #2A2E3D;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("👑 Golden Finder")
menu = st.sidebar.radio(
    "메뉴",
    [
        "📊 황금 채널 발굴기",
        "🔍 조회수 폭발 쇼츠 찾기",
        "🔥 터진 영상",
        "📈 채널 랭킹",
        "⭐ 즐겨찾기",
        "🔑 YouTube API 키 설정",
        "💳 구독 관리",
        "✨ 요금제 안내"
    ]
)

if menu == "📊 황금 채널 발굴기":
    st.markdown("### 📊 황금 채널 발굴기")

    categories = [
        "전체", "건강/의학", "영화/드라마 리뷰", "연예인/이슈",
        "재테크/부동산", "동기부여/명언", "AI/IT 꿀팁", "라이프스타일/Vlog",
        "반려동물", "블랙박스/사건사고", "뷰티", "요리", "여행"
    ]
    
    if "selected_category" not in st.session_state:
        st.session_state["selected_category"] = "전체"

    st.write("📌 **카테고리 선택**")
    cols = st.columns(4)
    for idx, cat in enumerate(categories):
        with cols[idx % 4]:
            if st.button(cat, key=f"cat_{cat}"):
                st.session_state["selected_category"] = cat

    st.markdown(f"선택된 카테고리: **{st.session_state['selected_category']}**")
    st.markdown("---")

    v_type = st.radio("영상 타입 선택", ["쇼츠", "롱폼"], horizontal=True)
    sub_range = st.radio("구독자 구간 선택", ["전체", "0~1만 명 (급성장)", "1만~5만 명", "5만~10만 명"], horizontal=True)
    sort_option = st.radio("정렬 기준 선택", ["조회수 높은 순", "구독자 많은 순"], horizontal=True)

    st.markdown("---")
    
    if st.button("🚀 조건에 맞는 황금 채널 탐색하기", use_container_width=True):
        keyword = st.session_state["selected_category"]
        if keyword == "전체":
            keyword = "인기 채널"
            
        with st.spinner(f"[{keyword}] 관련 유튜브 채널을 분석하는 중입니다..."):
            try:
                youtube = build("youtube", "v3", developerKey=st.session_state["api_key"])
                
                search_response = youtube.search().list(
                    q=keyword,
                    type="channel",
                    part="snippet",
                    maxResults=5
                ).execute()

                items = search_response.get("items", [])
                if not items:
                    st.warning("검색 결과가 없습니다.")
                else:
                    st.success(f"🎉 총 {len(items)}개의 황금 채널을 발굴했습니다!")
                    
                    for item in items:
                        channel_id = item["snippet"]["channelId"]
                        title = item["snippet"]["title"]
                        thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
                        
                        ch_detail = youtube.channels().list(
                            part="statistics,snippet",
                            id=channel_id
                        ).execute()
                        
                        sub_count = 0
                        view_count = 0
                        if ch_detail.get("items"):
                            stats = ch_detail["items"][0]["statistics"]
                            sub_count = int(stats.get("subscriberCount", 0))
                            view_count = int(stats.get("viewCount", 0))

                        video_response = youtube.search().list(
                            channelId=channel_id,
                            part="snippet",
                            maxResults=1,
                            order="viewCount",
                            type="video"
                        ).execute()
                        
                        video_title = "대표 영상 정보 없음"
                        video_thumb = thumbnail
                        upload_date_str = "최근"
                        video_url = f"https://www.youtube.com/channel/{channel_id}"
                        
                        daily_views = view_count // 365 if view_count > 0 else 1200
                        ams_index = round(min(99.9, (daily_views / 10000) * 85), 1)

                        if video_response.get("items"):
                            v_item = video_response["items"][0]
                            video_title = v_item["snippet"]["title"]
                            video_thumb = v_item["snippet"]["thumbnails"]["high"]["url"]
                            video_id = v_item["id"]["videoId"]
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            
                            pub_time = v_item["snippet"]["publishedAt"]
                            pub_date = datetime.datetime.strptime(pub_time[:10], "%Y-%m-%d")
                            days_ago = (datetime.datetime.now() - pub_date).days
                            upload_date_str = f"{days_ago}일 전" if days_ago > 0 else "오늘"

                        st.markdown(f"""
                        <div class="channel-card">
                            <a href="{video_url}" target="_blank">
                                <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                                    <img src="{video_thumb}" style="width: 120px; height: 80px; object-fit: cover; border-radius: 8px;">
                                    <div>
                                        <h4 style="margin: 0 0 5px 0; color: white; font-size: 16px;">{video_title}</h4>
                                        <p style="margin: 0; color: #4B6BFB; font-weight: bold; font-size: 14px;">👑 {title}</p>
                                    </div>
                                </div>
                            </a>
                            <div style="display: flex; gap: 10px; margin-bottom: 12px;">
                                <div class="metric-box" style="flex:1;">
                                    <div style="color: #8A8F98; font-size: 12px;">구독자</div>
                                    <div style="color: white; font-weight: bold; font-size: 15px;">{sub_count:,}명</div>
                                </div>
                                <div class="metric-box" style="flex:1;">
                                    <div style="color: #8A8F98; font-size: 12px;">조회수</div>
                                    <div style="color: white; font-weight: bold; font-size: 15px;">{view_count:,}회</div>
                                </div>
                                <div class="metric-box" style="flex:1;">
                                    <div style="color: #8A8F98; font-size: 12px;">업로드</div>
                                    <div style="color: white; font-weight: bold; font-size: 15px;">{upload_date_str}</div>
                                </div>
                            </div>
                            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                                <div class="metric-box" style="flex:1;">
                                    <div style="color: #8A8F98; font-size: 12px;">일일 조회수</div>
                                    <div style="color: #4ADE80; font-weight: bold; font-size: 15px;">{daily_views:,}회/일</div>
                                </div>
                                <div class="metric-box" style="flex:1;">
                                    <div style="color: #8A8F98; font-size: 12px;">AMS 지수</div>
                                    <div style="color: #FACC15; font-weight: bold; font-size: 15px;">{ams_index}</div>
                                </div>
                            </div>
                            <a href="{video_url}" target="_blank" style="display: block; text-align: center; background-color: #FF0000; color: white; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                                ▶️ 해당 영상 바로 시청하기
                            </a>
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"⚠️ 검색 중 오류가 발생했습니다: {e}")

elif menu == "🔑 YouTube API 키 설정":
    st.title("🔑 YouTube API 키 설정")
    key_input = st.text_input("Google Cloud API Key", value=st.session_state["api_key"], type="password")
    if st.button("저장하기"):
        st.session_state["api_key"] = key_input.strip()
        st.success("API 키가 성공적으로 저장되었습니다!")

else:
    st.title(f"🛠️ {menu}")
    st.write("해당 메뉴 페이지 준비 중입니다.")
