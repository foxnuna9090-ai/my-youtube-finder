import streamlit as st
import streamlit.components.v1 as components
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime, timedelta, timezone
import re
import uuid

# ---------------------------------------------------------
# Page Configuration & Custom CSS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="유튜브 떡상 발굴기",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS matching exact reference UI
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #F8F9FA;
    }
    
    /* Header Card */
    .header-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
        text-align: center;
    }
    
    .header-title {
        font-size: 24px;
        font-weight: 800;
        color: #1A1A1A;
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }

    /* Form Container Card */
    div[data-testid="stForm"] {
        background: white;
        padding: 25px 20px;
        border-radius: 24px;
        border: none;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
    }
    
    /* Input & Select Box Styling */
    .stTextInput input, .stSelectbox select {
        border-radius: 14px !important;
        border: 1px solid #EAEAEA !important;
        padding: 12px 15px !important;
        background-color: #F9FAFB !important;
        font-size: 15px !important;
    }
    
    /* Gradient Button */
    div.stButton > button, div[data-testid="stForm"] button {
        width: 100%;
        background: linear-gradient(135deg, #8A2387 0%, #E94057 50%, #F27121 100%);
        color: white !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        padding: 14px 20px !important;
        border-radius: 16px !important;
        border: none !important;
        box-shadow: 0 8px 20px rgba(233, 64, 87, 0.3) !important;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    /* Pricing Cards Style */
    .pricing-card-free {
        background: #F0FDF4;
        border: 2px solid #86EFAC;
        border-radius: 24px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    .pricing-card-pro {
        background: #F5F3FF;
        border: 2px solid #A855F7;
        border-radius: 24px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
    }

    .badge-pop {
        background-color: #A855F7;
        color: white;
        font-size: 12px;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 10px;
    }

    .pricing-title {
        font-size: 20px;
        font-weight: bold;
        color: #1F2937;
        margin-bottom: 10px;
    }

    .pricing-price {
        font-size: 32px;
        font-weight: 900;
        color: #10B981;
        margin-bottom: 15px;
    }

    .pricing-price-pro {
        font-size: 32px;
        font-weight: 900;
        color: #6366F1;
        margin-bottom: 15px;
    }

    .benefit-box {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .benefit-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #F3F4F6;
    }

    /* Checkout Modal Top Banner */
    .checkout-header {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
        border-radius: 20px 20px 0 0;
        padding: 25px 20px;
        color: white;
        text-align: center;
        margin: -20px -20px 20px -20px;
    }
    
    .checkout-feature-item {
        display: flex;
        gap: 12px;
        margin-bottom: 15px;
        align-items: flex-start;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Navigation (메뉴 선택)
# ---------------------------------------------------------
st.sidebar.title("📌 메뉴")
menu = st.sidebar.radio(
    "이동할 기능을 선택하세요:",
    [
        "🔍 조회수 폭발 쇼츠 찾기",
        "📈 떡상 일반 영상 찾기",
        "👥 떡상 채널 탐색기",
        "💳 요금제 안내",
        "🔑 API 키 설정"
    ]
)

# API Key Session State Check
if "api_key" not in st.session_state:
    st.session_state["api_key"] = "AIzaSyD9NBQdPmHPmxKuuAC01d3r6ehdmxS1XBo"

# API Helper Functions
def get_youtube_client(api_key):
    return build("youtube", "v3", developerKey=api_key)

def format_number(num):
    if num >= 10000:
        return f"{num / 10000:.1f}만회"
    elif num >= 1000:
        return f"{num / 1000:.1f}천회"
    return f"{num}회"

def parse_iso8601_duration(duration_str):
    pattern = re.compile(r'PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?')
    match = pattern.match(duration_str)
    if not match:
        return 0
    parts = match.groupdict()
    hours = int(parts['hours'] or 0)
    minutes = int(parts['minutes'] or 0)
    seconds = int(parts['seconds'] or 0)
    return hours * 3600 + minutes * 60 + seconds


# ---------------------------------------------------------
# Toss Payments Checkout Dialog Modal (실제 결제창 연동)
# ---------------------------------------------------------
@st.dialog("💳 프리미엄 구독 결제")
def show_checkout_dialog():
    st.markdown("""
        <div class="checkout-header">
            <div style="background: rgba(255,255,255,0.2); width: fit-content; padding: 4px 12px; border-radius: 12px; margin: 0 auto 10px; font-size: 12px; font-weight: bold; color: #FDE047;">🚀 PREMIUM</div>
            <h2 style="margin: 0; font-size: 22px; font-weight: 800; color: white;">🚀 3일간의 무료 체험이<br>종료되었습니다.</h2>
            <p style="margin: 10px 0 4px; font-size: 16px; font-weight: bold; color: #E0E7FF;">15,000원 · 매월 자동결제</p>
            <p style="margin: 0; font-size: 12px; color: #A5B4FC;">언제든지 취소 · 7일 이내 전액 환불</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature checklist
    st.markdown("""
        <div class="checkout-feature-item">
            <span style="background: #818CF8; color: white; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold;">✓</span>
            <div>
                <strong style="font-size: 15px; color: #1F2937;">🔍 모든 쇼츠 검색 무제한</strong>
                <p style="margin: 2px 0 0; font-size: 12px; color: #6B7280;">키워드·날짜·구독자·조회수 필터 조건 없이 무제한 사용</p>
            </div>
        </div>
        
        <div class="checkout-feature-item">
            <span style="background: #818CF8; color: white; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold;">✓</span>
            <div>
                <strong style="font-size: 15px; color: #1F2937;">📊 100배 떡상 채널 실시간 분석</strong>
                <p style="margin: 2px 0 0; font-size: 12px; color: #6B7280;">수익 채널 데이터 실시간 업데이트 & 무제한 탐색</p>
            </div>
        </div>

        <div class="checkout-feature-item">
            <span style="background: #818CF8; color: white; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold;">✓</span>
            <div>
                <strong style="font-size: 15px; color: #1F2937;">⚡ 신규 기능 우선 제공</strong>
                <p style="margin: 2px 0 0; font-size: 12px; color: #6B7280;">베타 기능 즉시 이용 & 전용 지원</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Agreement Checkbox
    agree = st.checkbox("【필수】 만 14세 이상이며, 15,000원 자동결제와 이용약관 · 환불정책 · 개인정보 수집·이용에 동의합니다.")
    
    # Toss Payments Parameters (테스트 환경 기준)
    TOSS_CLIENT_KEY = "test_ck_D5GePWvyJnrK0W0k6q8gLzN97Eoq"  # 토스페이먼츠 테스트용 키
    order_id = f"ORDER_{uuid.uuid4().hex[:10]}"
    amount = 15000
    order_name = "월간 프리미엄 구독"

    if agree:
        # Toss Payments SDK HTML/JS Embed
        toss_payment_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://js.tosspayments.com/v1/payment"></script>
        </head>
        <body style="margin:0; padding:0;">
            <button id="pay-button" style="
                width: 100%;
                background: #3182F6;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 14px 20px;
                border-radius: 12px;
                border: none;
                cursor: pointer;
                margin-top: 10px;">
                💳 카드 등록하고 시작하기
            </button>

            <script>
                var tossPayments = TossPayments('{TOSS_CLIENT_KEY}');
                document.getElementById('pay-button').addEventListener('click', function () {{
                    tossPayments.requestPayment('카드', {{
                        amount: {amount},
                        orderId: '{order_id}',
                        orderName: '{order_name}',
                        successUrl: window.location.href + '?pay=success',
                        failUrl: window.location.href + '?pay=fail'
                    }}).catch(function (error) {{
                        if (error.code !== 'USER_CANCEL') {{
                            alert('결제 창 오류: ' + error.message);
                        }}
                    }});
                }});
            </script>
        </body>
        </html>
        """
        components.html(toss_payment_html, height=70)
    else:
        st.info("💡 이용 약관 및 동의 체크박스에 동의하셔야 결제 버튼이 활성화됩니다.")

    st.caption("💳 신용·체크카드 등록 후 매월 자동결제 (토스페이먼츠)")


# ---------------------------------------------------------
# PAGE 1: 🔍 조회수 폭발 쇼츠 찾기
# ---------------------------------------------------------
if menu == "🔍 조회수 폭발 쇼츠 찾기":
    st.markdown("""
        <div class="header-card">
            <h1 class="header-title">🔍 조회수 폭발 쇼츠 찾기</h1>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state["api_key"]:
        st.warning("⚠️ 먼저 사이드바의 **'🔑 API 키 설정'** 메뉴에서 YouTube API Key를 입력해주세요.")
        st.stop()
        
    with st.form("shorts_form"):
        keyword = st.text_input("🔍 검색어를 입력하세요", placeholder="예: 요리, 주식, 운동, 리액션")
        upload_date_opt = st.selectbox("📅 업로드 일자", ["최근 1주일", "최근 24시간", "최근 1개월", "최근 1년", "전체"])
        max_subscribers_opt = st.selectbox("👥 최대 구독자", ["제한 없음", "1만명 이하", "5만명 이하", "10만명 이하", "50만명 이하", "100만명 이하"])
        view_count_opt = st.selectbox("👀 조회수 범위", ["1만 ~ 5만회", "전체", "1천 ~ 1만회", "5만 ~ 10만회", "10만회 이상", "100만회 이상"])
        sort_opt = st.selectbox("🔀 정렬", ["조회수 높은순", "최신순", "구독자 대비 조회수높은순 (떡상)"])
        
        submit_button = st.form_submit_button("🚀 떡상 쇼츠 발굴 시작")

    if submit_button:
        if not keyword.strip():
            st.error("검색어를 입력해 주세요!")
        else:
            with st.spinner("🚀 폭발적인 조회수의 쇼츠를 수집하는 중..."):
                try:
                    youtube = get_youtube_client(st.session_state["api_key"])
                    
                    now = datetime.now(timezone.utc)
                    published_after = None
                    if upload_date_opt == "최근 24시간":
                        published_after = (now - timedelta(days=1)).isoformat()
                    elif upload_date_opt == "최근 1주일":
                        published_after = (now - timedelta(weeks=1)).isoformat()
                    elif upload_date_opt == "최근 1개월":
                        published_after = (now - timedelta(days=30)).isoformat()
                    elif upload_date_opt == "최근 1년":
                        published_after = (now - timedelta(days=365)).isoformat()

                    search_kwargs = {
                        "q": f"{keyword} #shorts",
                        "part": "snippet",
                        "maxResults": 30,
                        "type": "video",
                        "videoDuration": "short"
                    }
                    if published_after:
                        search_kwargs["publishedAfter"] = published_after
                        
                    search_res = youtube.search().list(**search_kwargs).execute()
                    video_ids = [item["id"]["videoId"] for item in search_res.get("items", [])]
                    
                    if not video_ids:
                        st.info("검색 조건에 일치하는 쇼츠 영상이 없습니다.")
                    else:
                        video_res = youtube.videos().list(
                            part="snippet,statistics,contentDetails",
                            id=",".join(video_ids)
                        ).execute()
                        
                        channel_ids = list(set([item["snippet"]["channelId"] for item in video_res.get("items", [])]))
                        
                        channel_sub_map = {}
                        if channel_ids:
                            chan_res = youtube.channels().list(
                                part="statistics",
                                id=",".join(channel_ids)
                            ).execute()
                            for c in chan_res.get("items", []):
                                sub_cnt = int(c["statistics"].get("subscriberCount", 0))
                                channel_sub_map[c["id"]] = sub_cnt

                        results = []
                        for item in video_res.get("items", []):
                            duration_sec = parse_iso8601_duration(item["contentDetails"]["duration"])
                            if duration_sec > 60:
                                continue
                                
                            views = int(item["statistics"].get("viewCount", 0))
                            channel_id = item["snippet"]["channelId"]
                            subs = channel_sub_map.get(channel_id, 0)
                            
                            if max_subscribers_opt == "1만명 이하" and subs > 10000: continue
                            elif max_subscribers_opt == "5만명 이하" and subs > 50000: continue
                            elif max_subscribers_opt == "10만명 이하" and subs > 100000: continue
                            elif max_subscribers_opt == "50만명 이하" and subs > 500000: continue
                            elif max_subscribers_opt == "100만명 이하" and subs > 1000000: continue
                            
                            if view_count_opt == "1천 ~ 1만회" and not (1000 <= views < 10000): continue
                            elif view_count_opt == "1만 ~ 5만회" and not (10000 <= views < 50000): continue
                            elif view_count_opt == "5만 ~ 10만회" and not (50000 <= views < 100000): continue
                            elif view_count_opt == "10만회 이상" and views < 100000: continue
                            elif view_count_opt == "100만회 이상" and views < 1000000: continue

                            ratio = (views / subs) if subs > 0 else views

                            results.append({
                                "title": item["snippet"]["title"],
                                "channel": item["snippet"]["channelTitle"],
                                "views": views,
                                "subs": subs,
                                "ratio": ratio,
                                "url": f"https://www.youtube.com/shorts/{item['id']}",
                                "thumb": item["snippet"]["thumbnails"]["medium"]["url"],
                                "published": item["snippet"]["publishedAt"][:10]
                            })
                        
                        if sort_opt == "조회수 높은순":
                            results.sort(key=lambda x: x["views"], reverse=True)
                        elif sort_opt == "최신순":
                            results.sort(key=lambda x: x["published"], reverse=True)
                        elif sort_opt == "구독자 대비 조회수높은순 (떡상)":
                            results.sort(key=lambda x: x["ratio"], reverse=True)

                        st.subheader(f"🎉 총 {len(results)}개의 쇼츠를 찾았습니다!")
                        
                        for r in results:
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.image(r["thumb"], use_container_width=True)
                            with col2:
                                st.markdown(f"### [{r['title']}]({r['url']})")
                                st.write(f"📺 **채널명:** {r['channel']}")
                                st.write(f"👀 **조회수:** {format_number(r['views'])} | 👥 **구독자:** {format_number(r['subs'])}")
                                st.write(f"📅 **업로드일:** {r['published']}")
                                if r["subs"] > 0 and r["ratio"] >= 3.0:
                                    st.markdown(f"🔥 **구독자 대비 조회수:** `{r['ratio']:.1f}배` (떡상 쇼츠!)")
                            st.divider()

                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")


# ---------------------------------------------------------
# PAGE 2: 📈 떡상 일반 영상 찾기
# ---------------------------------------------------------
elif menu == "📈 떡상 일반 영상 찾기":
    st.title("📈 떡상 일반 영상 찾기")
    st.info("긴 영상 중 구독자 대비 조회수가 폭발한 영상을 발굴합니다.")


# ---------------------------------------------------------
# PAGE 3: 👥 떡상 채널 탐색기
# ---------------------------------------------------------
elif menu == "👥 떡상 채널 탐색기":
    st.title("👥 떡상 채널 탐색기")
    st.info("최근 급성장 중인 유튜버 채널을 찾습니다.")


# ---------------------------------------------------------
# PAGE 4: 💳 요금제 안내
# ---------------------------------------------------------
elif menu == "💳 요금제 안내":
    # Check url query parameter for payment status
    if st.query_params.get("pay") == "success":
        st.success("🎉 결제가 정상적으로 완료되었습니다! 모든 프리미엄 기능 권한이 등록되었습니다.")

    st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="font-weight: 800; color: #111827;">✨ 요금제 안내</h1>
            <p style="color: #6B7280; font-size: 16px;">3일 무료 체험 후, 프리미엄으로 모든 기능을 무제한 이용하세요.</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. Free Trial Card
    st.markdown("""
        <div class="pricing-card-free">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 24px;">🎁</span>
                <span class="pricing-title" style="margin: 0;">3일 무료 체험</span>
            </div>
            <div class="pricing-price" style="margin-top: 10px;">₩0</div>
            <p style="color: #6B7280; font-size: 14px; margin-bottom: 15px;">카드 등록 없이 가입 즉시 시작</p>
            <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 15px 0;">
            <p style="color: #374151; font-size: 14px; line-height: 1.5;">
                가입 후 <b>3일간 모든 기능 무제한</b> 체험. 종료 전 월간 프리미엄으로 이어가세요.
            </p>
            <div style="background: white; border: 1px solid #10B981; color: #10B981; text-align: center; padding: 12px; border-radius: 12px; font-weight: bold; margin-top: 15px;">
                ✓ 현재 이용 중
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Monthly Premium Card (15,000 KRW)
    st.markdown("""
        <div class="pricing-card-pro">
            <div class="badge-pop">👑 가장 인기</div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 24px;">👑</span>
                <span class="pricing-title" style="margin: 0;">월간 프리미엄</span>
            </div>
            <div class="pricing-price-pro" style="margin-top: 10px;">₩15,000 <span style="font-size: 16px; color: #6B7280; font-weight: normal;">/ 월</span></div>
            <p style="color: #6B7280; font-size: 14px; margin-bottom: 15px;">매월 자동결제 · 언제든 해지</p>
            <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 15px 0;">
            <p style="color: #374151; font-size: 14px; line-height: 1.5; margin-bottom: 20px;">
                황금 채널 발굴기 · 쇼츠 검색 · 터진 영상 · 채널 랭킹 등 <b>모든 기능 무제한</b>
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Open payment dialog modal
    if st.button("이 플랜으로 시작하기 ➔"):
        show_checkout_dialog()

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Benefits Summary
    st.markdown("""
        <div class="benefit-box">
            <h3 style="font-size: 18px; font-weight: bold; color: #111827; margin-bottom: 15px;">👑 모든 프리미엄 플랜 공통 혜택</h3>
            <div class="benefit-item">
                <span>💜 <b>조회수 폭발 쇼츠 검색</b></span>
                <span style="color: #6366F1; font-weight: bold;">무제한 (필터 자유)</span>
            </div>
            <div class="benefit-item">
                <span>💜 <b>황금 채널 발굴기</b></span>
                <span style="color: #6366F1; font-weight: bold;">실시간 무제한 분석</span>
            </div>
            <div class="benefit-item">
                <span>💜 <b>터진 영상 실시간 추적</b></span>
                <span style="color: #6366F1; font-weight: bold;">실시간 무제한</span>
            </div>
            <div class="benefit-item">
                <span>💜 <b>채널 랭킹</b></span>
                <span style="color: #6366F1; font-weight: bold;">무제한</span>
            </div>
            <div class="benefit-item">
                <span>💜 <b>신규 기능 우선 제공</b></span>
                <span style="color: #6366F1; font-weight: bold;">베타 기능 즉시 제공</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# PAGE 5: 🔑 API 키 설정
# ---------------------------------------------------------
elif menu == "🔑 API 키 설정":
    st.title("🔑 YouTube API Key 설정")
    st.write("YouTube Data API v3 발급 키를 입력하고 저장해 주세요.")
    
    key_input = st.text_input(
        "Google Cloud API Key",
        value=st.session_state["api_key"],
        type="password"
    )
    
    if st.button("저장하기"):
        st.session_state["api_key"] = key_input.strip()
        st.success("✅ API 키가 성공적으로 저장되었습니다!")
