import streamlit as st
from streamlit_option_menu import option_menu
from database import get_connection
from student import show_footer

# ── Logout helper ──
def logout():
    try:
        st.query_params.clear()
    except Exception:
        pass
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

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

def show_cs_dashboard():
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
                background:linear-gradient(135deg,#E67E22,#D35400);
                display:flex; align-items:center; justify-content:center;
                margin:0 auto; font-size:32px; color:white; font-weight:700;
                box-shadow: 0 4px 12px rgba(230,126,34,0.4);
            ">
                {user['first_name'][0].upper()}
            </div>
            <h3 style="margin-top:10px; margin-bottom:2px; color:#2C3E50; font-size:16px;">
                {user['first_name']} {user['last_name']}
            </h3>
            <p style="color:#7F8C8D; font-size:12px; margin:0;">🛠️ Customer Support</p>
        </div>
        <hr style="border:none; border-top:1px solid #E5E7E9; margin:10px 0;">
        """, unsafe_allow_html=True)

        selected = option_menu(
            menu_title=None,
            options=[
                "Dashboard", "Trouble Tickets", "Create Ticket",
                "Manage Orders", "Profile", "Logout"
            ],
            icons=[
                "speedometer2", "ticket-detailed", "plus-circle",
                "bag", "person-circle", "box-arrow-right"
            ],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {"padding": "0px", "background-color": "transparent"},
                "icon": {"color": "#E67E22", "font-size": "17px"},
                "nav-link": {
                    "font-size": "14px", "text-align": "left",
                    "margin": "3px 0", "padding": "10px 15px",
                    "border-radius": "8px", "color": "#2C3E50", "font-weight": "500",
                },
                "nav-link-selected": {
                    "background-color": "#E67E22", "color": "white", "font-weight": "700",
                },
            }
        )

    # ══════════════════════════════════════
    #   LOGOUT
    # ══════════════════════════════════════
    if selected == "Logout":
        logout()

    # ══════════════════════════════════════
    #   DASHBOARD
    # ══════════════════════════════════════
    elif selected == "Dashboard":
        st.title("🛠️ Customer Support Dashboard")
        st.markdown(f"### Welcome, **{user['first_name']}**! 👋")

        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT COUNT(*) as cnt FROM trouble_tickets "
                "WHERE ticket_status = 'new'"
            )
            new_tickets = cursor.fetchone()['cnt']

            cursor.execute(
                "SELECT COUNT(*) as cnt FROM trouble_tickets "
                "WHERE ticket_status = 'assigned'"
            )
            assigned_tickets = cursor.fetchone()['cnt']

            cursor.execute(
                "SELECT COUNT(*) as cnt FROM trouble_tickets "
                "WHERE ticket_status = 'in-process'"
            )
            ip_tickets = cursor.fetchone()['cnt']

            cursor.execute(
                "SELECT COUNT(*) as cnt FROM trouble_tickets "
                "WHERE ticket_status = 'completed'"
            )
            comp_tickets = cursor.fetchone()['cnt']

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🟢 New Tickets", new_tickets)
            with col2:
                st.metric("🔵 Assigned", assigned_tickets)
            with col3:
                st.metric("🟡 In Process", ip_tickets)
            with col4:
                st.metric("✅ Completed", comp_tickets)

            st.markdown("---")

            # ── Administrator Workload Overview ──
            st.subheader("⚙️ Administrator Workload Overview")
            cursor.execute("""
                SELECT
                    u.user_id,
                    u.first_name,
                    u.last_name,
                    COUNT(CASE WHEN tt.ticket_status = 'assigned'
                               THEN 1 END) as assigned_count,
                    COUNT(CASE WHEN tt.ticket_status = 'in-process'
                               THEN 1 END) as inprocess_count,
                    COUNT(CASE WHEN tt.ticket_status = 'completed'
                               THEN 1 END) as completed_count,
                    COUNT(tt.ticket_id) as total_count
                FROM users u
                LEFT JOIN trouble_tickets tt
                    ON tt.assigned_admin = u.user_id
                WHERE u.role = 'administrator'
                GROUP BY u.user_id, u.first_name, u.last_name
                ORDER BY total_count DESC
            """)
            admins = cursor.fetchall()

            if admins:
                cols_per_row = 3
                for row_start in range(0, len(admins), cols_per_row):
                    row_admins = admins[row_start: row_start + cols_per_row]
                    cols = st.columns(cols_per_row)
                    for idx, adm in enumerate(row_admins):
                        with cols[idx]:
                            active = (
                                adm['assigned_count'] +
                                adm['inprocess_count']
                            )
                            if active == 0:
                                badge_color = "#27AE60"
                                badge_label = "Free"
                            elif active <= 2:
                                badge_color = "#F39C12"
                                badge_label = "Busy"
                            else:
                                badge_color = "#E74C3C"
                                badge_label = "Overloaded"

                            st.markdown(f"""
                            <div style="background:white; border:1px solid #E5E7E9;
                                        border-radius:10px; padding:12px;
                                        text-align:center;
                                        box-shadow:0 2px 6px rgba(0,0,0,0.06);
                                        margin-bottom:10px;">
                                <div style="width:40px; height:40px; border-radius:50%;
                                            background:linear-gradient(135deg,#8E44AD,#6C3483);
                                            display:flex; align-items:center;
                                            justify-content:center;
                                            margin:0 auto 8px auto;
                                            font-size:18px; color:white; font-weight:700;">
                                    {adm['first_name'][0].upper()}
                                </div>
                                <p style="margin:0; font-size:13px; font-weight:700;
                                           color:#2C3E50;">
                                    {adm['first_name']} {adm['last_name']}
                                </p>
                                <p style="margin:4px 0 2px 0; font-size:11px;
                                           color:#7F8C8D;">
                                    🔵 Assigned: <strong>{adm['assigned_count']}</strong>
                                </p>
                                <p style="margin:2px 0; font-size:11px;
                                           color:#7F8C8D;">
                                    🟡 In-Process: <strong>{adm['inprocess_count']}</strong>
                                </p>
                                <p style="margin:2px 0; font-size:11px;
                                           color:#7F8C8D;">
                                    ✅ Completed: <strong>{adm['completed_count']}</strong>
                                </p>
                                <span style="display:inline-block; margin-top:6px;
                                             background:{badge_color}; color:white;
                                             font-size:11px; font-weight:600;
                                             padding:2px 10px; border-radius:12px;">
                                    {badge_label}
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("No administrators found.")

            st.markdown("---")
            st.subheader("🟢 Recent New Tickets")
            cursor.execute("""
                SELECT tt.*, u.first_name, u.last_name
                FROM trouble_tickets tt
                LEFT JOIN users u ON tt.created_by = u.user_id
                WHERE tt.ticket_status = 'new'
                ORDER BY tt.date_logged DESC LIMIT 5
            """)
            tickets = cursor.fetchall()
            if tickets:
                for t in tickets:
                    st.markdown(
                        f"**#{t['ticket_id']}** — {t['title']} — "
                        f"by {t['first_name']} {t['last_name']} — "
                        f"{t['date_logged'].strftime('%d %b %Y')}"
                    )
            else:
                st.info("No new tickets.")

            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   TROUBLE TICKETS
    # ══════════════════════════════════════
    elif selected == "Trouble Tickets":
        st.title("🎫 Trouble Tickets")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)

            # ── Fetch all administrators with ticket counts ──
            cursor.execute("""
                SELECT
                    u.user_id,
                    u.first_name,
                    u.last_name,
                    COUNT(CASE WHEN tt.ticket_status IN ('assigned','in-process')
                               THEN 1 END) as active_tickets,
                    COUNT(CASE WHEN tt.ticket_status = 'completed'
                               THEN 1 END) as completed_tickets,
                    COUNT(tt.ticket_id) as total_tickets
                FROM users u
                LEFT JOIN trouble_tickets tt
                    ON tt.assigned_admin = u.user_id
                WHERE u.role = 'administrator'
                GROUP BY u.user_id, u.first_name, u.last_name
                ORDER BY u.first_name
            """)
            admins = cursor.fetchall()
            admin_count = len(admins)

            # ── Show Admin Workload Panel ──
            if admins:
                st.subheader("⚙️ Administrator Workload")
                st.info(
                    "ℹ️ Below shows how many tickets each administrator "
                    "is currently handling. Use this to decide "
                    "who to assign tickets to."
                )

                # ── Always 3 per row ──
                cols_per_row = 3
                for row_start in range(0, len(admins), cols_per_row):
                    row_admins = admins[row_start: row_start + cols_per_row]
                    cols = st.columns(cols_per_row)
                    for idx, adm in enumerate(row_admins):
                        with cols[idx]:
                            active = adm['active_tickets']
                            if active == 0:
                                badge_color = "#27AE60"
                                badge_label = "Free"
                            elif active <= 2:
                                badge_color = "#F39C12"
                                badge_label = "Busy"
                            else:
                                badge_color = "#E74C3C"
                                badge_label = "Overloaded"

                            st.markdown(f"""
                            <div style="background:white; border:1px solid #E5E7E9;
                                        border-radius:10px; padding:12px;
                                        text-align:center;
                                        box-shadow:0 2px 6px rgba(0,0,0,0.06);
                                        margin-bottom:10px;">
                                <div style="width:40px; height:40px; border-radius:50%;
                                            background:linear-gradient(135deg,#8E44AD,#6C3483);
                                            display:flex; align-items:center;
                                            justify-content:center;
                                            margin:0 auto 8px auto;
                                            font-size:18px; color:white; font-weight:700;">
                                    {adm['first_name'][0].upper()}
                                </div>
                                <p style="margin:0; font-size:13px; font-weight:700;
                                           color:#2C3E50;">
                                    {adm['first_name']} {adm['last_name']}
                                </p>
                                <p style="margin:4px 0 0 0; font-size:11px;
                                           color:#7F8C8D;">
                                    🔵 Active: <strong>{adm['active_tickets']}</strong> |
                                    ✅ Done: <strong>{adm['completed_tickets']}</strong>
                                </p>
                                <span style="display:inline-block; margin-top:6px;
                                             background:{badge_color}; color:white;
                                             font-size:11px; font-weight:600;
                                             padding:2px 10px; border-radius:12px;">
                                    {badge_label}
                                </span>
                            </div>
                            """, unsafe_allow_html=True)

                st.markdown("---")

            # ── Filter ──
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "new", "assigned", "in-process", "completed"]
            )

            query = """
                SELECT tt.*, u.first_name as creator_fn,
                       u.last_name as creator_ln,
                       a.first_name as admin_fn,
                       a.last_name as admin_ln
                FROM trouble_tickets tt
                LEFT JOIN users u ON tt.created_by = u.user_id
                LEFT JOIN users a ON tt.assigned_admin = a.user_id
            """
            params = []
            if status_filter != "All":
                query += " WHERE tt.ticket_status = %s"
                params.append(status_filter)
            query += " ORDER BY tt.date_logged DESC"
            cursor.execute(query, params)
            tickets = cursor.fetchall()

            if tickets:
                for t in tickets:
                    status_icons = {
                        "new": "🟢", "assigned": "🔵",
                        "in-process": "🟡", "completed": "✅"
                    }
                    with st.expander(
                        f"#{t['ticket_id']} — {t['title']} — "
                        f"{status_icons.get(t['ticket_status'], '⚪')} "
                        f"{t['ticket_status'].upper()}"
                    ):
                        st.write(f"**Category:** {t['category']}")
                        st.write(
                            f"**Created By:** {t['creator_fn']} "
                            f"{t['creator_ln']} "
                            f"({t['created_by_role']})"
                        )
                        st.write(f"**Problem:** {t['problem_description']}")
                        if t['solution_description']:
                            st.success(
                                f"**Solution:** {t['solution_description']}"
                            )
                        st.write(
                            f"**Date Logged:** "
                            f"{t['date_logged'].strftime('%d %b %Y %H:%M')}"
                        )
                        if t['admin_fn']:
                            st.write(
                                f"**Assigned Admin:** "
                                f"{t['admin_fn']} {t['admin_ln']}"
                            )

                        # ── CS can only modify 'new' tickets ──
                        if t['ticket_status'] == 'new':
                            st.markdown("---")

                            if admin_count > 0:
                                st.markdown(
                                    "**Assign to Administrator:**"
                                )

                                # ── Build admin options with workload info ──
                                admin_options = {}
                                for adm in admins:
                                    active = adm['active_tickets']
                                    if active == 0:
                                        status_txt = "🟢 Free"
                                    elif active <= 2:
                                        status_txt = "🟡 Busy"
                                    else:
                                        status_txt = "🔴 Overloaded"
                                    label = (
                                        f"{adm['first_name']} "
                                        f"{adm['last_name']} — "
                                        f"Active: {adm['active_tickets']} | "
                                        f"Completed: {adm['completed_tickets']} | "
                                        f"{status_txt}"
                                    )
                                    admin_options[label] = adm['user_id']

                                selected_admin_label = st.selectbox(
                                    "Select Administrator",
                                    list(admin_options.keys()),
                                    key=f"select_admin_{t['ticket_id']}"
                                )

                                if st.button(
                                    f"Assign Ticket #{t['ticket_id']}",
                                    key=f"btn_assign_{t['ticket_id']}",
                                    type="primary",
                                    use_container_width=True
                                ):
                                    selected_admin_id = (
                                        admin_options[selected_admin_label]
                                    )
                                    cursor.execute("""
                                        UPDATE trouble_tickets
                                        SET ticket_status  = 'assigned',
                                            assigned_admin = %s
                                        WHERE ticket_id = %s
                                    """, (selected_admin_id, t['ticket_id']))
                                    cursor.execute("""
                                        INSERT INTO ticket_status_history
                                            (ticket_id, old_status,
                                             new_status, changed_by)
                                        VALUES (%s, 'new', 'assigned', %s)
                                    """, (t['ticket_id'], user['user_id']))
                                    conn.commit()
                                    selected_admin_name = (
                                        selected_admin_label.split(" — ")[0]
                                    )
                                    st.session_state['toast_message'] = (
                                        f"✅ Changes Updated! "
                                        f"Ticket #{t['ticket_id']} assigned "
                                        f"to {selected_admin_name}!"
                                    )
                                    st.session_state['toast_icon'] = "🎉"
                                    st.rerun()

                            else:
                                st.warning(
                                    "⚠️ No administrators available to assign. "
                                    "Please contact the Super Admin to "
                                    "add administrators."
                                )
            else:
                st.info("No tickets found.")

            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   CREATE TICKET
    # ══════════════════════════════════════
    elif selected == "Create Ticket":
        st.title("Create Trouble Ticket")
        st.info(
            "Customer support can create tickets "
            "for technical issues or complaints."
        )
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            with st.form("cs_create_ticket"):
                t_cat   = st.selectbox(
                    "Category",
                    ["user_profile", "products", "cart", "orders", "other"]
                )
                t_title = st.text_input("Title *")
                t_desc  = st.text_area("Problem Description *")
                if st.form_submit_button(
                    "Create Ticket",
                    use_container_width=True,
                    type="primary"
                ):
                    if not t_title or not t_desc:
                        st.error("Please fill all fields")
                    else:
                        cursor.execute("""
                            INSERT INTO trouble_tickets
                                (category, title, problem_description,
                                 ticket_status, created_by, created_by_role)
                            VALUES (%s, %s, %s, 'new', %s, 'customer_support')
                        """, (t_cat, t_title, t_desc, user['user_id']))
                        conn.commit()
                        st.session_state['toast_message'] = (
                            "✅ Changes Updated! Ticket created successfully!"
                        )
                        st.session_state['toast_icon'] = "🎉"
                        st.rerun()
            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   MANAGE ORDERS
    # ══════════════════════════════════════
    elif selected == "Manage Orders":
        st.title("Manage Orders (Cancel)")
        st.info(
            "You can cancel orders upon student request. "
            "Returns are not supported."
        )
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT o.*, u.first_name, u.last_name, u.email
                FROM orders o
                JOIN users u ON o.student_id = u.user_id
                ORDER BY o.date_created DESC
            """)
            orders = cursor.fetchall()
            if orders:
                for order in orders:
                    status_icons = {
                        "new": "🟢", "processed": "🔵",
                        "awaiting_shipping": "🟡",
                        "shipped": "✅", "canceled": "🔴"
                    }
                    with st.expander(
                        f"Order #{order['order_id']} — "
                        f"{order['first_name']} {order['last_name']} — "
                        f"{status_icons.get(order['order_status'], '⚪')} "
                        f"{order['order_status']}"
                    ):
                        st.write(
                            f"**Student:** {order['first_name']} "
                            f"{order['last_name']} ({order['email']})"
                        )
                        st.write(f"**Amount:** ₹{order['total_amount']}")
                        st.write(f"**Status:** {order['order_status']}")
                        st.write(f"**Shipping:** {order['shipping_type']}")

                        cursor.execute("""
                            SELECT oi.*, b.title FROM order_items oi
                            JOIN books b ON oi.book_id = b.book_id
                            WHERE oi.order_id = %s
                        """, (order['order_id'],))
                        items = cursor.fetchall()
                        for it in items:
                            st.write(
                                f"📖 {it['title']} — "
                                f"Qty: {it['quantity']} — "
                                f"₹{it['price']} ({it['purchase_option']})"
                            )

                        if order['order_status'] not in ('canceled', 'shipped'):
                            if st.button(
                                f"❌ Cancel Order #{order['order_id']}",
                                key=f"cs_cancel_{order['order_id']}"
                            ):
                                cursor.execute(
                                    "UPDATE orders SET order_status = 'canceled' "
                                    "WHERE order_id = %s",
                                    (order['order_id'],)
                                )
                                for it in items:
                                    cursor.execute(
                                        "UPDATE books SET quantity = quantity + %s "
                                        "WHERE book_id = %s",
                                        (it['quantity'], it['book_id'])
                                    )
                                conn.commit()
                                st.session_state['toast_message'] = (
                                    f"✅ Changes Updated! "
                                    f"Order #{order['order_id']} "
                                    f"canceled successfully."
                                )
                                st.session_state['toast_icon'] = "🎉"
                                st.rerun()
            else:
                st.info("No orders found.")

            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   PROFILE
    # ══════════════════════════════════════
    elif selected == "Profile":
        show_cs_profile(user)

    show_footer()


# ══════════════════════════════════════
#   CS PROFILE (no salary field)
# ══════════════════════════════════════
def show_cs_profile(user):
    st.title("My Profile")

    conn = get_connection()
    if not conn:
        st.error("Database connection failed.")
        return

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
    emp = cursor.fetchone()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👤 Personal Information")
        st.write(
            f"**Name:** "
            f"{fresh_user['first_name']} {fresh_user['last_name']}"
        )
        st.write(f"**Email:** {fresh_user['email']}")
        st.write(f"**Phone:** {fresh_user['phone'] or 'N/A'}")
        st.write(f"**Address:** {fresh_user['address'] or 'N/A'}")
        st.write(
            f"**Role:** "
            f"{fresh_user['role'].replace('_', ' ').title()}"
        )
        st.write(
            f"**Joined:** "
            f"{fresh_user['created_at'].strftime('%d %b %Y')}"
        )
    with col2:
        st.subheader("💼 Employment Information")
        if emp:
            st.write(f"**Gender:** {emp['gender'] or 'N/A'}")
            st.write(f"**Salary:** ₹{emp['salary'] or '0.00'}")
            st.write(
                f"**Aadhaar:** XXXX-XXXX-"
                f"{emp['aadhaar_number'][-4:] if emp['aadhaar_number'] else 'N/A'}"
            )
            st.write(f"**Employee ID:** {emp['employee_id']}")
        else:
            st.info("No employment details found.")

    st.markdown("---")
    st.subheader("✏️ Change Profile")

    with st.form("cs_change_profile_form", clear_on_submit=False):

        st.markdown("##### Personal Details")
        col1, col2 = st.columns(2)
        with col1:
            new_first = st.text_input(
                "First Name *",
                value=fresh_user['first_name'],
                key="cs_cp_fn"
            )
            new_email = st.text_input(
                "Email *",
                value=fresh_user['email'],
                key="cs_cp_email"
            )
            new_phone = st.text_input(
                "Phone",
                value=fresh_user['phone'] or "",
                key="cs_cp_phone"
            )
        with col2:
            new_last = st.text_input(
                "Last Name *",
                value=fresh_user['last_name'],
                key="cs_cp_ln"
            )
            new_password = st.text_input(
                "New Password (leave blank to keep current)",
                type="password",
                placeholder="Enter new password",
                key="cs_cp_pass"
            )
            confirm_password = st.text_input(
                "Confirm New Password",
                type="password",
                placeholder="Confirm new password",
                key="cs_cp_confirm"
            )
        new_address = st.text_area(
            "Address",
            value=fresh_user['address'] or "",
            key="cs_cp_addr"
        )

        st.markdown("##### Employment Details")
        col3, col4 = st.columns(2)
        with col3:
            gender_options = ["Male", "Female", "Other"]
            current_gender = (
                emp['gender'] if emp and emp['gender'] else "Male"
            )
            new_gender = st.selectbox(
                "Gender",
                gender_options,
                index=gender_options.index(current_gender),
                key="cs_cp_gender"
            )
        with col4:
            new_aadhaar = st.text_input(
                "Aadhaar Number *",
                value=emp['aadhaar_number']
                      if emp and emp['aadhaar_number'] else "",
                max_chars=12,
                key="cs_cp_aadhaar"
            )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "Save Changes",
                use_container_width=True,
                type="primary"
            )

        if submitted:
            if not new_first or not new_last or not new_email:
                st.error("⚠️ First name, last name and email are required.")
            elif new_password and new_password != confirm_password:
                st.error("⚠️ Passwords do not match.")
            elif new_password and len(new_password) < 6:
                st.error("⚠️ Password must be at least 6 characters.")
            elif not new_aadhaar or len(new_aadhaar) != 12 \
                    or not new_aadhaar.isdigit():
                st.error("⚠️ Aadhaar must be exactly 12 digits.")
            else:
                try:
                    cursor.execute(
                        "SELECT user_id FROM users "
                        "WHERE email = %s AND user_id != %s",
                        (new_email, fresh_user['user_id'])
                    )
                    if cursor.fetchone():
                        st.error(
                            "❌ This email is already used by another account."
                        )
                    else:
                        cursor.execute("""
                            SELECT employee_id FROM employee_details
                            WHERE aadhaar_number = %s
                              AND employee_id != %s
                        """, (new_aadhaar, fresh_user['user_id']))
                        if cursor.fetchone():
                            st.error(
                                "❌ This Aadhaar is already used "
                                "by another account."
                            )
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
                                    aadhaar_number = %s
                                WHERE employee_id = %s
                            """, (
                                new_gender,
                                new_aadhaar,
                                fresh_user['user_id']
                            ))

                            conn.commit()

                            st.session_state['user']['first_name'] = new_first
                            st.session_state['user']['last_name']  = new_last
                            st.session_state['user']['email']      = new_email
                            st.session_state['user']['phone']      = new_phone
                            st.session_state['user']['address']    = new_address

                            st.session_state['toast_message'] = "✅ Changes Updated!"
                            st.session_state['toast_icon']    = "🎉"
                            st.rerun()

                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Error updating profile: {e}")

    cursor.close()
    conn.close()