import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import datetime
import re
import uuid

# ---------------------------------------------------------
# Page Configuration & Custom CSS Styling
# ---------------------------------------------------------
st.set_page_config(page_title="황금 채널 발굴기", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")

# API Key & Payment Session State Check
if "api_key" not in st.session_state:
    st.session_state["api_key"] = "AIzaSyD9NBQdPmHPmxKuuAC01d3r6ehdmxS1XBq"

if "is_premium" not in st.session_state:
    st.session_state["is_premium"] = False

# Custom CSS for Pill Buttons and UI
st.markdown("""
<style>
    /* 메인 배경색 */
    .stApp {
        background-color: #F8F9FA;
    }
    /* 카테고리 칩 버튼 스타일 */
    .stButton > button {
        border-radius: 20px !important;
        border: 1px solid #E0E0E0 !important;
        background-color: #FFFFFF !important;
        color: #333333 !important;
        font-weight: 600 !important;
        padding: 6px 16px !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        margin-bottom: 8px !important;
    }
    .stButton > button:hover {
        border-color: #4B6BFB !important;
        color: #4B6BFB !important;
        background-color: #F0F4FF !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# PAGE 1: 황금 채널 발굴기
# ---------------------------------------------------------
if menu == "📊 황금 채널 발굴기":
    st.markdown("### 📊 황금 채널 발굴기")
    
    if not st.session_state["is_premium"]:
        st.info("🔒 현재 무료 체험 중입니다. 모든 기능을 제한없이 쓰시려면 구독(결제)을 진행해 주세요!")

    # 1. 사진과 동일한 모든 카테고리 목록
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

    # 2. 영상 타입 선택 (쇼츠 / 롱폼)
    st.write("🎬 **영상 타입**")
    v_type = st.radio("영상 타입 선택", ["쇼츠", "롱폼"], horizontal=True, label_visibility="collapsed")

    # 3. 구독자 구간 선택
    st.write("👥 **구독자 구간**")
    sub_range = st.radio(
        "구독자 구간 선택", 
        ["전체", "0~1만 명 (급성장)", "1만~5만 명", "5만~10만 명"], 
        horizontal=True, 
        label_visibility="collapsed"
    )

    # 4. 정렬 기준
    st.write("📊 **정렬 기준**")
    sort_option = st.radio(
        "정렬 기준 선택", 
        ["조회수 높은 순", "구독자 많은 순"], 
        horizontal=True, 
        label_visibility="collapsed"
    )

    st.markdown("---")
    if st.button("🚀 조건에 맞는 황금 채널 탐색하기", use_container_width=True):
        if not st.session_state["is_premium"]:
            st.warning("⚠️ 무료 버전에서는 하루 검색 횟수가 제한됩니다. 무제한 이용을 위해 요금제 안내에서 구독을 진행해 주세요!")
        else:
            st.success(f"[{st.session_state['selected_category']}] 카테고리에서 조건에 맞는 채널을 검색 중입니다...")

# ---------------------------------------------------------
# PAGE: 요금제 안내 및 토스페이먼츠 결제 연동
# ---------------------------------------------------------
elif menu == "✨ 요금제 안내" or menu == "💳 구독 관리":
    st.title("💳 요금제 및 구독 관리")
    st.write("황금 채널 발굴기의 모든 기능을 무제한으로 이용하고 채널 분석 효율을 극대화하세요!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="border: 2px solid #E0E0E0; border-radius: 15px; padding: 25px; background: white;">
            <h3>🆓 무료 체험 플랜</h3>
            <p style="color: gray;">기본 기능 체험용</p>
            <h2>0원 / 월</h2>
            <hr>
            <p>✅ 기본 카테고리 탐색</p>
            <p>❌ 실시간 무제한 분석 제한</p>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state["is_premium"]:
            if st.button("무료 플랜으로 변경"):
                st.session_state["is_premium"] = False
                st.rerun()

    with col2:
        st.markdown("""
        <div style="border: 2px solid #4B6BFB; border-radius: 15px; padding: 25px; background: #F8FAFF;">
            <h3>🚀 프로 무제한 패스</h3>
            <p style="color: #4B6BFB; font-weight: bold;">전문가 추천 인기 플랜</p>
            <h2>29,000원 / 월</h2>
            <hr>
            <p>💜 실시간 무제한 분석</p>
            <p>🚀 터진 영상 실시간 추적</p>
            <p>🏆 채널 랭킹 무제한 열람</p>
            <p>✨ 베타 기능 즉시 제공</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state["is_premium"]:
            st.success("🎉 현재 프로 패스 이용 중입니다!")
        else:
            # 토스페이먼츠 연동 결제 버튼
            order_id = f"ORDER_{uuid.uuid4().hex[:8]}"
            toss_html = f"""
            <script src="https://js.tosspayments.com/v1/payment"></script>
            <button id="payment-button" style="background-color: #3182CE; color: white; padding: 12px 20px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; width: 100%;">
                💳 토스페이먼츠로 29,000원 결제하기
            </button>
            <script>
                var clientKey = "test_ck_D5GePWvyJnrK0W0k6q8gLzN97Eoq";
                var tossPayments = TossPayments(clientKey);
                
                document.getElementById("payment-button").onclick = function () {{
                    tossPayments.requestPayment('카드', {{
                        amount: 29000,
                        orderId: '{order_id}',
                        orderName: '황금 채널 발굴기 프로 패스 (1개월)',
                        customerName: 'Lee Cecilia',
                        successUrl: window.location.origin + '?payment=success',
                        failUrl: window.location.origin + '?payment=fail',
                    }});
                }};
            </script>
            """
            st.components.v1.html(toss_html, height=70)

    # 결제 성공 리다이렉트 처리
    query_params = st.query_params
    if "payment" in query_params:
        if query_params["payment"] == "success":
            st.session_state["is_premium"] = True
            st.success("🎉 결제가 성공적으로 완료되었습니다! 이제 모든 프리미엄 기능을 이용하실 수 있습니다.")
        elif query_params["payment"] == "fail":
            st.error("❌ 결제가 취소되었거나 실패했습니다. 다시 시도해 주세요.")

# ---------------------------------------------------------
# PAGE: API 키 설정
# ---------------------------------------------------------
elif menu == "🔑 YouTube API 키 설정":
    st.title("🔑 YouTube API 키 설정")
    key_input = st.text_input("Google Cloud API Key", value=st.session_state["api_key"], type="password")
    if st.button("저장하기"):
        st.session_state["api_key"] = key_input.strip()
        st.success("API 키가 성공적으로 저장되었습니다!")

else:
    st.title(f"🛠️ {menu}")
    st.write("해당 메뉴 페이지 준비 중입니다.")
