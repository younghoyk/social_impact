"""공무원용 원클릭 승인 대시보드 (Step 4). backend/app/applications API를 호출."""
import os

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="실버브릿지 승인 대시보드", layout="wide")
st.title("실버브릿지 — 복지 신청 승인 대시보드")

response = requests.get(f"{API_BASE_URL}/applications/pending")
response.raise_for_status()
applications = response.json()

if not applications:
    st.info("승인 대기 중인 신청이 없습니다.")

for application in applications:
    with st.container(border=True):
        st.subheader(application["policy_title"])
        st.caption(f"어르신 ID: {application['elder_id']} · 통화 ID: {application['call_id']}")
        st.text_area("AI 작성 서류 초안", application["draft_content"], height=150, disabled=True)

        if st.button("승인", key=f"approve-{application['id']}"):
            approve_response = requests.post(f"{API_BASE_URL}/applications/{application['id']}/approve")
            approve_response.raise_for_status()
            st.success("승인 완료. 어르신께 자동으로 콜백이 발신됩니다.")
            st.rerun()
