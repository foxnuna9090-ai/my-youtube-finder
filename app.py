import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import datetime

st.set_page_config(page_title="황금 채널 발굴기", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")

# ⬇️ 본인의 YouTube API 키를 큰따옴표 사이에 넣어주세요!
MY_API_KEY = "AIzaSyD9NBQdPmHPmxKuuAC01d3r6ehdmxS1XBo"

if "api_key" not in st.session_state:
    st.session_state["api_key"] = MY_API_KEY

# 🎨 가독성과 시각적 완성도를 높인 프리미엄 스타일 적용
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #F8FAFC;
    }
    .stRadio label {
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
        padding: 8px 16px !important;
        width: 100% !important;
        margin-bottom: 6px !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        border-color: #818CF8 !important;
        background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%) !important;
        box-shadow: 0 6px 16px rgba(129, 140, 248, 0.4);
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
    .channel-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease;
    }
    .channel-card:hover {
        border-color: #6366F1;
        transform: translateY(-2px);
    }
    .channel-card a {
        text-decoration: none;
        color: inherit;
    }
    .metric-box {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 12px;
        padding: 12px;
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
        "🔥 터진 영상",
        "📈 채널 랭킹",
        "⭐ 즐겨찾기",
        "🔑 YouTube API 키 설정",
        "💳 구독 관리",
        "✨ 요금제 안내"
    ]
)

if menu == "📊 황금 채널 발굴기":
    st.markdown("### 📊 황금 채널 발굴기 (떡상 채널 탐색 시스템)")

    # 📌 '연예인 명품' 카테고리 추가 완료
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

    # 📌 선택된 카테고리를 눈에 띄는 컬러 배지로 시각화
    st.markdown(f'<div class="cat-badge">🎯 현재 선택된 카테고리: {st.session_state["selected_category"]}</div>', unsafe_allow_html=True)
    st.markdown("---")

    v_type = st.radio("영상 타입 선택", ["쇼츠", "롱폼"], horizontal=True)
    sub_range = st.radio("구독자 구간 선택", ["전체", "0~20만 명 (급성장/떡상 타겟)", "20만~50만 명", "50만 명 이상"], horizontal=True)
    sort_option = st.radio("정렬 기준 선택", ["조회수 높은 순", "구독자 많은 순"], horizontal=True)

    st.markdown("---")
    
    if st.button("🚀 조건에 맞는 황금 채널 탐색하기", use_container_width=True):
        keyword = st.session_state["selected_category"]
        if keyword == "전체":
            keyword = "인기 채널"
            
        with st.spinner(f"[{keyword}] 카테고리에서 떡상 조건을 만족하는 채널을 수집 중입니다..."):
            try:
                youtube = build("youtube", "v3", developerKey=st.session_state["api_key"])
                
                search_response = youtube.search().list(
                    q=keyword,
                    type="channel",
                    part="snippet",
                    maxResults=10
                ).execute()

                items = search_response.get("items", [])
                filtered_channels = []

                # 📌 요구하신 필터 로직 적용 (구독자 20만 미만 + 최근 60일 이내 떡상 영상 우선 수집)
                thresholds = [1000000, 500000, 300000, 100000, 50000] # 100만 -> 50만 -> 30만 -> 10만 -> 5만 순으로 보충

                for target_view_limit in thresholds:
                    if len(filtered_channels) >= 5: # 최대 5개 채널 확보 시 종료
                        break
                        
                    for item in items:
                        channel_id = item["snippet"]["channelId"]
                        title = item["snippet"]["title"]
                        thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
                        
                        # 이미 담긴 채널이면 패스
                        if any(ch['channel_id'] == channel_id for ch in filtered_channels):
                            continue

                        # 채널 상세 정보 (구독자 수 확인)
                        ch_detail = youtube.channels().list(
                            part="statistics,snippet",
                            id=channel_id
                        ).execute()
                        
                        if not ch_detail.get("items"):
                            continue
                            
                        stats = ch_detail["items"][0]["statistics"]
                        sub_count = int(stats.get("subscriberCount", 0))
                        view_count = int(stats.get("viewCount", 0))

                        # 구독자 20만 미만 필터 적용 (옵션이 전체가 아닐 경우 반영)
                        if sub_count >= 200000 and sub_range == "0~20만 명 (급성장/떡상 타겟)":
                            continue

                        # 최근 60일 이내 떡상 영상 탐색
                        video_response = youtube.search().list(
                            channelId=channel_id,
                            part="snippet",
                            maxResults=3,
                            order="viewCount",
                            type="video"
                        ).execute()

                        best_video = None
                        for v_item in video_response.get("items", []):
                            pub_time = v_item["snippet"]["publishedAt"]
                            pub_date = datetime.datetime.strptime(pub_time[:10], "%Y-%m-%d")
                            days_ago = (datetime.datetime.now() - pub_date).days

                            if days_ago <= 60: # 최근 60일 이내
                                video_id = v_item["id"]["videoId"]
                                # 영상 상세 조회수 확인
                                v_stat = youtube.videos().list(
                                    part="statistics",
                                    id=video_id
                                ).execute()
                                
                                if v_stat.get("items"):
                                    v_views = int(v_stat["items"][0]["statistics"].get("viewCount", 0))
                                    if v_views >= target_view_limit:
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
                                "channel_id": channel_id,
                                "title": title,
                                "thumbnail": thumbnail,
                                "sub_count": sub_count,
                                "view_count": view_count,
                                "best_video": best_video
                            })

                if not filtered_channels:
                    st.warning("조건에 정확히 일치하는 채널을 찾지 못했습니다. 기준을 완화하여 다시 시도해 보세요.")
                else:
                    st.success(f"🎉 떡상 조건에 부합하는 황금 채널 {len(filtered_channels)}개를 발굴했습니다!")
                    
                    for ch in filtered_channels:
                        bv = ch["best_video"]
                        video_url = f"https://www.youtube.com/watch?v={bv['video_id']}"
                        daily_views = ch["view_count"] // 365 if ch["view_count"] > 0 else 1200
                        ams_index = round(min(99.9, (bv["views"] / 10000) * 9.5), 1)

                        st.markdown(f"""
                        <div class="channel-card">
                            <a href="{video_url}" target="_blank">
                                <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                                    <img src="{bv['video_thumb']}" style="width: 140px; height: 90px; object-fit: cover; border-radius: 10px;">
                                    <div>
                                        <h4 style="margin: 0 0 6px 0; color: #FFFFFF; font-size: 16px;">🔥 {bv['video_title']}</h4>
                                        <p style="margin: 0; color: #818CF8; font-weight: bold; font-size: 14px;">👑 채널명: {ch['title']}</p>
                                    </div>
                                </div>
                            </a>
                            <div style="display: flex; gap: 10px; margin-bottom: 12px;">
                                <div class="metric-box" style="flex:1;">
                                    <div style="color: #94A3B8; font-size: 12px;">구독자 수</div>
                                    <div style="color: #F8FAFC; font-weight: bold; font-size: 15px;">{ch['sub_count']:,}명</div>
                                </div>
                                <div class="metric-box" style="flex:1;">
                                    <div style="color: #94A3B8; font-size: 12px;">급상승 영상 조회수</div>
                                    <div style="color: #34D399; font-weight: bold; font-size: 15px;">{bv['views']:,}회 ({bv['days_ago']}일 전)</div>
                                </div>
                                <div class="metric-box" style="flex:1;">
                                    <div style="color: #94A3B8; font-size: 12px;">AMS 떡상 지수</div>
                                    <div style="color: #FBBF24; font-weight: bold; font-size: 15px;">⭐ {ams_index}</div>
                                </div>
                            </div>
                            <a href="{video_url}" target="_blank" style="display: block; text-align: center; background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); color: white; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);">
                                ▶️ 떡상 영상 바로 시청하기
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
