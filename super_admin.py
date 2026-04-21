import streamlit as st
from streamlit_option_menu import option_menu
from database import get_connection
from student import show_footer 
from auth import hash_password

def apply_sidebar_fix():
    st.markdown("""
    <style>
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
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        .block-container {
            padding-top: 1.5rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

def show_super_admin_dashboard():
    user = st.session_state['user']
    apply_sidebar_fix()

    # ── Show toast notification if exists ──
    if st.session_state.get('toast_message'):
        st.toast(
            st.session_state['toast_message'],
            icon=st.session_state.get('toast_icon', '✅')
        )
        del st.session_state['toast_message']
        if 'toast_icon' in st.session_state:
            del st.session_state['toast_icon']

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding:15px 0 10px 0;">
            <div style="
                width:75px; height:75px; border-radius:50%;
                background:linear-gradient(135deg,#C0392B,#E74C3C);
                display:flex; align-items:center; justify-content:center;
                margin:0 auto; font-size:32px; color:white; font-weight:700;
                box-shadow: 0 4px 12px rgba(192,57,43,0.4);
            ">
                {user['first_name'][0].upper()}
            </div>
            <h3 style="margin-top:10px; margin-bottom:2px; color:#2C3E50; font-size:16px;">
                {user['first_name']} {user['last_name']}
            </h3>
            <p style="color:#7F8C8D; font-size:12px; margin:0;">Super Administrator</p>
        </div>
        <hr style="border:none; border-top:1px solid #E5E7E9; margin:10px 0;">
        """, unsafe_allow_html=True)

        selected = option_menu(
            menu_title=None,
            options=[
                "Dashboard",
                "Add Employee",
                "Manage Employees",
                "All Users",
                "Profile",
                "Logout"
            ],
            icons=[
                "speedometer2",
                "person-plus",
                "people",
                "person-lines-fill",
                "person-circle",
                "box-arrow-right"
            ],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {"padding": "0px", "background-color": "transparent"},
                "icon": {"color": "#C0392B", "font-size": "17px"},
                "nav-link": {
                    "font-size": "14px", "text-align": "left",
                    "margin": "3px 0", "padding": "10px 15px",
                    "border-radius": "8px", "color": "#2C3E50", "font-weight": "500",
                },
                "nav-link-selected": {
                    "background-color": "#C0392B", "color": "white", "font-weight": "700",
                },
            }
        )

    # ══════════════════════════════════════
    #   LOGOUT
    # ══════════════════════════════════════
    if selected == "Logout":
        try:
            st.query_params.clear()
        except Exception:
            pass
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # ══════════════════════════════════════
    #   DASHBOARD
    # ══════════════════════════════════════
    elif selected == "Dashboard":
        st.title("Super Administrator Dashboard")
        st.markdown(f"### Welcome, **{user['first_name']}**! 👋")

        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'student'")
            students = cursor.fetchone()['cnt']

            cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'customer_support'")
            cs_count = cursor.fetchone()['cnt']

            cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'administrator'")
            admin_count = cursor.fetchone()['cnt']

            cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'super_admin'")
            sa_count = cursor.fetchone()['cnt']

            cursor.execute("SELECT COUNT(*) as cnt FROM users")
            total_users = cursor.fetchone()['cnt']

            cursor.execute("SELECT COUNT(*) as cnt FROM trouble_tickets")
            total_tickets = cursor.fetchone()['cnt']

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Students", students)
            with col2:
                st.metric("Customer Support", cs_count)
            with col3:
                st.metric("Administrators", admin_count)

            col4, col5, col6 = st.columns(3)
            with col4:
                st.metric("Super Admins", sa_count)
            with col5:
                st.metric("Total Users", total_users)
            with col6:
                st.metric("Total Tickets", total_tickets)

            st.markdown("---")
            st.subheader("Recently Added Employees")
            cursor.execute("""
                SELECT u.user_id, u.first_name, u.last_name,
                       u.email, u.role, u.created_at
                FROM users u
                WHERE u.role IN ('customer_support', 'administrator')
                ORDER BY u.created_at DESC
                LIMIT 5
            """)
            recent_emps = cursor.fetchall()
            if recent_emps:
                for emp in recent_emps:
                    role_icon = "" if emp['role'] == 'customer_support' else ""
                    st.markdown(
                        f"{role_icon} **{emp['first_name']} {emp['last_name']}** — "
                        f"{emp['email']} — "
                        f"{emp['role'].replace('_', ' ').title()} — "
                        f"Added: {emp['created_at'].strftime('%d %b %Y')}"
                    )
            else:
                st.info("No employees added yet.")

            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   ADD EMPLOYEE
    # ══════════════════════════════════════
    elif selected == "Add Employee":
        st.title("Add New Employee")

        role_choice = st.selectbox(
            "Select Employee Role",
            ["customer_support", "administrator"],
            format_func=lambda x: (
                "Customer Support" if x == "customer_support"
                else "Administrator"
            )
        )

        with st.form("add_employee_form", clear_on_submit=False):
            st.markdown("##### Personal Details")
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name *", placeholder="Jane",                key="ae_fn")
                email      = st.text_input("Email *", placeholder="jane@gyanpustak.com",      key="ae_email")
                phone      = st.text_input("Phone", placeholder="+91 XXXXXXXXXX",             key="ae_phone")
                gender     = st.selectbox("Gender", ["Male", "Female", "Other"],              key="ae_gender")
            with col2:
                last_name = st.text_input("Last Name *", placeholder="Smith",                 key="ae_ln")
                password  = st.text_input(
                    "Password *", type="password",
                    placeholder="Min. 6 characters",                                          key="ae_pass"
                )
                salary    = st.number_input(
                    "Salary (₹)",
                    min_value=0.00, step=1000.00,
                    value=0.00, format="%.2f",                                                key="ae_salary"
                )
                aadhaar   = st.text_input(
                    "Aadhaar Number *",
                    placeholder="12 digit Aadhaar",
                    max_chars=12,                                                              key="ae_aadhaar"
                )
            address = st.text_area("Address", placeholder="Full address",                     key="ae_addr")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button(
                    "Add Employee",
                    use_container_width=True,
                    type="primary"
                )

            if submitted:
                if not first_name or not last_name or not email \
                        or not password or not aadhaar:
                    st.error("Please fill all required fields (*)")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif len(aadhaar) != 12 or not aadhaar.isdigit():
                    st.error("Aadhaar must be exactly 12 digits.")
                else:
                    conn = get_connection()
                    if conn:
                        cursor = conn.cursor(dictionary=True)
                        try:
                            if role_choice == 'super_admin':
                                st.error(
                                    "You cannot add another Super Admin. "
                                    "Only 1 Super Admin is allowed."
                                )
                            else:
                                cursor.execute(
                                    "SELECT user_id FROM users WHERE email = %s",
                                    (email,)
                                )
                                if cursor.fetchone():
                                    st.error("Email already registered.")
                                else:
                                    cursor.execute(
                                        "SELECT employee_id FROM employee_details "
                                        "WHERE aadhaar_number = %s",
                                        (aadhaar,)
                                    )
                                    if cursor.fetchone():
                                        st.error("Aadhaar number already registered.")
                                    else:
                                        pw_hash = hash_password(password)
                                        cursor.execute("""
                                            INSERT INTO users
                                                (email, password_hash, role,
                                                 first_name, last_name, phone, address)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                                        """, (
                                            email, pw_hash, role_choice,
                                            first_name, last_name, phone, address
                                        ))
                                        uid = cursor.lastrowid
                                        cursor.execute("""
                                            INSERT INTO employee_details
                                                (employee_id, gender, salary, aadhaar_number)
                                            VALUES (%s, %s, %s, %s)
                                        """, (uid, gender, salary, aadhaar))
                                        conn.commit()
                                        role_label = role_choice.replace('_', ' ').title()
                                        st.session_state['toast_message'] = (
                                            f"Changes Updated! "
                                            f"{role_label} {first_name} {last_name} added!"
                                        )
                                        st.session_state['toast_icon'] = "🎉"
                                        st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Error: {e}")
                        finally:
                            cursor.close()
                            conn.close()

    # ══════════════════════════════════════
    #   MANAGE EMPLOYEES
    # ══════════════════════════════════════
    elif selected == "Manage Employees":
        st.title("Manage Employees")

        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)

            # ── Filters Row ──
            col1, col2 = st.columns(2)
            with col1:
                role_filter = st.selectbox(
                    "Filter by Role",
                    ["All", "customer_support", "administrator"],
                    format_func=lambda x: "All Employees" if x == "All"
                        else ("Customer Support" if x == "customer_support"
                              else "Administrator")
                )
            with col2:
                search = st.text_input(
                    "Search by Name or Email",
                    placeholder="Type name or email..."
                )

            # ── Build Query ──
            query = """
                SELECT u.*, ed.gender, ed.salary, ed.aadhaar_number
                FROM users u
                JOIN employee_details ed ON u.user_id = ed.employee_id
                WHERE u.role IN ('customer_support', 'administrator')
            """
            params = []

            if role_filter != "All":
                query += " AND u.role = %s"
                params.append(role_filter)

            if search:
                query += """ AND (
                    u.first_name LIKE %s OR
                    u.last_name  LIKE %s OR
                    u.email      LIKE %s OR
                    CONCAT(u.first_name, ' ', u.last_name) LIKE %s
                )"""
                params.extend([
                    f"%{search}%",
                    f"%{search}%",
                    f"%{search}%",
                    f"%{search}%"
                ])

            query += " ORDER BY u.first_name"
            cursor.execute(query, params)
            emps = cursor.fetchall()

            if emps:
                st.markdown(f"**Total: {len(emps)} employee(s) found**")
                st.markdown("---")
                for emp in emps:
                    icon       = '' if emp['role'] == 'customer_support' else ''
                    role_label = emp['role'].replace('_', ' ').title()
                    with st.expander(
                        f"{icon} {emp['first_name']} {emp['last_name']} "
                        f"— {role_label} "
                        f"(ID: {emp['user_id']})"
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("Personal Information")
                            st.write(f"**Name:** {emp['first_name']} {emp['last_name']}")
                            st.write(f"**Email:** {emp['email']}")
                            st.write(f"**Phone:** {emp['phone'] or 'N/A'}")
                            st.write(f"**Address:** {emp['address'] or 'N/A'}")
                        with col2:
                            st.subheader("Employment Information")
                            st.write(f"**Role:** {role_label}")
                            st.write(f"**Gender:** {emp['gender'] or 'N/A'}")
                            st.write(f"**Salary:** ₹{emp['salary'] or '0.00'}")
                            st.write(
                                f"**Aadhaar:** "
                                f"XXXX-XXXX-{emp['aadhaar_number'][-4:] if emp['aadhaar_number'] else 'N/A'}"
                            )
                            st.write(f"**Joined:** {emp['created_at'].strftime('%d %b %Y')}")

                        st.markdown("---")

                        # ── Update Salary Form ──
                        st.subheader("Update Salary")
                        with st.form(f"update_salary_{emp['user_id']}"):
                            col_s1, col_s2 = st.columns(2)
                            with col_s1:
                                st.markdown(
                                    f"**Current Salary:** ₹{emp['salary'] or '0.00'}"
                                )
                            with col_s2:
                                new_salary = st.number_input(
                                    "New Salary (₹)",
                                    min_value=0.00,
                                    step=1000.00,
                                    value=float(emp['salary'])
                                          if emp['salary'] else 0.00,
                                    format="%.2f",
                                    key=f"new_sal_{emp['user_id']}"
                                )
                            col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
                            with col_b2:
                                if st.form_submit_button(
                                    "Update Salary",
                                    use_container_width=True,
                                    type="primary"
                                ):
                                    try:
                                        cursor.execute("""
                                            UPDATE employee_details
                                            SET salary = %s
                                            WHERE employee_id = %s
                                        """, (new_salary, emp['user_id']))
                                        conn.commit()
                                        st.session_state['toast_message'] = (
                                            f"Changes Updated! Salary updated for "
                                            f"{emp['first_name']} {emp['last_name']}!"
                                        )
                                        st.session_state['toast_icon'] = "🎉"
                                        st.rerun()
                                    except Exception as e:
                                        conn.rollback()
                                        st.error(f"Error: {e}")

                        st.markdown("")

                        # ── Remove Employee Button ──
                        st.subheader("Remove Employee")
                        st.warning(
                            f"Removing **{emp['first_name']} {emp['last_name']}** "
                            f"will permanently delete their account."
                        )
                        col_a, col_b, col_c = st.columns([2, 1, 2])
                        with col_b:
                            if st.button(
                                "Remove",
                                key=f"rem_emp_{emp['user_id']}",
                                use_container_width=True
                            ):
                                cursor.execute(
                                    "DELETE FROM users WHERE user_id = %s",
                                    (emp['user_id'],)
                                )
                                conn.commit()
                                st.session_state['toast_message'] = (
                                    f"Changes Updated! "
                                    f"{emp['first_name']} {emp['last_name']} removed."
                                )
                                st.session_state['toast_icon'] = "🎉"
                                st.rerun()
            else:
                if search:
                    st.info(
                        f"No employees found matching "
                        f"**'{search}'**."
                    )
                else:
                    st.info("No employees found.")

            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   ALL USERS
    # ══════════════════════════════════════
    elif selected == "All Users":
        st.title("All Registered Users")

        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)

            role_filter = st.selectbox(
                "Filter by Role",
                ["All", "student", "customer_support", "administrator", "super_admin"],
                format_func=lambda x: {
                    "All":              "All Users",
                    "student":          "Students",
                    "customer_support": "Customer Support",
                    "administrator":    "Administrators",
                    "super_admin":      "Super Admins"
                }.get(x, x)
            )

            search = st.text_input(
                "Search by Name or Email",
                placeholder="Type name or email..."
            )

            query = """
                SELECT user_id, first_name, last_name,
                       email, role, phone, address, created_at
                FROM users
                WHERE 1=1
            """
            params = []

            if role_filter != "All":
                query += " AND role = %s"
                params.append(role_filter)

            if search:
                query += """ AND (
                    first_name LIKE %s OR
                    last_name  LIKE %s OR
                    email      LIKE %s OR
                    CONCAT(first_name, ' ', last_name) LIKE %s
                )"""
                params.extend([
                    f"%{search}%",
                    f"%{search}%",
                    f"%{search}%",
                    f"%{search}%"
                ])

            query += " ORDER BY created_at DESC"
            cursor.execute(query, params)
            users = cursor.fetchall()

            if users:
                st.markdown(f"**Total: {len(users)} user(s) found**")
                st.markdown("---")

                role_icons = {
                    "student":          "",
                    "customer_support": "",
                    "administrator":    "",
                    "super_admin":      ""
                }

                for u in users:
                    icon       = role_icons.get(u['role'], '')
                    role_label = u['role'].replace('_', ' ').title()

                    with st.expander(
                        f"{icon} {u['first_name']} {u['last_name']} "
                        f"— {role_label} "
                        f"— {u['email']}"
                    ):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("Personal Information")
                            st.write(f"**Full Name:** {u['first_name']} {u['last_name']}")
                            st.write(f"**Email:** {u['email']}")
                            st.write(f"**Phone:** {u['phone'] or 'N/A'}")
                            st.write(f"**Address:** {u['address'] or 'N/A'}")
                            st.write(f"**Joined:** {u['created_at'].strftime('%d %b %Y %H:%M')}")

                        with col2:
                            if u['role'] == 'student':
                                cursor.execute("""
                                    SELECT * FROM student_details
                                    WHERE student_id = %s
                                """, (u['user_id'],))
                                std = cursor.fetchone()
                                st.subheader("🎓 Academic Information")
                                if std:
                                    st.write(f"**University:** {std['university'] or 'N/A'}")
                                    st.write(f"**Major:** {std['major'] or 'N/A'}")
                                    st.write(f"**Status:** {std['student_status'] or 'N/A'}")
                                    st.write(f"**Year:** {std['year_of_study'] or 'N/A'}")
                                    st.write(f"**DOB:** {std['date_of_birth'] or 'N/A'}")
                                else:
                                    st.info("No academic details found.")

                            elif u['role'] in ('customer_support', 'administrator', 'super_admin'):
                                cursor.execute("""
                                    SELECT * FROM employee_details
                                    WHERE employee_id = %s
                                """, (u['user_id'],))
                                emp = cursor.fetchone()
                                st.subheader("Employment Information")
                                if emp:
                                    st.write(f"**Role:** {role_label}")
                                    st.write(f"**Gender:** {emp['gender'] or 'N/A'}")
                                    st.write(f"**Salary:** ₹{emp['salary'] or '0.00'}")
                                    st.write(
                                        f"**Aadhaar:** "
                                        f"XXXX-XXXX-"
                                        f"{emp['aadhaar_number'][-4:] if emp['aadhaar_number'] else 'N/A'}"
                                    )
                                    st.write(f"**Employee ID:** {emp['employee_id']}")
                                else:
                                    st.info("No employment details found.")

                        # ── Student Activity Stats ──
                        if u['role'] == 'student':
                            st.markdown("---")
                            st.subheader("Student Activity")

                            cursor.execute("""
                                SELECT COUNT(*) as cnt FROM orders
                                WHERE student_id = %s
                            """, (u['user_id'],))
                            order_count = cursor.fetchone()['cnt']

                            cursor.execute("""
                                SELECT COUNT(*) as cnt FROM reviews
                                WHERE student_id = %s
                            """, (u['user_id'],))
                            review_count = cursor.fetchone()['cnt']

                            cursor.execute("""
                                SELECT COUNT(*) as cnt FROM trouble_tickets
                                WHERE created_by = %s
                            """, (u['user_id'],))
                            ticket_count = cursor.fetchone()['cnt']

                            cursor.execute("""
                                SELECT COUNT(*) as cnt FROM cart_items ci
                                JOIN carts c ON ci.cart_id = c.cart_id
                                WHERE c.student_id = %s
                            """, (u['user_id'],))
                            cart_count = cursor.fetchone()['cnt']

                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Orders", order_count)
                            with col2:
                                st.metric("Reviews", review_count)
                            with col3:
                                st.metric("Tickets", ticket_count)
                            with col4:
                                st.metric("Cart Items", cart_count)

                        # ── Employee Activity Stats ──
                        elif u['role'] in ('customer_support', 'administrator'):
                            st.markdown("---")
                            st.subheader("Employee Activity")

                            cursor.execute("""
                                SELECT COUNT(*) as cnt FROM trouble_tickets
                                WHERE created_by = %s
                            """, (u['user_id'],))
                            created_tickets = cursor.fetchone()['cnt']

                            cursor.execute("""
                                SELECT COUNT(*) as cnt FROM trouble_tickets
                                WHERE assigned_admin = %s
                            """, (u['user_id'],))
                            assigned_tickets = cursor.fetchone()['cnt']

                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Tickets Created", created_tickets)
                            with col2:
                                st.metric("Tickets Resolved", assigned_tickets)

            else:
                if search:
                    st.info(
                        f"No users found matching **'{search}'**."
                    )
                else:
                    st.info("No users found.")

            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   PROFILE
    # ══════════════════════════════════════
    elif selected == "Profile":
        st.title("Super Admin Profile")

        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM users WHERE user_id = %s",
                (user['user_id'],)
            )
            fresh_user = cursor.fetchone()

            cursor.execute(
                "SELECT * FROM employee_details WHERE employee_id = %s",
                (fresh_user['user_id'],)
            )
            emp_details = cursor.fetchone()

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Personal Information")
                st.write(f"**Full Name:** {fresh_user['first_name']} {fresh_user['last_name']}")
                st.write(f"**Email:** {fresh_user['email']}")
                st.write(f"**Phone:** {fresh_user['phone'] or 'N/A'}")
                st.write(f"**Address:** {fresh_user['address'] or 'N/A'}")
                st.write(f"**Role:** {fresh_user['role'].replace('_', ' ').title()}")
                st.write(f"**Joined:** {fresh_user['created_at'].strftime('%d %b %Y')}")

            with col2:
                st.subheader("Employment Information")
                if emp_details:
                    st.write(f"**Gender:** {emp_details['gender'] or 'N/A'}")
                    st.write(f"**Salary:** ₹{emp_details['salary'] or '0.00'}")
                    st.write(
                        f"**Aadhaar:** "
                        f"XXXX-XXXX-"
                        f"{emp_details['aadhaar_number'][-4:] if emp_details['aadhaar_number'] else 'N/A'}"
                    )
                    st.write(f"**Employee ID:** {emp_details['employee_id']}")

            st.markdown("---")

            tab1, tab2 = st.tabs([
                "Change My Profile",
                "Update Employee Salaries"
            ])

            # ──────────────────────────────────────
            #   TAB 1: CHANGE OWN PROFILE
            # ──────────────────────────────────────
            with tab1:
                st.subheader("Update My Profile")

                with st.form("sa_change_profile", clear_on_submit=False):
                    st.markdown("##### Personal Details")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_first = st.text_input(
                            "First Name *",
                            value=fresh_user['first_name'],
                            key="sa_cp_fn"
                        )
                        new_email = st.text_input(
                            "Email *",
                            value=fresh_user['email'],
                            key="sa_cp_email"
                        )
                        new_phone = st.text_input(
                            "Phone",
                            value=fresh_user['phone'] or "",
                            key="sa_cp_phone"
                        )
                    with col2:
                        new_last = st.text_input(
                            "Last Name *",
                            value=fresh_user['last_name'],
                            key="sa_cp_ln"
                        )
                        new_password = st.text_input(
                            "New Password (leave blank to keep current)",
                            type="password",
                            placeholder="Enter new password",
                            key="sa_cp_pass"
                        )
                        confirm_password = st.text_input(
                            "Confirm New Password",
                            type="password",
                            placeholder="Confirm new password",
                            key="sa_cp_confirm"
                        )
                    new_address = st.text_area(
                        "Address",
                        value=fresh_user['address'] or "",
                        key="sa_cp_addr"
                    )

                    st.markdown("##### Employment Details")
                    col3, col4 = st.columns(2)
                    with col3:
                        gender_options = ["Male", "Female", "Other"]
                        current_gender = (
                            emp_details['gender']
                            if emp_details and emp_details['gender']
                            else "Male"
                        )
                        new_gender = st.selectbox(
                            "Gender",
                            gender_options,
                            index=gender_options.index(current_gender),
                            key="sa_cp_gender"
                        )
                        new_salary = st.number_input(
                            "Salary (₹)",
                            min_value=0.00,
                            step=1000.00,
                            value=float(emp_details['salary'])
                                  if emp_details and emp_details['salary'] else 0.00,
                            format="%.2f",
                            key="sa_cp_salary"
                        )
                    with col4:
                        new_aadhaar = st.text_input(
                            "Aadhaar Number *",
                            value=emp_details['aadhaar_number']
                                  if emp_details else "",
                            max_chars=12,
                            key="sa_cp_aadhaar"
                        )

                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        submitted = st.form_submit_button(
                            "Save My Profile",
                            use_container_width=True,
                            type="primary"
                        )

                    if submitted:
                        if not new_first or not new_last or not new_email:
                            st.error("First name, last name and email are required.")
                        elif new_password and new_password != confirm_password:
                            st.error("Passwords do not match.")
                        elif new_password and len(new_password) < 6:
                            st.error("Password must be at least 6 characters.")
                        elif not new_aadhaar or len(new_aadhaar) != 12 or not new_aadhaar.isdigit():
                            st.error("Aadhaar must be exactly 12 digits.")
                        else:
                            try:
                                cursor.execute("""
                                    SELECT user_id FROM users
                                    WHERE email = %s AND user_id != %s
                                """, (new_email, fresh_user['user_id']))
                                if cursor.fetchone():
                                    st.error("This email is already used by another account.")
                                else:
                                    cursor.execute("""
                                        SELECT employee_id FROM employee_details
                                        WHERE aadhaar_number = %s AND employee_id != %s
                                    """, (new_aadhaar, fresh_user['user_id']))
                                    if cursor.fetchone():
                                        st.error("This Aadhaar is already used by another account.")
                                    else:
                                        if new_password:
                                            import bcrypt
                                            pw_hash = bcrypt.hashpw(
                                                new_password.encode('utf-8'),
                                                bcrypt.gensalt()
                                            ).decode('utf-8')
                                            cursor.execute("""
                                                UPDATE users
                                                SET first_name    = %s,
                                                    last_name     = %s,
                                                    email         = %s,
                                                    phone         = %s,
                                                    address       = %s,
                                                    password_hash = %s
                                                WHERE user_id = %s
                                            """, (
                                                new_first, new_last, new_email,
                                                new_phone, new_address, pw_hash,
                                                fresh_user['user_id']
                                            ))
                                        else:
                                            cursor.execute("""
                                                UPDATE users
                                                SET first_name = %s,
                                                    last_name  = %s,
                                                    email      = %s,
                                                    phone      = %s,
                                                    address    = %s
                                                WHERE user_id = %s
                                            """, (
                                                new_first, new_last, new_email,
                                                new_phone, new_address,
                                                fresh_user['user_id']
                                            ))

                                        cursor.execute("""
                                            UPDATE employee_details
                                            SET gender         = %s,
                                                salary         = %s,
                                                aadhaar_number = %s
                                            WHERE employee_id = %s
                                        """, (
                                            new_gender, new_salary,
                                            new_aadhaar, fresh_user['user_id']
                                        ))

                                        conn.commit()

                                        st.session_state['user']['first_name'] = new_first
                                        st.session_state['user']['last_name']  = new_last
                                        st.session_state['user']['email']      = new_email
                                        st.session_state['user']['phone']      = new_phone
                                        st.session_state['user']['address']    = new_address

                                        st.session_state['toast_message'] = "Changes Updated!"
                                        st.session_state['toast_icon']    = "🎉"
                                        st.rerun()

                            except Exception as e:
                                conn.rollback()
                                st.error(f"Error: {e}")

            # ──────────────────────────────────────
            #   TAB 2: UPDATE EMPLOYEE SALARIES
            # ──────────────────────────────────────
            with tab2:
                st.subheader("Update Employee Salaries")

                cursor.execute("""
                    SELECT u.user_id, u.first_name, u.last_name,
                           u.email, u.role, ed.salary, ed.gender
                    FROM users u
                    JOIN employee_details ed ON u.user_id = ed.employee_id
                    WHERE u.role IN ('customer_support', 'administrator')
                    ORDER BY u.role, u.first_name
                """)
                employees = cursor.fetchall()

                if employees:
                    st.markdown(f"**Total Employees: {len(employees)}**")
                    st.markdown("---")

                    for emp in employees:
                        role_icon  = "" if emp['role'] == 'customer_support' else ""
                        role_label = emp['role'].replace('_', ' ').title()

                        with st.expander(
                            f"{role_icon} {emp['first_name']} {emp['last_name']} "
                            f"— {role_label} "
                            f"— Current Salary: ₹{emp['salary'] or '0.00'}"
                        ):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Name:** {emp['first_name']} {emp['last_name']}")
                                st.write(f"**Email:** {emp['email']}")
                            with col2:
                                st.write(f"**Role:** {role_label}")
                                st.write(f"**Current Salary:** ₹{emp['salary'] or '0.00'}")

                            with st.form(f"salary_form_{emp['user_id']}"):
                                new_emp_salary = st.number_input(
                                    "New Salary (₹)",
                                    min_value=0.00,
                                    step=1000.00,
                                    value=float(emp['salary']) if emp['salary'] else 0.00,
                                    format="%.2f",
                                    key=f"sal_{emp['user_id']}"
                                )
                                col1, col2, col3 = st.columns([1, 2, 1])
                                with col2:
                                    if st.form_submit_button(
                                        "Update Salary",
                                        use_container_width=True,
                                        type="primary"
                                    ):
                                        try:
                                            cursor.execute("""
                                                UPDATE employee_details
                                                SET salary = %s
                                                WHERE employee_id = %s
                                            """, (new_emp_salary, emp['user_id']))
                                            conn.commit()
                                            st.session_state['toast_message'] = (
                                                f"Changes Updated! Salary updated for "
                                                f"{emp['first_name']} {emp['last_name']}!"
                                            )
                                            st.session_state['toast_icon'] = "🎉"
                                            st.rerun()
                                        except Exception as e:
                                            conn.rollback()
                                            st.error(f"Error: {e}")
                else:
                    st.info(
                        "No employees found. "
                        "Add employees from the 'Add Employee' section."
                    )

            cursor.close()
            conn.close()

    show_footer()
