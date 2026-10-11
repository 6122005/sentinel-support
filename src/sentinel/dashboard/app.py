"""Sentinel — Support Operations Platform.

Minimalist, clean, production-grade interface without clutter or vanity metrics.
Focuses directly on:
1. Support ticket submission & live routing
2. Manager approval authorization queue
3. Audit log verification
"""

import streamlit as st
import httpx

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Sentinel Support",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# Clean, Modern Minimalist Styling
# -------------------------------------------------------------
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <style>
    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Minimalist Header */
    .clean-header {
        padding: 0.25rem 0 0.85rem 0;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 1.25rem;
    }
    
    .clean-title {
        font-size: 1.65rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #0F172A;
        margin: 0;
    }
    
    /* Clean Enterprise Cards */
    .clean-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.15rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.04);
        margin-bottom: 0.85rem;
    }
    
    /* Live / Alert Indicators */
    .badge-live {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #ECFDF5;
        color: #065F46;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid #A7F3D0;
    }
    
    .badge-alert {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #FEF2F2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid #FECACA;
    }

    .live-dot {
        width: 8px;
        height: 8px;
        background: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
    }
    
    .alert-dot {
        width: 8px;
        height: 8px;
        background: #EF4444;
        border-radius: 50%;
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
    }

    /* Execution Stage Item */
    .stage-item {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .stage-text {
        font-weight: 600;
        color: #1E293B;
        font-size: 0.85rem;
    }
    
    .stage-tag {
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 2px 7px;
        border-radius: 4px;
        letter-spacing: 0.03em;
    }
    .tag-ok { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
    .tag-review { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
    
    .field-tag {
        font-size: 0.8rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# Check Backend Health Status
# -------------------------------------------------------------
is_operational = False
try:
    health_res = httpx.get(f"{API_BASE_URL}/health", timeout=1.5)
    is_operational = health_res.status_code == 200
except Exception:
    is_operational = False

# -------------------------------------------------------------
# Minimalist Sidebar
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛡️ **Sentinel**")
    st.caption("Customer Support Platform")

    if is_operational:
        st.markdown(
            """
            <div class="badge-live">
                <div class="live-dot"></div> Status · Operational
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="badge-alert">
                <div class="alert-dot"></div> Status · Offline
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if st.button("🔄 Refresh State", width="stretch"):
        st.rerun()

# -------------------------------------------------------------
# Clean Minimalist Title
# -------------------------------------------------------------
st.markdown(
    """
    <div class="clean-header">
        <h2 class="clean-title">🛡️ Sentinel Support Desk</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

# Straight into the core tabs
tab_support, tab_approvals, tab_audit = st.tabs([
    "📥 Support Desk",
    "🛡️ Manager Approvals",
    "📋 Audit Logs",
])

# -------------------------------------------------------------
# TAB 1: Support Desk
# -------------------------------------------------------------
with tab_support:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("##### 📝 Create Ticket")
        
        # Sample Inquiry Presets
        st.markdown("<div class='field-tag'>Sample Inquiries:</div>", unsafe_allow_html=True)
        b1, b2, b3, b4 = st.columns(4)
        
        if b1.button("💵 $29 Refund", help="Refund request under $50"):
            st.session_state["msg"] = "Please refund order ord_902 charged incorrectly"
            st.session_state["cust"] = "cust_102"
        if b2.button("⚠️ $490 Refund", help="High-value refund exceeding limit"):
            st.session_state["msg"] = "I was charged twice for ord_901, please issue refund"
            st.session_state["cust"] = "cust_101"
        if b3.button("📱 App Crash", help="Technical troubleshooting"):
            st.session_state["msg"] = "Application crashes immediately upon login"
            st.session_state["cust"] = "cust_105"
        if b4.button("❓ Unclear Query", help="Incomplete description"):
            st.session_state["msg"] = "Something went wrong on my dashboard earlier"
            st.session_state["cust"] = "cust_109"

        customer_id = st.text_input(
            "Customer ID",
            value=st.session_state.get("cust", "cust_101"),
            placeholder="e.g. cust_101",
        )
        
        message = st.text_area(
            "Customer Message",
            value=st.session_state.get("msg", "Please refund order ord_902 charged incorrectly"),
            placeholder="Enter customer message...",
            height=100,
        )

        submit_btn = st.button("🚀 Submit Ticket", type="primary", width="stretch")

    with col_right:
        st.markdown("##### ⚡ Resolution Output")

        if submit_btn and message:
            with st.spinner("Processing ticket..."):
                try:
                    payload = {"customer_id": customer_id, "message": message}
                    res = httpx.post(f"{API_BASE_URL}/tickets", json=payload, timeout=15.0)

                    if res.status_code == 200:
                        data = res.json()
                        status = data.get("status")
                        ticket_id = data.get("ticket_id")

                        st.session_state["last_ticket_id"] = ticket_id

                        if status == "resolved":
                            st.success(f"**Ticket #{ticket_id[:8]} · Resolved**", icon="✅")
                            st.markdown(
                                f"""
                                <div class="clean-card">
                                    <div style="font-size: 0.75rem; font-weight: 700; color: #15803D; text-transform: uppercase;">Resolution</div>
                                    <div style="font-size: 1rem; color: #0F172A; margin-top: 5px;">{data.get('resolution')}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.warning(f"**Ticket #{ticket_id[:8]} · Pending Manager Approval**", icon="🛡️")
                            st.markdown(
                                f"""
                                <div class="clean-card" style="border-left: 4px solid #F59E0B;">
                                    <div style="font-size: 0.75rem; font-weight: 700; color: #B45309; text-transform: uppercase;">Escalation Notice</div>
                                    <pre style="margin-top: 6px; font-size: 0.85rem; background: #FFFBEB; padding: 10px; border-radius: 6px; color: #78350F; white-space: pre-wrap;">{data.get('summary')}</pre>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            st.info("Ticket held for manager authorization. Open **Manager Approvals** to review.", icon="ℹ️")

                        # Execution Steps
                        trace = data.get("trace", [])
                        if trace:
                            st.markdown("###### Processing Stages")
                            stage_names = {
                                "intake": ("Request Intake & Validation", "tag-ok"),
                                "classify": ("Intent Classification", "tag-ok"),
                                "billing": ("Billing & Transaction Verification", "tag-ok"),
                                "tech": ("Technical Knowledge Diagnostic", "tag-ok"),
                                "escalate": ("Approval Gate Triggered", "tag-review"),
                            }
                            for step in trace:
                                node = step.get("node", "step")
                                name, tag_style = stage_names.get(node, (node.capitalize(), "tag-ok"))
                                st.markdown(
                                    f"""
                                    <div class="stage-item">
                                        <div class="stage-text">{name}</div>
                                        <div class="stage-tag {tag_style}">Complete</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")
                except Exception as exc:
                    st.error(f"Connection error: {str(exc)}")
        else:
            st.markdown(
                """
                <div class="clean-card" style="text-align: center; color: #64748B; padding: 2.5rem 1rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.35rem;">📥</div>
                    <div style="font-weight: 600; color: #1E293B;">Ready</div>
                    <div style="font-size: 0.82rem; margin-top: 2px;">Submit a ticket to view resolution and routing.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# -------------------------------------------------------------
# TAB 2: Manager Approvals
# -------------------------------------------------------------
with tab_approvals:
    st.markdown("##### 🛡️ Pending Approvals")

    col_app_l, col_app_r = st.columns([1, 1], gap="large")

    with col_app_l:
        target_id = st.text_input(
            "Ticket ID",
            value=st.session_state.get("last_ticket_id", ""),
            placeholder="Enter ticket UUID",
        )
        
        manager_note = st.text_input("Review Note", value="Approved by operations manager")

        btn_yes, btn_no = st.columns(2)
        approve_hit = btn_yes.button("✅ Approve", type="primary", width="stretch")
        deny_hit = btn_no.button("❌ Reject", width="stretch")

        if (approve_hit or deny_hit) and target_id:
            action = True if approve_hit else False
            with st.spinner("Updating ticket..."):
                try:
                    resume_body = {"approved": action, "note": manager_note}
                    r_res = httpx.post(f"{API_BASE_URL}/tickets/{target_id}/resume", json=resume_body, timeout=10.0)
                    if r_res.status_code == 200:
                        st.session_state["resume_result"] = r_res.json()
                        st.success(f"Ticket #{target_id[:8]} updated: {'Approved' if action else 'Rejected'}")
                    else:
                        st.error(f"Failed: {r_res.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    with col_app_r:
        st.markdown("###### Status")
        auth_data = st.session_state.get("resume_result")
        if auth_data:
            st.markdown(
                f"""
                <div class="clean-card">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #047857; text-transform: uppercase;">Status: Completed</div>
                    <div style="font-size: 0.95rem; color: #0F172A; margin-top: 5px;">{auth_data.get('resolution') or 'Action completed.'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander("Details"):
                st.json(auth_data)
        else:
            st.markdown(
                """
                <div class="clean-card" style="text-align: center; color: #64748B; padding: 2rem 1rem;">
                    <div style="font-size: 1.6rem; margin-bottom: 0.35rem;">📋</div>
                    <div style="font-weight: 600; color: #1E293B;">No Selection</div>
                    <div style="font-size: 0.82rem; margin-top: 2px;">Enter a ticket ID on the left to approve.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# -------------------------------------------------------------
# TAB 3: Audit Logs
# -------------------------------------------------------------
with tab_audit:
    st.markdown("##### 📋 Audit Logs")

    col_s_box, col_s_btn = st.columns([4, 1])
    with col_s_box:
        lookup_id = st.text_input(
            "Search Ticket ID",
            value=st.session_state.get("last_ticket_id", ""),
            placeholder="e.g. 9ee34bd5-7b4f-4110-ade0-787278894bd7",
            label_visibility="collapsed",
        )
    with col_s_btn:
        find_btn = st.button("Search", type="primary", width="stretch")

    if find_btn and lookup_id:
        try:
            t_res = httpx.get(f"{API_BASE_URL}/trace/{lookup_id}", timeout=5.0)
            if t_res.status_code == 200:
                t_data = t_res.json()
                st.success(f"Log found for #{lookup_id}")
                st.dataframe(t_data.get("trace", []), width="stretch")
                with st.expander("Raw Record"):
                    st.json(t_data)
            else:
                st.warning(f"No log found for #{lookup_id}")
        except Exception as e:
            st.error(f"Lookup error: {str(e)}")
