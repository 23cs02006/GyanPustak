import streamlit as st
from database import initialize_database, get_connection
from auth import show_login_page
from student import show_student_dashboard
from customer_support import show_cs_dashboard
from administrator import show_admin_dashboard
from super_admin import show_super_admin_dashboard

# ── Page config ──
st.set_page_config(
    page_title="GyanPustak — Online Textbook Platform",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ──
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #FDF5E6 !important;
    }

    /* Force sidebar always open */
    [data-testid="stSidebar"] {
        min-width: 280px !important;
        max-width: 280px !important;
        width: 280px !important;
        display: block !important;
        visibility: visible !important;
        transform: translateX(0px) !important;
        left: 0 !important;
        background-color: #FDFEFE !important;
        border-right: 2px solid #E5E7E9 !important;
    }

    /* Hide collapse button */
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Main content */
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* ══════════════════════════════════════
       BUTTON STYLING — WORKS ON ALL DEVICES
       ══════════════════════════════════════ */

    /* All buttons base style */
    .stButton > button,
    button[kind="primary"],
    button[kind="secondary"],
    .stButton > button:active,
    .stButton > button:focus,
    .stButton > button:hover,
    .stButton > button:visited {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        -webkit-appearance: none !important;
        -moz-appearance: none !important;
        appearance: none !important;
    }

    /* Primary button — force consistent color */
    .stButton > button[kind="primary"],
    button[data-testid="stFormSubmitButton"] > button,
    .stFormSubmitButton > button {
        background-color: #FF4B4B !important;
        color: white !important;
        border: none !important;
        -webkit-appearance: none !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button:hover {
        background-color: #E03E3E !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }

    /* Secondary buttons */
    .stButton > button:not([kind="primary"]) {
        background-color: white !important;
        color: #2C3E50 !important;
        border: 1px solid #E5E7E9 !important;
        -webkit-appearance: none !important;
    }

    .stButton > button:not([kind="primary"]):hover {
        background-color: #F8F9FA !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }

    /* ══════════════════════════════════════
       FORM STYLING
       ══════════════════════════════════════ */

    [data-testid="stForm"] {
        background: white !important;
        padding: 25px !important;
        border-radius: 12px !important;
        border: 1px solid #E5E7E9 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }

    /* ══════════════════════════════════════
       METRIC CARDS
       ══════════════════════════════════════ */

    [data-testid="stMetric"] {
        background: white !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #E5E7E9 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #2C3E50 !important;
    }

    /* ══════════════════════════════════════
       EXPANDER
       ══════════════════════════════════════ */

    .streamlit-expanderHeader {
        font-weight: 600 !important;
        color: #2C3E50 !important;
        background: white !important;
        border-radius: 8px !important;
    }

    /* ══════════════════════════════════════
       TABS
       ══════════════════════════════════════ */

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: white !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
    }

    /* ══════════════════════════════════════
       INPUTS
       ══════════════════════════════════════ */

    .stTextInput > div > div > input {
        border-radius: 8px !important;
    }
    .stSelectbox > div > div {
        border-radius: 8px !important;
    }

    /* ══════════════════════════════════════
       HIDE STREAMLIT BRANDING
       ══════════════════════════════════════ */

    #MainMenu  { visibility: hidden !important; }
    header     { visibility: hidden !important; }
    footer     { visibility: hidden !important; }

    /* ══════════════════════════════════════
       SCROLLBAR
       ══════════════════════════════════════ */

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #FDF5E6; }
    ::-webkit-scrollbar-thumb { background: #BDC3C7; border-radius: 4px; }

    /* ══════════════════════════════════════
       MOBILE RESPONSIVE FIXES
       ══════════════════════════════════════ */

    @media (max-width: 768px) {
        /* Sidebar on mobile */
        [data-testid="stSidebar"] {
            min-width: 250px !important;
            max-width: 250px !important;
        }

        /* Smaller padding on mobile */
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        /* Force button colors on mobile */
        .stButton > button,
        .stButton > button:active,
        .stButton > button:focus {
            -webkit-appearance: none !important;
            -webkit-tap-highlight-color: transparent !important;
        }

        /* Metric cards smaller on mobile */
        [data-testid="stMetricValue"] {
            font-size: 22px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ── Initialize Database ──
initialize_database()


# ════════════════════════════════════════════
#   SESSION PERSISTENCE FUNCTIONS
# ════════════════════════════════════════════

def save_session(user_id):
    """Save user_id to query params so it persists on refresh."""
    try:
        st.query_params["uid"] = str(user_id)
    except Exception:
        pass


def clear_session():
    """Clear query params and session state on logout."""
    try:
        st.query_params.clear()
    except Exception:
        pass
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def restore_session():
    """
    On refresh, if session state is lost but query param uid exists,
    re-fetch user from DB and restore session state.
    """
    try:
        uid = st.query_params.get("uid", None)
    except Exception:
        uid = None

    if uid and not st.session_state.get('logged_in', False):
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (int(uid),))
                user = cursor.fetchone()
                cursor.close()
                conn.close()
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user']      = user
                    st.session_state['page']      = 'dashboard'
        except Exception:
            pass


# ════════════════════════════════════════════
#   MAIN APP ROUTING
# ════════════════════════════════════════════

# Step 1: Try to restore session from query params (handles refresh)
restore_session()

# Step 2: Initialize session state defaults
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Step 3: Route to correct page
if not st.session_state.get('logged_in', False):
    # ── Clear any leftover query params ──
    try:
        st.query_params.clear()
    except Exception:
        pass
    show_login_page()

else:
    user = st.session_state.get('user')

    if user:
        # ── Save session to query params on every render ──
        save_session(user['user_id'])

        role = user['role']
        if role == 'student':
            show_student_dashboard()
        elif role == 'customer_support':
            show_cs_dashboard()
        elif role == 'administrator':
            show_admin_dashboard()
        elif role == 'super_admin':
            show_super_admin_dashboard()
        else:
            st.error("Unknown role. Please contact support.")
            if st.button("Go to Login"):
                clear_session()
                st.rerun()
    else:
        st.session_state['logged_in'] = False
        try:
            st.query_params.clear()
        except Exception:
            pass
        st.rerun()
