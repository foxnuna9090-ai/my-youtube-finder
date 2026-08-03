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

# API Key Setting
if "api_key" not in st.session_state:
    st.session_state["api_key"] = "AIzaSyD9NBQdPmHPmxKuuAC01d3r6ehdmxS1XBq"

# Custom CSS for Pill Buttons and UI
st.markdown("""
<style>
    .stApp {
        background-color: #F8F9FA;
    }
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

    # 1. 카테고리 선택 태그
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
        st.success(f"[{st.session_state['selected_category']}] 카테고리에서 조건에 맞는 채널을 검색합니다!")

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
