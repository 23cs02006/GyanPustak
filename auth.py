import streamlit as st
import bcrypt
from database import get_connection
from datetime import date

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def login_user(email, password):
    conn = get_connection()
    if conn is None:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and verify_password(password, user['password_hash']):
        return user
    return None

def register_student(data):
    conn = get_connection()
    if conn is None:
        return False, "Database connection failed"
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s",
            (data['email'],)
        )
        if cursor.fetchone():
            return False, "Email already registered"
        pw_hash = hash_password(data['password'])
        cursor.execute("""
            INSERT INTO users
                (email, password_hash, role, first_name, last_name, phone, address)
            VALUES (%s, %s, 'student', %s, %s, %s, %s)
        """, (
            data['email'], pw_hash, data['first_name'],
            data['last_name'], data['phone'], data['address']
        ))
        user_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO student_details
                (student_id, date_of_birth, university, major,
                 student_status, year_of_study)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_id, data['dob'], data['university'],
            data['major'], data['status'], data['year']
        ))
        cursor.execute(
            "INSERT INTO carts (student_id) VALUES (%s)",
            (user_id,)
        )
        conn.commit()
        return True, "Registration successful!"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def reset_password(email, new_password):
    """Reset password for a user by email."""
    conn = get_connection()
    if conn is None:
        return False, "Database connection failed"
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT user_id, first_name FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        if not user:
            return False, "Email not found in our system."
        pw_hash = hash_password(new_password)
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (pw_hash, email)
        )
        conn.commit()
        return True, user['first_name']
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def show_login_page():

    # ── Show toast after registration ──
    if st.session_state.get('show_register_success'):
        st.toast(
            "✅ Registration Successful! You can now login.",
            icon="🎉"
        )
        del st.session_state['show_register_success']

    # ── Show toast after password reset ──
    if st.session_state.get('password_reset_success'):
        st.toast(
            "✅ Password Reset Successfully! Please login.",
            icon="🎉"
        )
        del st.session_state['password_reset_success']

    # ── Header ──
    st.markdown("""
    <div style="text-align:center; padding: 30px 0 10px 0;">
        <h1 style="color:#2C3E50; font-size:48px; font-weight:800; margin-bottom:0;">
            📚 GyanPustak
        </h1>
        <p style="color:#7F8C8D; font-size:18px; margin-top:5px;">
            Your Trusted Online Textbook Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Show success banner after registration ──
    if st.session_state.get('show_register_banner'):
        st.success(
            "🎉 Registration Successful! "
            "You can now login with your credentials."
        )
        del st.session_state['show_register_banner']

    # ── Show success banner after password reset ──
    if st.session_state.get('password_reset_banner'):
        st.success(
            "✅ Password Reset Successfully! "
            "You can now login with your new password."
        )
        del st.session_state['password_reset_banner']

    # ══════════════════════════════════════
    #   PAGE ROUTING
    # ══════════════════════════════════════

    # ── If forgot password page is active ──
    if st.session_state.get('show_forgot_password'):
        show_forgot_password_page()
        return

    # ── Normal tabs ──
    tab1, tab2, tab3 = st.tabs([
        "🔐 Login",
        "📝 Register",
        "🎫 Submit Trouble Ticket"
    ])

    # ══════════════════════════════════════
    #   LOGIN TAB
    # ══════════════════════════════════════
    with tab1:
        st.subheader("Welcome Back!")
        st.markdown("""
        <p style="color:#7F8C8D; font-size:14px;">
            Please login with your registered credentials.
            If you are a <strong>Customer Support</strong> or
            <strong>Administrator</strong>, your account is created
            by the Super Administrator.
        </p>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            email    = st.text_input(
                "📧 Email Address",
                placeholder="Enter your email",
                key="login_email"
            )
            password = st.text_input(
                "🔑 Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button(
                    "🔐 Login",
                    use_container_width=True,
                    type="primary"
                )
            if submitted:
                if not email or not password:
                    st.error("⚠️ Please fill in all fields.")
                else:
                    user = login_user(email, password)
                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['user']      = user
                        st.session_state['page']      = 'dashboard'
                        st.success(f"✅ Welcome, {user['first_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password.")

        # ── Forgot Password Button ──
        st.markdown("")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "🔑 Forgot Password?",
                use_container_width=True,
                key="forgot_pass_btn"
            ):
                st.session_state['show_forgot_password'] = True
                st.rerun()

    # ══════════════════════════════════════
    #   REGISTER TAB
    # ══════════════════════════════════════
    with tab2:
        st.subheader("📝 Student Registration")

        with st.form("register_student_form", clear_on_submit=False):
            st.markdown("##### 📋 Personal Details")
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input(
                    "First Name *",
                    placeholder="John",
                    key="s_fn"
                )
                email      = st.text_input(
                    "Email *",
                    placeholder="john@example.com",
                    key="s_email"
                )
                phone      = st.text_input(
                    "Phone",
                    placeholder="+91 XXXXXXXXXX",
                    key="s_phone"
                )
            with col2:
                last_name  = st.text_input(
                    "Last Name *",
                    placeholder="Doe",
                    key="s_ln"
                )
                password   = st.text_input(
                    "Password *",
                    type="password",
                    placeholder="Min. 6 characters",
                    key="s_pass"
                )
                dob        = st.date_input(
                    "Date of Birth",
                    min_value=date(1970, 1, 1),
                    max_value=date(2010, 12, 31),
                    key="s_dob"
                )

            st.markdown("##### 🎓 Academic Details")
            col3, col4 = st.columns(2)
            with col3:
                university     = st.text_input(
                    "University *",
                    placeholder="Your University Name",
                    key="s_uni"
                )
                student_status = st.selectbox(
                    "Student Status",
                    ["undergraduate", "graduate"],
                    key="s_status"
                )
            with col4:
                major = st.text_input(
                    "Major *",
                    placeholder="e.g. Computer Science",
                    key="s_major"
                )
                year  = st.selectbox(
                    "Year of Study",
                    [1, 2, 3, 4, 5, 6],
                    key="s_year"
                )

            address = st.text_area(
                "Address",
                placeholder="Your full address",
                key="s_addr"
            )

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button(
                    "📝 Register as Student",
                    use_container_width=True,
                    type="primary"
                )

            if submitted:
                if not first_name or not last_name or not email \
                        or not password or not university or not major:
                    st.error("⚠️ Please fill all required fields (*)")
                elif len(password) < 6:
                    st.error("⚠️ Password must be at least 6 characters.")
                else:
                    data = {
                        'first_name': first_name,
                        'last_name':  last_name,
                        'email':      email,
                        'password':   password,
                        'phone':      phone,
                        'address':    address,
                        'dob':        dob,
                        'university': university,
                        'major':      major,
                        'status':     student_status,
                        'year':       year
                    }
                    success, msg = register_student(data)
                    if success:
                        st.session_state['show_register_success'] = True
                        st.session_state['show_register_banner']  = True
                        st.session_state['active_tab']            = 0
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

    # ══════════════════════════════════════
    #   TROUBLE TICKET TAB
    # ══════════════════════════════════════
    with tab3:
        st.subheader("🎫 Submit a Trouble Ticket")
        st.info(
            "If you are a registered student, you can submit a "
            "trouble ticket here. It will be reviewed by our "
            "Customer Support team."
        )
        with st.form("ticket_form_login", clear_on_submit=False):
            ticket_email    = st.text_input(
                "Your Registered Email *",
                placeholder="Enter your registered email",
                key="t_email"
            )
            ticket_category = st.selectbox(
                "Category",
                ["user_profile", "products", "cart", "orders", "other"],
                key="t_cat"
            )
            ticket_title    = st.text_input(
                "Ticket Title *",
                placeholder="Brief title of your issue",
                key="t_title"
            )
            ticket_desc     = st.text_area(
                "Problem Description *",
                placeholder="Describe your problem in detail...",
                key="t_desc"
            )
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button(
                    "🎫 Submit Ticket",
                    use_container_width=True,
                    type="primary"
                )
            if submitted:
                if not ticket_email or not ticket_title or not ticket_desc:
                    st.error("⚠️ Please fill all required fields (*)")
                else:
                    conn = get_connection()
                    if conn:
                        cursor = conn.cursor(dictionary=True)
                        cursor.execute(
                            "SELECT user_id, role FROM users WHERE email = %s",
                            (ticket_email,)
                        )
                        user = cursor.fetchone()
                        if user and user['role'] == 'student':
                            cursor.execute("""
                                INSERT INTO trouble_tickets
                                    (category, title, problem_description,
                                     ticket_status, created_by, created_by_role)
                                VALUES (%s, %s, %s, 'new', %s, 'student')
                            """, (
                                ticket_category, ticket_title,
                                ticket_desc, user['user_id']
                            ))
                            conn.commit()
                            st.success(
                                "✅ Ticket submitted successfully! "
                                "Our team will review it shortly."
                            )
                        elif user:
                            st.error(
                                "❌ Only students can submit tickets "
                                "from this page. Please login to "
                                "your dashboard."
                            )
                        else:
                            st.error(
                                "❌ Email not found. "
                                "Please register first."
                            )
                        cursor.close()
                        conn.close()

    # ── Footer ──
    show_footer()


# ══════════════════════════════════════
#   FORGOT PASSWORD PAGE
# ══════════════════════════════════════
def show_forgot_password_page():

    # ── Back button at top ──
    if st.button("← Back to Login", key="back_to_login"):
        # ── Clear all fp session keys ──
        for key in [
            'show_forgot_password',
            'fp_email_verified',
            'fp_verified_email',
            'fp_user_name',
            'fp_user_role'
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown("""
    <div style="text-align:center; padding: 10px 0 20px 0;">
        <h2 style="color:#2C3E50; font-weight:800;">🔑 Forgot Password</h2>
        <p style="color:#7F8C8D; font-size:15px;">
            Reset your GyanPustak account password
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#FEF9E7; border-left:4px solid #F39C12;
                padding:15px 20px; border-radius:8px; margin-bottom:20px;">
        <p style="margin:0; color:#2C3E50; font-size:14px;">
            ℹ️ Enter your registered email address and
            set a <strong>new password</strong> directly.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Step 1: Verify Email ──
    if not st.session_state.get('fp_email_verified'):

        st.markdown("##### 📧 Step 1: Verify Your Email")
        with st.form("fp_verify_email", clear_on_submit=False):
            fp_email_input = st.text_input(
                "Registered Email Address *",
                placeholder="Enter your registered email",
                key="fp_email_input"
            )
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                verify_submitted = st.form_submit_button(
                    "🔍 Verify Email",
                    use_container_width=True,
                    type="primary"
                )

            if verify_submitted:
                if not fp_email_input:
                    st.error("⚠️ Please enter your email address.")
                else:
                    conn = get_connection()
                    if conn:
                        cursor = conn.cursor(dictionary=True)
                        cursor.execute(
                            """SELECT user_id, first_name,
                                      last_name, role
                               FROM users WHERE email = %s""",
                            (fp_email_input,)
                        )
                        found_user = cursor.fetchone()
                        cursor.close()
                        conn.close()
                        if found_user:
                            st.session_state['fp_email_verified'] = True
                            st.session_state['fp_verified_email'] = fp_email_input
                            st.session_state['fp_user_name']      = found_user['first_name']
                            st.session_state['fp_user_role']      = found_user['role']
                            st.rerun()
                        else:
                            st.error(
                                "❌ Email not found in our system. "
                                "Please check and try again."
                            )

    # ── Step 2: Set New Password ──
    else:
        fp_verified_email = st.session_state.get('fp_verified_email', '')
        fp_user_name      = st.session_state.get('fp_user_name', '')
        fp_user_role      = st.session_state.get('fp_user_role', '')

        st.success(
            f"✅ Email verified! Hello, **{fp_user_name}** "
            f"({fp_user_role.replace('_', ' ').title()})."
        )
        st.markdown(
            f"📧 Resetting password for: **{fp_verified_email}**"
        )

        st.markdown("---")
        st.markdown("##### 🔐 Step 2: Set New Password")

        with st.form("fp_set_password", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                new_pass = st.text_input(
                    "New Password *",
                    type="password",
                    placeholder="Min. 6 characters",
                    key="fp_new_pass"
                )
            with col2:
                confirm_pass = st.text_input(
                    "Confirm New Password *",
                    type="password",
                    placeholder="Confirm new password",
                    key="fp_confirm_pass"
                )
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                reset_submitted = st.form_submit_button(
                    "💾 Set New Password",
                    use_container_width=True,
                    type="primary"
                )

            if reset_submitted:
                if not new_pass or not confirm_pass:
                    st.error("⚠️ Please fill both password fields.")
                elif len(new_pass) < 6:
                    st.error("⚠️ Password must be at least 6 characters.")
                elif new_pass != confirm_pass:
                    st.error("⚠️ Passwords do not match.")
                else:
                    success, result = reset_password(
                        fp_verified_email, new_pass
                    )
                    if success:
                        # ── Clear all fp session keys ──
                        for key in [
                            'show_forgot_password',
                            'fp_email_verified',
                            'fp_verified_email',
                            'fp_user_name',
                            'fp_user_role'
                        ]:
                            if key in st.session_state:
                                del st.session_state[key]

                        # ── Set flags to show on login page ──
                        st.session_state['password_reset_success'] = True
                        st.session_state['password_reset_banner']  = True

                        # ── Redirect to login page ──
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")

        st.markdown("")

        # ── Use different email button ──
        if st.button(
            "🔙 Use Different Email",
            use_container_width=False,
            key="use_diff_email"
        ):
            for key in [
                'fp_email_verified',
                'fp_verified_email',
                'fp_user_name',
                'fp_user_role'
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # ── Footer ──
    show_footer()


# ══════════════════════════════════════
#   FOOTER
# ══════════════════════════════════════
def show_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:20px; color:#7F8C8D;">
        <p style="font-size:14px;">
            📚 <strong>GyanPustak</strong> —
            Your Trusted Online Textbook Platform
        </p>
        <p style="font-size:12px;">
            Buy, Rent &amp; Explore Textbooks for College Students
        </p>
        <p style="font-size:12px;">
            📧 support@gyanpustak.com | 📞 +91-1800-XXX-XXXX
        </p>
        <p style="font-size:11px; color:#BDC3C7;">
            © 2025 GyanPustak. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)