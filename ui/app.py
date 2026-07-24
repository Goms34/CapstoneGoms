"""Streamlit UI for Loan Approval System."""

import streamlit as st
import requests
import time
import json
from datetime import datetime

FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Loan Approval System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("💰 Intelligent Loan Approval System")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📝 New Application", "📊 Check Status", "📋 All Applications"])

with tab1:
    st.header("Submit Loan Application")

    col1, col2 = st.columns(2)

    with col1:
        applicant_id = st.text_input("Applicant ID", value="APP001")
        applicant_name = st.text_input("Full Name", value="John Doe")
        age = st.number_input("Age", min_value=18, max_value=100, value=35)
        employment_type = st.selectbox(
            "Employment Type",
            ["Full-Time", "Part-Time", "Self-Employed", "Freelance", "Contract"],
            index=0,
        )
        employment_years = st.number_input("Years of Employment", min_value=0, value=5)

    with col2:
        annual_income = st.number_input("Annual Income ($)", min_value=0.0, value=85000.0)
        existing_liabilities = st.number_input("Existing Liabilities ($)", min_value=0.0, value=15000.0)
        credit_score = st.number_input(
            "Credit Score", min_value=300, max_value=850, value=720
        )
        location = st.text_input("Location", value="New York")
        email = st.text_input("Email", value="applicant@example.com")

    col3, col4 = st.columns(2)

    with col3:
        loan_amount = st.number_input("Loan Amount ($)", min_value=1000.0, value=50000.0)

    with col4:
        loan_tenure_months = st.number_input("Loan Tenure (months)", min_value=1, value=60)

    if st.button("Submit Application", type="primary", use_container_width=True):
        with st.spinner("Submitting application..."):
            try:
                payload = {
                    "applicant_id": applicant_id,
                    "applicant_name": applicant_name,
                    "age": int(age),
                    "annual_income": float(annual_income),
                    "employment_type": employment_type,
                    "employment_years": int(employment_years),
                    "existing_liabilities": float(existing_liabilities),
                    "credit_score": int(credit_score),
                    "loan_amount": float(loan_amount),
                    "loan_tenure_months": int(loan_tenure_months),
                    "location": location,
                    "email": email,
                }

                response = requests.post(f"{FASTAPI_URL}/api/applications", json=payload)

                if response.status_code == 200:
                    result = response.json()
                    st.session_state.submitted_app_id = result["application_id"]
                    st.success(f"✅ Application submitted successfully!")
                    st.info(
                        f"**Application ID:** `{result['application_id']}`\n\n"
                        f"Your application is being processed. Use the 'Check Status' tab to view the decision."
                    )

                    with st.expander("View Request Details"):
                        st.json(payload)
                else:
                    st.error(f"❌ Error: {response.text}")

            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")

with tab2:
    st.header("Check Application Status")

    col1, col2 = st.columns([3, 1])

    with col1:
        app_id = st.text_input(
            "Application ID",
            value=st.session_state.get("submitted_app_id", ""),
        )

    with col2:
        check_button = st.button("Check Status", type="primary", use_container_width=True)

    if check_button and app_id:
        with st.spinner("Fetching application details..."):
            try:
                response = requests.get(f"{FASTAPI_URL}/api/applications/{app_id}")

                if response.status_code == 200:
                    app_status = response.json()

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Status", app_status.get("status", "unknown").upper())

                    with col2:
                        st.metric("Applicant", app_status.get("applicant_id", "N/A"))

                    with col3:
                        st.metric(
                            "Submitted",
                            app_status.get("submitted_at", "N/A")[:10],
                        )

                    st.markdown("---")

                    if app_status.get("decision"):
                        st.subheader("📋 Decision Result")

                        decision_response = requests.get(
                            f"{FASTAPI_URL}/api/applications/{app_id}/decision"
                        )

                        if decision_response.status_code == 200:
                            decision_data = decision_response.json()
                            decision = decision_data["decision"]

                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                decision_color = (
                                    "🟢"
                                    if decision["decision"] == "Approve"
                                    else "🔴"
                                    if decision["decision"] == "Reject"
                                    else "🟡"
                                )
                                st.metric(
                                    "Decision",
                                    f"{decision_color} {decision['decision']}",
                                )

                            with col2:
                                st.metric(
                                    "Risk Score",
                                    f"{decision['risk_score']:.2%}",
                                )

                            with col3:
                                st.metric(
                                    "Confidence",
                                    f"{decision['confidence']:.0%}",
                                )

                            with col4:
                                st.metric(
                                    "Case ID",
                                    decision.get("case_id", "N/A")[:8],
                                )

                            st.markdown("---")

                            col1, col2 = st.columns([1, 1])

                            with col1:
                                st.subheader("📝 Rationale")
                                st.write(decision["rationale"])

                            with col2:
                                st.subheader("🔑 Key Factors")
                                for factor in decision["key_factors"]:
                                    st.write(f"• {factor}")

                            if decision_data.get("audit_trail"):
                                with st.expander("View Audit Trail"):
                                    st.json(decision_data["audit_trail"])

                    else:
                        st.info(
                            "⏳ Decision is still being processed. Please check back in a few moments."
                        )

                elif response.status_code == 404:
                    st.error(f"❌ Application '{app_id}' not found.")
                else:
                    st.error(f"❌ Error: {response.text}")

            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")

with tab3:
    st.header("All Applications")

    if st.button("Refresh", use_container_width=True):
        pass

    try:
        response = requests.get(f"{FASTAPI_URL}/api/applications")

        if response.status_code == 200:
            data = response.json()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Applications", data["total"])

            if data["applications"]:
                st.dataframe(
                    data["applications"],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("📭 No applications submitted yet.")

        else:
            st.error(f"❌ Error: {response.text}")

    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")

st.markdown("---")
st.markdown(
    """
### About This System
This is an **Intelligent Loan Approval System** powered by multi-agent AI:
- **Domain-specific agents** analyze applicant profiles, financial risk, and make decisions
- **LangGraph orchestration** coordinates the workflow across agents
- **Claude AI** provides intelligent reasoning for each decision
- **Explainable decisions** with reasoning and key factors

For questions, check the documentation or contact support.
"""
)
