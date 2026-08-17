import os
import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = os.getenv("API_URL",
    "http://127.0.0.1:8000")


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "status" not in st.session_state:
    st.session_state.status = None

if "report" not in st.session_state:
    st.session_state.report = None

if "approval" not in st.session_state:
    st.session_state.approval = None

if "question" not in st.session_state:
    st.session_state.question = ""


# ============================================================
# HEADER
# ============================================================

st.title("🔎 AI Research Agent")

st.write(
    "Research a topic using web search and the project's "
    "knowledge base, then review and approve the generated report."
)


# ============================================================
# RESEARCH QUESTION
# ============================================================

st.subheader("Research Question")

question = st.text_area(
    "Enter your question",
    placeholder="Example: Explain LangGraph in detail",
    height=120,
    label_visibility="collapsed",
)


# ============================================================
# START RESEARCH
# ============================================================

if st.button(
    "🚀 Start Research",
    type="primary",
    use_container_width=True,
):

    if not question.strip():

        st.warning(
            "Please enter a research question."
        )

    else:

        try:

            with st.spinner(
                "Researching your question..."
            ):

                response = requests.post(
                    f"{API_URL}/research",
                    json={
                        "question": question.strip()
                    },
                    timeout=300,
                )

            if response.status_code != 200:

                st.error(
                    f"Research failed: {response.text}"
                )

            else:

                data = response.json()

                # Keep thread ID internally.
                # Do NOT display it to the user.

                st.session_state.thread_id = (
                    data.get("thread_id")
                )

                st.session_state.status = (
                    data.get("status")
                )

                st.session_state.question = (
                    question.strip()
                )

                st.session_state.approval = (
                    data.get("approval")
                )

                # ------------------------------------------------
                # If workflow already completed
                # ------------------------------------------------

                st.session_state.report = (
                    data.get("report")
                )

                st.rerun()

        except requests.exceptions.RequestException as exc:

            st.error(
                "Could not connect to the AI Research API."
            )

            st.caption(
                f"Details: {exc}"
            )


# ============================================================
# HUMAN REVIEW
# ============================================================

if (
    st.session_state.status
    == "waiting_for_approval"
):

    approval = (
        st.session_state.approval
        or {}
    )

    report = approval.get(
        "report",
        ""
    )


    # ========================================================
    # REPORT
    # ========================================================

    st.divider()

    st.header("📄 Research Report")

    if report:

        st.markdown(report)

    else:

        st.warning(
            "The research report is not available."
        )


    # ========================================================
    # HUMAN REVIEW
    # ========================================================

    st.divider()

    st.header("👤 Review the Report")

    st.write(
        "Read the report above carefully. "
        "If it satisfies your requirements, approve it. "
        "Otherwise reject it and provide revision instructions."
    )


    # ========================================================
    # REVISION INSTRUCTIONS
    # ========================================================

    revision_reason = st.text_area(
        "Revision instructions",
        placeholder=(
            "If you reject the report, explain what "
            "needs to be improved..."
        ),
        height=120,
    )


    # ========================================================
    # DECISION BUTTONS
    # ========================================================

    col1, col2 = st.columns(2)


    # ========================================================
    # APPROVE
    # ========================================================

    with col1:

        if st.button(
            "✅ Approve Report",
            type="primary",
            use_container_width=True,
        ):

            try:

                with st.spinner(
                    "Finalizing the research..."
                ):

                    response = requests.post(
                        (
                            f"{API_URL}/research/"
                            f"{st.session_state.thread_id}"
                            "/decision"
                        ),
                        json={
                            "decision": "approve",
                            "revision_reason": "",
                        },
                        timeout=300,
                    )


                if response.status_code != 200:

                    st.error(
                        f"Approval failed: {response.text}"
                    )

                else:

                    data = response.json()

                    # --------------------------------------------
                    # Save final report
                    # --------------------------------------------

                    st.session_state.report = (
                        data.get("report")
                    )

                    # --------------------------------------------
                    # Clear approval state
                    # --------------------------------------------

                    st.session_state.approval = None

                    st.session_state.status = (
                        "completed"
                    )

                    st.rerun()


            except requests.exceptions.RequestException as exc:

                st.error(
                    "Could not connect to the AI Research API."
                )

                st.caption(
                    f"Details: {exc}"
                )


    # ========================================================
    # REJECT
    # ========================================================

    with col2:

        if st.button(
            "❌ Reject & Revise",
            use_container_width=True,
        ):

            if not revision_reason.strip():

                st.warning(
                    "Please provide revision instructions "
                    "before rejecting the report."
                )

            else:

                try:

                    with st.spinner(
                        "Revising the research report..."
                    ):

                        response = requests.post(
                            (
                                f"{API_URL}/research/"
                                f"{st.session_state.thread_id}"
                                "/decision"
                            ),
                            json={
                                "decision": "reject",
                                "revision_reason":
                                    revision_reason.strip(),
                            },
                            timeout=300,
                        )


                    if response.status_code != 200:

                        st.error(
                            f"Revision failed: {response.text}"
                        )

                    else:

                        data = response.json()


                        # ----------------------------------------
                        # If another human approval is required
                        # ----------------------------------------

                        if (
                            data.get("status")
                            == "waiting_for_approval"
                        ):

                            st.session_state.status = (
                                "waiting_for_approval"
                            )

                            st.session_state.approval = (
                                data.get("approval")
                            )

                            st.session_state.report = None

                            st.success(
                                "The report has been revised. "
                                "Please review the new version."
                            )

                            st.rerun()


                        # ----------------------------------------
                        # Unexpected completion
                        # ----------------------------------------

                        else:

                            st.session_state.status = (
                                data.get("status")
                            )

                            st.session_state.report = (
                                data.get("report")
                            )

                            st.session_state.approval = None

                            st.rerun()


                except requests.exceptions.RequestException as exc:

                    st.error(
                        "Could not connect to the AI Research API."
                    )

                    st.caption(
                        f"Details: {exc}"
                    )


# ============================================================
# FINAL REPORT
# ============================================================

if (
    st.session_state.status
    == "completed"
):

    st.divider()

    st.header("📄 Final Research Report")

    if st.session_state.report:

        st.markdown(
            st.session_state.report
        )

    else:

        st.warning(
            "The final report could not be retrieved."
        )


# ============================================================
# RESET
# ============================================================

st.divider()

if st.button(
    "🔄 New Research",
    use_container_width=True,
):

    st.session_state.thread_id = None
    st.session_state.status = None
    st.session_state.report = None
    st.session_state.approval = None
    st.session_state.question = ""

    st.rerun()