import streamlit as st
import pandas as pd
from googleapiclient.discovery import build

# =========================================================
# 🔑 API 키 설정
# =========================================================
API_KEY = "AIzaSyD9NBQdPmHPmxKuuAC01d3r6ehdmxS1XBo"

# 페이지 기본 설정
st.set_page_config(page_title="황금 채널 & 영상 발굴기", page_icon="🎬", layout="wide")

st.title("🎬 황금 채널 & 영상 발굴기")
st.markdown("원하시는 조건들을 선택하신 후 **[🔍 조건으로 검색하기]** 버튼을 눌러주세요!")

st.divider()

# 1. 카테고리 선택
st.subheader("📂 카테고리")
CATEGORIES = [
    "전체", "건강/의학", "영화/드라마 리뷰", "연예인/이슈",
    "재테크/부동산", "동기부여/명언", "AI/IT 꿀팁", "라이프스타일/Vlog",
    "반려동물", "블랙박스/사건사고", "뷰티", "요리", "여행"
]
selected_category = st.radio("카테고리 선택", CATEGORIES, horizontal=True, label_visibility="collapsed")

st.divider()

# 2. 영상 타입 / 구독자 구간 / 정렬 기준 선택
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🎬 영상 타입")
    selected_type = st.radio("영상 타입 선택", ["쇼츠", "롱폼"], horizontal=True, label_visibility="collapsed")

with col2:
    st.subheader("👥 구독자 구간")
    sub_options = ["전체", "0~1만 명 (급성장)", "1만~5만 명", "5만~10만 명"]
    selected_sub_range = st.radio("구독자 구간 선택", sub_options, horizontal=True, label_visibility="collapsed")

with col3:
    st.subheader("📊 정렬 기준")
    order_options = ["조회수 높은 순", "구독자 많은 순"]
    selected_order = st.radio("정렬 기준 선택", order_options, horizontal=True, label_visibility="collapsed")

st.divider()

# 유튜브 검색 처리 함수
def search_youtube(cat, v_type, sub_range, order_type, key):
    if not key or "AIzaSy" not in key:
        st.error("❌ API 키가 올바르지 않습니다.")
        return

    query = "" if cat == "전체" else cat.replace("/", " ")
    duration_param = 'short' if v_type == "쇼츠" else 'medium'

    try:
        youtube = build('youtube', 'v3', developerKey=key)
        
        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            videoDuration=duration_param,
            order='viewCount',
            maxResults=50
        )
        response = request.execute()

        video_items = response.get('items', [])
        if not video_items:
            st.warning("검색 결과가 없습니다.")
            return

        video_ids = [item['id']['videoId'] for item in video_items]
        channel_ids = list(set([item['snippet']['channelId'] for item in video_items]))

        stats_request = youtube.videos().list(
            part='statistics,snippet',
            id=','.join(video_ids)
        )
        stats_response = stats_request.execute()

        channel_request = youtube.channels().list(
            part='statistics',
            id=','.join(channel_ids)
        )
        channel_response = channel_request.execute()
        
        channel_subs = {}
        for ch in channel_response.get('items', []):
            ch_id = ch['id']
            sub_cnt = int(ch['statistics'].get('subscriberCount', 0)) if not ch['statistics'].get('hiddenSubscriberCount', False) else 0
            channel_subs[ch_id] = sub_cnt

        data = []
        for item in stats_response.get('items', []):
            title = item['snippet']['title']
            channel = item['snippet']['channelTitle']
            ch_id = item['snippet']['channelId']
            views = int(item['statistics'].get('viewCount', 0))
            subscribers = channel_subs.get(ch_id, 0)
            video_id = item['id']
            url = f"https://www.youtube.com/watch?v={video_id}"

            if sub_range == "0~1만 명 (급성장)" and not (0 <= subscribers <= 10000):
                continue
            elif sub_range == "1만~5만 명" and not (10000 < subscribers <= 50000):
                continue
            elif sub_range == "5만~10만 명" and not (50000 < subscribers <= 100000):
                continue

            data.append({
                "제목": title,
                "채널명": channel,
                "조회수": views,
                "구독자 수": subscribers,
                "링크": url
            })

        if not data:
            st.warning("선택하신 조건에 해당하는 결과가 없습니다. 다른 구간을 선택해 보세요!")
            return

        df = pd.DataFrame(data)

        if order_type == "구독자 많은 순":
            df = df.sort_values(by="구독자 수", ascending=False)
        else:
            df = df.sort_values(by="조회수", ascending=False)

        df["조회수"] = df["조회수"].apply(lambda x: f"{x:,}회")
        df["구독자 수"] = df["구독자 수"].apply(lambda x: f"{x:,}명" if x > 0 else "비공개")

        st.success(f"✅ 검색 결과 ({len(df)}개 발굴 완료)")
        
        st.dataframe(
            df,
            column_config={
                "링크": st.column_config.LinkColumn("영상 링크", display_text="🎬 영상 보기")
            },
            hide_index=True,
            use_container_width=True
        )

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")

# 검색 실행 버튼
if st.button("🔍 조건으로 검색하기", type="primary", use_container_width=True):
    search_youtube(selected_category, selected_type, selected_sub_range, selected_order, API_KEY)
