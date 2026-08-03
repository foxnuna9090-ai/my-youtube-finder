import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import datetime

st.set_page_config(page_title="황금 채널 발굴기", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")

# ⬇️ 본인의 YouTube API 키를 큰따옴표 사이에 넣어주세요!
MY_API_KEY = "AIzaSyD9NBQdPmHPmxKuuAC01d3r6ehdmxS1XBo"

if "api_key" not in st.session_state:
    st.session_state["api_key"] = MY_API_KEY

# 🎨 스타일 적용
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #F8FAFC;
    }
    .stRadio label, .stSelectbox label, .stTextInput label {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
    }
    .stMarkdown p, .stMarkdown span {
        color: #F8FAFC;
    }
    .stButton > button {
        border-radius: 12px !important;
        border: 1px solid #4338CA !important;
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        padding: 10px 16px !important;
        width: 100% !important;
        margin-top: 10px !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        border-color: #818CF8 !important;
        background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%) !important;
    }
    .cat-badge {
        background: linear-gradient(135deg, #EC4899 0%, #8B5CF6 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.3);
    }
    .shorts-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    .metric-box {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("👑 Golden Finder")
menu = st.sidebar.radio(
    "메뉴",
    [
        "📊 황금 채널 발굴기",
        "🔍 조회수 폭발 쇼츠 찾기",
        "🔑 YouTube API 키 설정"
    ]
)

# 1️⃣ 황금 채널 발굴기 (롱폼 중심)
if menu == "📊 황금 채널 발굴기":
    st.markdown("### 📊 황금 채널 발굴기 (롱폼 탐색)")

    categories = [
        "전체", "연예인 명품", "건강/의학", "영화/드라마 리뷰", "연예인/이슈",
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

    st.markdown(f'<div class="cat-badge">🎯 현재 선택된 카테고리: {st.session_state["selected_category"]}</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("🚀 조건에 맞는 황금 채널 탐색하기", use_container_width=True):
        keyword = st.session_state["selected_category"]
        if keyword == "전체":
            keyword = "인기 채널"
            
        with st.spinner(f"[{keyword}] 카테고리에서 '구독자 20만 미만 & 최근 60일 이내 50만 이상' 롱폼 채널을 수집 중입니다..."):
            try:
                youtube = build("youtube", "v3", developerKey=st.session_state["api_key"])
                search_response = youtube.search().list(q=keyword, type="channel", part="snippet", maxResults=15).execute()

                items = search_response.get("items", [])
                filtered_channels = []

                for item in items:
                    if len(filtered_channels) >= 5:
                        break
                    channel_id = item["snippet"]["channelId"]
                    title = item["snippet"]["title"]
                    thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
                    
                    ch_detail = youtube.channels().list(part="statistics", id=channel_id).execute()
                    if not ch_detail.get("items"):
                        continue
                        
                    stats = ch_detail["items"][0]["statistics"]
                    sub_count = int(stats.get("subscriberCount", 0))

                    if sub_count >= 200000:
                        continue

                    video_response = youtube.search().list(channelId=channel_id, part="snippet", maxResults=3, order="viewCount", type="video").execute()

                    best_video = None
                    for v_item in video_response.get("items", []):
                        pub_time = v_item["snippet"]["publishedAt"]
                        pub_date = datetime.datetime.strptime(pub_time[:10], "%Y-%m-%d")
                        days_ago = (datetime.datetime.now() - pub_date).days

                        if days_ago <= 60:
                            video_id = v_item["id"]["videoId"]
                            v_stat = youtube.videos().list(part="statistics", id=video_id).execute()
                            if v_stat.get("items"):
                                v_views = int(v_stat["items"][0]["statistics"].get("viewCount", 0))
                                if v_views >= 500000:
                                    best_video = {
                                        "video_title": v_item["snippet"]["title"],
                                        "video_thumb": v_item["snippet"]["thumbnails"]["high"]["url"],
                                        "video_id": video_id,
                                        "views": v_views,
                                        "days_ago": days_ago
                                    }
                                    break

                    if best_video:
                        filtered_channels.append({
                            "title": title, "sub_count": sub_count, "best_video": best_video
                        })

                if not filtered_channels:
                    st.warning("조건에 일치하는 롱폼 채널을 찾지 못했습니다.")
                else:
                    st.success(f"🎉 황금 롱폼 채널 {len(filtered_channels)}개를 발굴했습니다!")
                    for ch in filtered_channels:
                        bv = ch["best_video"]
                        video_url = f"https://www.youtube.com/watch?v={bv['video_id']}"
                        st.markdown(f"""
                        <div class="shorts-card">
                            <a href="{video_url}" target="_blank" style="text-decoration: none; color: inherit;">
                                <div style="display: flex; gap: 15px; margin-bottom: 12px;">
                                    <img src="{bv['video_thumb']}" style="width: 140px; height: 90px; object-fit: cover; border-radius: 10px;">
                                    <div>
                                        <h4 style="margin: 0 0 6px 0; color: #FFFFFF; font-size: 16px;">🔥 {bv['video_title']}</h4>
                                        <p style="margin: 0; color: #818CF8; font-weight: bold;">👑 채널명: {ch['title']}</p>
                                    </div>
                                </div>
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"⚠️ 오류 발생: {e}")

# 2️⃣ 조회수 폭발 쇼츠 찾기 (이미지 요구사항 완벽 반영)
elif menu == "🔍 조회수 폭발 쇼츠 찾기":
    st.markdown("### 🔍 조회수 폭발 쇼츠 찾기")

    query = st.text_input("검색어를 입력하세요 (예: 요리, 연예인 명품, 재테크)", value="연예인 명품")
    
    col1, col2 = st.columns(2)
    with col1:
        upload_date_opt = st.selectbox("📅 업로드 일자", ["최근 1주일", "최근 1개월", "최근 3개월", "제한 없음"])
    with col2:
        max_sub_opt = st.selectbox("👥 최대 구독자", ["1만 명 미만", "5만 명 미만", "20만 명 미만", "제한 없음"], index=2)

    col3, col4 = st.columns(2)
    with col3:
        views_opt = st.selectbox("👀 조회수 범위", ["1만 ~ 5만회", "5만 ~ 10만회", "10만회 이상", "제한 없음"], index=2)
    with col4:
        sort_opt = st.selectbox("🔀 정렬", ["조회수 높은 순", "최신순"])

    if st.button("🚀 떡상 쇼츠 발굴 시작", use_container_width=True):
        with st.spinner(f"[{query}] 키워드로 떡상 쇼츠를 탐색 중입니다..."):
            try:
                youtube = build("youtube", "v3", developerKey=st.session_state["api_key"])
                
                # 날짜 계산
                published_after = None
                if upload_date_opt == "최근 1주일":
                    published_after = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).isoformat() + "Z"
                elif upload_date_opt == "최근 1개월":
                    published_after = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).isoformat() + "Z"
                elif upload_date_opt == "최근 3개월":
                    published_after = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).isoformat() + "Z"

                search_params = {
                    "q": f"{query} #shorts",
                    "type": "video",
                    "videoDuration": "short", # 쇼츠(4분 미만/실제 쇼츠 영역) 타겟
                    "part": "snippet",
                    "maxResults": 10
                }
                if published_after:
                    search_params["publishedAfter"] = published_after
                if sort_opt == "조회수 높은 순":
                    search_params["order"] = "viewCount"
                else:
                    search_params["order"] = "date"

                search_response = youtube.search().list(**search_params).execute()
                items = search_response.get("items", [])
                
                filtered_shorts = []
                for item in items:
                    video_id = item["id"]["videoId"]
                    channel_id = item["snippet"]["channelId"]
                    title = item["snippet"]["title"]
                    thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
                    channel_title = item["snippet"]["channelTitle"]

                    # 채널 구독자 확인
                    ch_detail = youtube.channels().list(part="statistics", id=channel_id).execute()
                    if not ch_detail.get("items"):
                        continue
                    sub_count = int(ch_detail["items"][0]["statistics"].get("subscriberCount", 0))

                    # 구독자 필터 적용
                    if max_sub_opt == "1만 명 미만" and sub_count >= 10000: continue
                    if max_sub_opt == "5만 명 미만" and sub_count >= 50000: continue
                    if max_sub_opt == "20만 명 미만" and sub_count >= 200000: continue

                    # 조회수 확인
                    v_stat = youtube.videos().list(part="statistics", id=video_id).execute()
                    if not v_stat.get("items"):
                        continue
                    v_views = int(v_stat["items"][0]["statistics"].get("viewCount", 0))

                    # 조회수 범위 필터 적용
                    if views_opt == "1만 ~ 5만회" and not (10000 <= v_views <= 50000): continue
                    elif views_opt == "5만 ~ 10만회" and not (50000 <= v_views <= 100000): continue
                    elif views_opt == "10만회 이상" and v_views < 100000: continue

                    filtered_shorts.append({
                        "video_id": video_id,
                        "title": title,
                        "thumbnail": thumbnail,
                        "channel_title": channel_title,
                        "sub_count": sub_count,
                        "views": v_views
                    })

                if not filtered_shorts:
                    st.warning("조건에 일치하는 쇼츠 영상을 찾지 못했습니다. 필터를 조금 넓혀보세요.")
                else:
                    st.success(f"🔥 조건에 맞는 폭발적인 쇼츠 {len(filtered_shorts)}개를 찾았습니다!")
                    for s in filtered_shorts:
                        shorts_url = f"https://www.youtube.com/shorts/{s['video_id']}"
                        st.markdown(f"""
                        <div class="shorts-card">
                            <a href="{shorts_url}" target="_blank" style="text-decoration: none; color: inherit;">
                                <div style="display: flex; gap: 15px; margin-bottom: 12px;">
                                    <img src="{s['thumbnail']}" style="width: 100px; height: 140px; object-fit: cover; border-radius: 10px;">
                                    <div>
                                        <h4 style="margin: 0 0 6px 0; color: #FFFFFF; font-size: 15px;">⚡ {s['title']}</h4>
                                        <p style="margin: 0 0 8px 0; color: #818CF8; font-weight: bold; font-size: 13px;">👑 채널: {s['channel_title']} (구독자 {s['sub_count']:,}명)</p>
                                        <p style="margin: 0; color: #34D399; font-weight: bold; font-size: 13px;">👀 조회수: {s['views']:,}회</p>
                                    </div>
                                </div>
                            </a>
                            <a href="{shorts_url}" target="_blank" style="display: block; text-align: center; background: linear-gradient(135deg, #EC4899 0%, #8B5CF6 100%); color: white; padding: 8px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 13px;">
                                ▶️ 쇼츠 영상 바로 시청하기
                            </a>
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"⚠️ 쇼츠 검색 중 오류 발생: {e}")

# 3️⃣ API 키 설정 메뉴
elif menu == "🔑 YouTube API 키 설정":
    st.title("🔑 YouTube API 키 설정")
    key_input = st.text_input("Google Cloud API Key", value=st.session_state["api_key"], type="password")
    if st.button("저장하기"):
        st.session_state["api_key"] = key_input.strip()
        st.success("API 키가 성공적으로 저장되었습니다!")
