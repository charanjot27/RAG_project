"""Streamlit UI. Run: streamlit run app/app.py (with the API running)."""

from __future__ import annotations

import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="VeriFin", page_icon="✅")
st.title("VeriFin — Verified Financial Answers")
st.caption("Green = backed by a source · Red = unverified, do not trust")

question = st.text_input("Ask a question:")

if st.button("Ask") and question:
    with st.spinner("Retrieving, answering, and fact-checking..."):
        try:
            res = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=120)
            res.raise_for_status()
            data = res.json()
        except requests.RequestException as exc:
            st.error(f"Could not reach the API at {API_URL}: {exc}")
            st.stop()

    st.metric("Faithfulness score", f"{data['faithfulness_score'] * 100:.0f}%")

    for s in data["sentences"]:
        if s["status"] == "grounded":
            citation = s["citation"] or ""
            if citation.startswith("http"):
                url = citation.split(" ")[0]
                citation = f"<a href='{url}' target='_blank'>{citation}</a>"
            st.markdown(
                f":green[{s['text']}]  \n"
                f"<small>Source: {citation} (confidence {s['confidence']})</small>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f":red[⚠ {s['text']}]  \n<small>Unverified — not found in sources</small>",
                unsafe_allow_html=True,
            )
