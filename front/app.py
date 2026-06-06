import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://back:8000")

st.set_page_config(page_title="커피 원두 추천", page_icon="☕", layout="centered")

st.title("☕ 커피 원두 추천")
st.caption("취향을 입력하면 어울리는 원두 3종을 추천해드려요.")

with st.form("preference_form"):
    st.subheader("취향 입력")

    acidity = st.radio(
        "산미",
        ["낮음", "중간", "높음"],
        index=1,
        help="감귤·베리류처럼 새콤한 맛. 라이트 로스팅일수록 산미가 강해집니다.",
        horizontal=True,
    )

    body = st.radio(
        "바디감",
        ["가벼움", "중간", "묵직"],
        index=1,
        help="입안에서 느껴지는 묵직함과 질감. 우유로 비유하면 저지방/일반/생크림 같은 차이.",
        horizontal=True,
    )

    roast = st.radio(
        "로스팅 정도",
        ["라이트", "미디엄", "다크"],
        index=1,
        help="원두를 볶은 정도. 라이트는 신맛·꽃향, 다크는 쓴맛·고소함이 강해져요.",
        horizontal=True,
    )

    flavor = st.radio(
        "향 프로파일",
        ["과일·꽃", "견과·초콜릿", "흙·스파이스"],
        index=1,
        help="원두의 주된 풍미 계열입니다. 자신이 가장 끌리는 분위기를 골라주세요.",
        horizontal=True,
    )

    sweetness = st.slider(
        "단맛 선호도",
        min_value=1,
        max_value=5,
        value=3,
        help="설탕이 아닌 원두 자체의 단맛 선호도. 후처리·품종에 따라 자연스러운 단맛이 강한 원두가 있어요.",
    )

    caffeine = st.radio(
        "카페인 강도",
        ["낮음", "보통", "높음"],
        index=1,
        help="원두에 함유된 카페인 강도. 라이트 로스팅이 일반적으로 카페인이 높아요.",
        horizontal=True,
    )

    brew_method = st.selectbox(
        "주로 사용하는 추출 방식",
        ["에스프레소", "드립", "콜드브루", "모카포트", "프렌치프레스"],
        index=1,
        help="평소 가장 자주 내리는 추출 방식을 골라주세요.",
    )

    submitted = st.form_submit_button("☕ 원두 추천받기", use_container_width=True)

if submitted:
    payload = {
        "acidity": acidity,
        "body": body,
        "roast": roast,
        "flavor": flavor,
        "sweetness": sweetness,
        "caffeine": caffeine,
        "brew_method": brew_method,
    }

    with st.spinner("취향에 맞는 원두를 찾는 중..."):
        try:
            response = requests.post(f"{API_URL}/recommend", json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            st.error(f"FastAPI 서버 호출 실패: {e}")
            st.stop()

    st.success("취향 분석이 완료되었어요!")
    st.divider()
    st.subheader("추천 원두 TOP 3")

    rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}
    level_text = ["", "매우 낮음", "낮음", "중간", "높음", "매우 높음"]

    for bean in data["recommendations"]:
        with st.container(border=True):
            top_col, score_col = st.columns([3, 1])
            with top_col:
                st.markdown(f"### {rank_emoji[bean['rank']]} {bean['name']}")
                st.caption(f"📍 {bean['origin']}")
            with score_col:
                st.metric("매칭 점수", f"{bean['score']}점")

            st.markdown(f"_{bean['description']}_")
            st.markdown(f"**풍미 노트** : {' · '.join(bean['flavor_notes'])}")

            info_cols = st.columns(3)
            info_cols[0].markdown(f"**산미** &nbsp; {level_text[bean['acidity']]}")
            info_cols[1].markdown(f"**바디** &nbsp; {level_text[bean['body']]}")
            info_cols[2].markdown(f"**로스팅** &nbsp; {bean['roast']}")

            if bean["match_reasons"]:
                st.markdown("**매칭 이유**")
                for reason in bean["match_reasons"]:
                    st.markdown(f"- {reason}")

            st.info(f"☕ **추출 팁** &nbsp; {bean['brew_tip']}")

    st.divider()
    with st.expander("FastAPI 원본 응답 (JSON)"):
        st.json(data)
