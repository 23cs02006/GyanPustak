import streamlit as st
from streamlit_option_menu import option_menu
from database import get_connection
from student import show_profile, show_footer 
from datetime import date

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

def show_admin_dashboard():
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
                background:linear-gradient(135deg,#8E44AD,#6C3483);
                display:flex; align-items:center; justify-content:center;
                margin:0 auto; font-size:32px; color:white; font-weight:700;
                box-shadow: 0 4px 12px rgba(142,68,173,0.4);
            ">
                {user['first_name'][0].upper()}
            </div>
            <h3 style="margin-top:10px; margin-bottom:2px;
                       color:#2C3E50; font-size:16px;">
                {user['first_name']} {user['last_name']}
            </h3>
            <p style="color:#7F8C8D; font-size:12px; margin:0;">
                Administrator
            </p>
        </div>
        <hr style="border:none; border-top:1px solid #E5E7E9; margin:10px 0;">
        """, unsafe_allow_html=True)

        selected = option_menu(
            menu_title=None,
            options=[
                "Dashboard", "Manage Books", "Manage Categories",
                "Manage Universities", "Manage Departments",
                "Manage Instructors", "Manage Courses",
                "Trouble Tickets", "Manage Orders",
                "View Reviews", "Profile", "Logout"
            ],
            icons=[
                "speedometer2", "book", "tags", "building", "diagram-3",
                "person-badge", "journal-bookmark", "ticket-detailed",
                "bag", "star", "person-circle", "box-arrow-right"
            ],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {"padding": "0px", "background-color": "transparent"},
                "icon": {"color": "#8E44AD", "font-size": "17px"},
                "nav-link": {
                    "font-size": "14px", "text-align": "left",
                    "margin": "3px 0", "padding": "10px 15px",
                    "border-radius": "8px", "color": "#2C3E50",
                    "font-weight": "500",
                },
                "nav-link-selected": {
                    "background-color": "#8E44AD",
                    "color": "white", "font-weight": "700",
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
        st.title("Administrator Dashboard")
        st.markdown(f"### Welcome, **{user['first_name']}**! 👋")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT COUNT(*) as cnt FROM books")
            book_count = cursor.fetchone()['cnt']
            cursor.execute("SELECT COUNT(*) as cnt FROM orders")
            order_count = cursor.fetchone()['cnt']
            cursor.execute(
                "SELECT COUNT(*) as cnt FROM users WHERE role = 'student'"
            )
            student_count = cursor.fetchone()['cnt']
            cursor.execute("""
                SELECT COUNT(*) as cnt FROM trouble_tickets
                WHERE ticket_status IN ('assigned','in-process')
            """)
            active_tickets = cursor.fetchone()['cnt']
            cursor.execute("SELECT COUNT(*) as cnt FROM universities")
            uni_count = cursor.fetchone()['cnt']
            cursor.execute("SELECT COUNT(*) as cnt FROM courses")
            course_count = cursor.fetchone()['cnt']

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Books", book_count)
                st.metric("Students", student_count)
            with col2:
                st.metric("Total Orders", order_count)
                st.metric("Universities", uni_count)
            with col3:
                st.metric("Active Tickets", active_tickets)
                st.metric("Courses", course_count)

            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   MANAGE BOOKS
    # ══════════════════════════════════════
    elif selected == "Manage Books":
        st.title("Manage Books")

        if st.session_state.get('edit_book_id'):
            show_edit_book(st.session_state['edit_book_id'])
            return

        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            tab1, tab2, tab3 = st.tabs([
                "All Books", "Add Book", "Update Stock"
            ])

            with tab1:
                cursor.execute("""
                    SELECT b.*, c.name as category_name FROM books b
                    LEFT JOIN categories c ON b.category_id = c.category_id
                    ORDER BY b.created_at DESC
                """)
                books = cursor.fetchall()
                if books:
                    for book in books:
                        with st.expander(
                            f"{book['title']} (ID: {book['book_id']})"
                        ):
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                if book.get('cover_image'):
                                    st.markdown(f"""
                                    <img src="{book['cover_image']}"
                                         style="width:100%; max-width:150px;
                                                border-radius:8px;
                                                box-shadow:0 2px 8px rgba(0,0,0,0.15);"
                                         alt="{book['title']}">
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown("""
                                    <div style="width:120px; height:160px;
                                                background:linear-gradient(135deg,#8E44AD,#6C3483);
                                                border-radius:8px; display:flex;
                                                align-items:center; justify-content:center;">
                                        <span style="font-size:40px;"></span>
                                    </div>
                                    """, unsafe_allow_html=True)

                            with col2:
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.write(f"**ISBN:** {book['isbn'] or 'N/A'}")
                                    st.write(f"**Publisher:** {book['publisher'] or 'N/A'}")
                                    st.write(f"**Edition:** {book['edition']}")
                                    st.write(f"**Language:** {book['language']}")
                                    st.write(f"**Category:** {book['category_name'] or 'N/A'}")
                                with col_b:
                                    st.write(f"**Type:** {book['book_type']}")
                                    st.write(f"**Format:** {book['format']}")
                                    st.write(f"**Purchase:** {book['purchase_option']}")
                                    st.write(f"**Price:** ₹{book['price']}")
                                    st.write(f"**Stock:** {book['quantity']}")
                                    st.write(f"**Rating:** ⭐ {book['avg_rating']}")

                            cursor.execute(
                                "SELECT author_name FROM book_authors WHERE book_id = %s",
                                (book['book_id'],)
                            )
                            authors = cursor.fetchall()
                            if authors:
                                st.write(
                                    f"**Authors:** "
                                    f"{', '.join(a['author_name'] for a in authors)}"
                                )

                            cursor.execute(
                                "SELECT keyword FROM book_keywords WHERE book_id = %s",
                                (book['book_id'],)
                            )
                            keywords = cursor.fetchall()
                            if keywords:
                                st.write(
                                    f"**Keywords:** "
                                    f"{', '.join(k['keyword'] for k in keywords)}"
                                )

                            btn_col1, btn_col2 = st.columns(2)
                            with btn_col1:
                                if st.button(
                                    f"Edit Book #{book['book_id']}",
                                    key=f"edit_book_{book['book_id']}",
                                    use_container_width=True
                                ):
                                    st.session_state['edit_book_id'] = book['book_id']
                                    st.rerun()
                            with btn_col2:
                                if st.button(
                                    f"Delete Book #{book['book_id']}",
                                    key=f"del_book_{book['book_id']}",
                                    use_container_width=True
                                ):
                                    cursor.execute(
                                        "DELETE FROM books WHERE book_id = %s",
                                        (book['book_id'],)
                                    )
                                    conn.commit()
                                    st.session_state['toast_message'] = "Changes Updated! Book deleted."
                                    st.session_state['toast_icon'] = "🎉"
                                    st.rerun()
                else:
                    st.info("No books yet. Add some books!")

            with tab2:
                cursor.execute("SELECT * FROM categories ORDER BY name")
                categories = cursor.fetchall()
                with st.form("add_book_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        title     = st.text_input("Title *")
                        isbn      = st.text_input("ISBN *", max_chars=20)
                        publisher = st.text_input("Publisher")
                        pub_date  = st.date_input(
                            "Publication Date", value=date.today()
                        )
                        edition   = st.number_input("Edition", min_value=1, value=1)
                        language  = st.text_input("Language", value="English")
                    with col2:
                        book_type       = st.selectbox("Type", ["new", "used"])
                        purchase_option = st.selectbox(
                            "Purchase Option", ["buy", "rent"]
                        )
                        book_format     = st.selectbox(
                            "Format", ["hardcover", "softcover", "electronic"]
                        )
                        price    = st.number_input("Price (₹)", min_value=0.0, step=10.0)
                        quantity = st.number_input("Quantity", min_value=0, step=1)
                        cat_options  = ["None"] + [c['name'] for c in categories]
                        selected_cat = st.selectbox("Category", cat_options)

                    authors_str  = st.text_input("Authors (comma-separated)")
                    keywords_str = st.text_input("Keywords (comma-separated)")
                    cover_image  = st.text_input(
                        "Book Cover Image URL (optional)",
                        placeholder="https://covers.openlibrary.org/b/isbn/ISBN-L.jpg"
                    )

                    if st.form_submit_button(
                        "Add Book", use_container_width=True, type="primary"
                    ):
                        if not title or not isbn:
                            st.error("Title and ISBN are required")
                        else:
                            cat_id = None
                            if selected_cat != "None":
                                cat_id = next(
                                    (c['category_id'] for c in categories
                                     if c['name'] == selected_cat), None
                                )
                            try:
                                cursor.execute("""
                                    INSERT INTO books
                                        (title, isbn, publisher, publication_date,
                                         edition, language, book_type, purchase_option,
                                         format, price, quantity, category_id, cover_image)
                                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                """, (
                                    title, isbn, publisher, pub_date,
                                    edition, language, book_type, purchase_option,
                                    book_format, price, quantity, cat_id,
                                    cover_image if cover_image else None
                                ))
                                book_id = cursor.lastrowid
                                if authors_str:
                                    for author in authors_str.split(","):
                                        author = author.strip()
                                        if author:
                                            cursor.execute(
                                                "INSERT INTO book_authors VALUES (%s,%s)",
                                                (book_id, author)
                                            )
                                if keywords_str:
                                    for kw in keywords_str.split(","):
                                        kw = kw.strip()
                                        if kw:
                                            cursor.execute(
                                                "INSERT INTO book_keywords VALUES (%s,%s)",
                                                (book_id, kw)
                                            )
                                conn.commit()
                                st.session_state['toast_message'] = f"Changes Updated! Book '{title}' added!"
                                st.session_state['toast_icon'] = "🎉"
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"Error: {e}")

            with tab3:
                cursor.execute(
                    "SELECT book_id, title, quantity FROM books ORDER BY title"
                )
                books = cursor.fetchall()
                if books:
                    with st.form("update_stock_form"):
                        book_options = {
                            f"{b['title']} (ID:{b['book_id']}) — Stock:{b['quantity']}": b['book_id']
                            for b in books
                        }
                        selected_book = st.selectbox(
                            "Select Book", list(book_options.keys())
                        )
                        new_qty = st.number_input("New Quantity", min_value=0, step=1)
                        if st.form_submit_button("Update Stock", type="primary"):
                            cursor.execute(
                                "UPDATE books SET quantity = %s WHERE book_id = %s",
                                (new_qty, book_options[selected_book])
                            )
                            conn.commit()
                            st.session_state['toast_message'] = "Changes Updated! Stock updated!"
                            st.session_state['toast_icon'] = "🎉"
                            st.rerun()
                else:
                    st.info("No books to update.")

            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   MANAGE CATEGORIES
    # ══════════════════════════════════════
    elif selected == "Manage Categories":
        st.title("Manage Categories & Subcategories")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            tab1, tab2 = st.tabs(["Categories", "Subcategories"])

            with tab1:
                with st.form("add_cat"):
                    cat_name = st.text_input("Category Name *")
                    if st.form_submit_button("Add Category", type="primary"):
                        if cat_name:
                            try:
                                cursor.execute(
                                    "INSERT INTO categories (name) VALUES (%s)",
                                    (cat_name,)
                                )
                                conn.commit()
                                st.session_state['toast_message'] = "Changes Updated! Category added!"
                                st.session_state['toast_icon'] = "🎉"
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

                st.markdown("---")
                st.subheader("All Categories")
                cursor.execute("SELECT * FROM categories ORDER BY name")
                cats = cursor.fetchall()
                if cats:
                    for c in cats:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"**{c['name']}** (ID: {c['category_id']})")
                        with col2:
                            if st.button(
                                "🗑️",
                                key=f"del_cat_{c['category_id']}",
                                help=f"Delete category '{c['name']}'"
                            ):
                                cursor.execute(
                                    "DELETE FROM categories WHERE category_id = %s",
                                    (c['category_id'],)
                                )
                                conn.commit()
                                st.session_state['toast_message'] = "Changes Updated! Category deleted."
                                st.session_state['toast_icon'] = "🎉"
                                st.rerun()
                else:
                    st.info("No categories found. Add one above!")

            with tab2:
                cursor.execute("SELECT * FROM categories ORDER BY name")
                cats = cursor.fetchall()
                if cats:
                    with st.form("add_subcat"):
                        cat_options = {c['name']: c['category_id'] for c in cats}
                        parent   = st.selectbox(
                            "Parent Category", list(cat_options.keys())
                        )
                        sub_name = st.text_input("Subcategory Name *")
                        if st.form_submit_button("Add Subcategory", type="primary"):
                            if sub_name:
                                try:
                                    cursor.execute(
                                        "INSERT INTO subcategories (name, category_id) VALUES (%s,%s)",
                                        (sub_name, cat_options[parent])
                                    )
                                    conn.commit()
                                    st.session_state['toast_message'] = "Changes Updated! Subcategory added!"
                                    st.session_state['toast_icon'] = "🎉"
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                            else:
                                st.error("⚠️ Subcategory name is required.")

                    st.markdown("---")
                    st.subheader("All Subcategories")
                    cursor.execute("""
                        SELECT s.*, c.name as cat_name
                        FROM subcategories s
                        JOIN categories c ON s.category_id = c.category_id
                        ORDER BY c.name, s.name
                    """)
                    subcats = cursor.fetchall()
                    if subcats:
                        current_cat = None
                        for s in subcats:
                            if s['cat_name'] != current_cat:
                                current_cat = s['cat_name']
                                st.markdown(f"**{current_cat}**")
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.write(
                                    f"&nbsp;&nbsp;&nbsp;&nbsp;↳ "
                                    f"{s['name']} "
                                    f"(ID: {s['subcategory_id']})"
                                )
                            with col2:
                                if st.button(
                                    "🗑️",
                                    key=f"del_subcat_{s['subcategory_id']}",
                                    help=f"Delete subcategory '{s['name']}'"
                                ):
                                    cursor.execute(
                                        "DELETE FROM subcategories WHERE subcategory_id = %s",
                                        (s['subcategory_id'],)
                                    )
                                    conn.commit()
                                    st.session_state['toast_message'] = (
                                        f"Changes Updated! "
                                        f"Subcategory '{s['name']}' deleted."
                                    )
                                    st.session_state['toast_icon'] = "🎉"
                                    st.rerun()
                    else:
                        st.info("No subcategories found. Add one above!")
                else:
                    st.info(
                        "No categories found. "
                        "Please add a category first."
                    )

            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   MANAGE UNIVERSITIES
    # ══════════════════════════════════════
    elif selected == "Manage Universities":
        st.title("Manage Universities")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            with st.form("add_uni"):
                col1, col2 = st.columns(2)
                with col1:
                    uni_name = st.text_input("University Name *")
                    uni_addr = st.text_area("Address")
                    rep_fn   = st.text_input("Representative First Name")
                with col2:
                    rep_ln    = st.text_input("Representative Last Name")
                    rep_email = st.text_input("Representative Email")
                    rep_phone = st.text_input("Representative Phone")
                if st.form_submit_button(
                    "Add University", use_container_width=True, type="primary"
                ):
                    if uni_name:
                        cursor.execute("""
                            INSERT INTO universities
                                (name, address, rep_first_name, rep_last_name,
                                 rep_email, rep_phone)
                            VALUES (%s,%s,%s,%s,%s,%s)
                        """, (uni_name, uni_addr, rep_fn, rep_ln, rep_email, rep_phone))
                        conn.commit()
                        st.session_state['toast_message'] = "Changes Updated! University added!"
                        st.session_state['toast_icon'] = "🎉"
                        st.rerun()

            st.markdown("---")
            cursor.execute("SELECT * FROM universities ORDER BY name")
            for u in cursor.fetchall():
                with st.expander(f"{u['name']} (ID: {u['university_id']})"):
                    st.write(f"**Address:** {u['address'] or 'N/A'}")
                    st.write(f"**Rep:** {u['rep_first_name']} {u['rep_last_name']}")
                    st.write(
                        f"**Email:** {u['rep_email'] or 'N/A'} | "
                        f"**Phone:** {u['rep_phone'] or 'N/A'}"
                    )
                    if st.button("Delete", key=f"del_uni_{u['university_id']}"):
                        cursor.execute(
                            "DELETE FROM universities WHERE university_id = %s",
                            (u['university_id'],)
                        )
                        conn.commit()
                        st.session_state['toast_message'] = "Changes Updated! University deleted."
                        st.session_state['toast_icon'] = "🎉"
                        st.rerun()

            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   MANAGE DEPARTMENTS
    # ══════════════════════════════════════
    elif selected == "Manage Departments":
        st.title("Manage Departments")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM universities ORDER BY name")
            unis = cursor.fetchall()
            if unis:
                with st.form("add_dept"):
                    uni_options = {u['name']: u['university_id'] for u in unis}
                    sel_uni   = st.selectbox("University", list(uni_options.keys()))
                    dept_name = st.text_input("Department Name *")
                    if st.form_submit_button("Add Department", type="primary"):
                        if dept_name:
                            cursor.execute(
                                "INSERT INTO departments (name, university_id) VALUES (%s,%s)",
                                (dept_name, uni_options[sel_uni])
                            )
                            conn.commit()
                            st.session_state['toast_message'] = "Changes Updated! Department added!"
                            st.session_state['toast_icon'] = "🎉"
                            st.rerun()

                st.markdown("---")
                cursor.execute("""
                    SELECT d.*, u.name as uni_name FROM departments d
                    JOIN universities u ON d.university_id = u.university_id
                    ORDER BY u.name, d.name
                """)
                for d in cursor.fetchall():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"**{d['name']}** — {d['uni_name']}")
                    with col2:
                        if st.button("🗑️", key=f"del_dept_{d['department_id']}"):
                            cursor.execute(
                                "DELETE FROM departments WHERE department_id = %s",
                                (d['department_id'],)
                            )
                            conn.commit()
                            st.session_state['toast_message'] = "Changes Updated! Department deleted."
                            st.session_state['toast_icon'] = "🎉"
                            st.rerun()
            else:
                st.info("Add a university first.")
            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   MANAGE INSTRUCTORS
    # ══════════════════════════════════════
    elif selected == "Manage Instructors":
        st.title("Manage Instructors")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM universities ORDER BY name")
            unis = cursor.fetchall()
            cursor.execute("""
                SELECT d.*, u.name as uni_name FROM departments d
                JOIN universities u ON d.university_id = u.university_id
                ORDER BY d.name
            """)
            depts = cursor.fetchall()
            if unis and depts:
                with st.form("add_instructor"):
                    col1, col2 = st.columns(2)
                    with col1:
                        inst_fn  = st.text_input("First Name *")
                        uni_opts = {u['name']: u['university_id'] for u in unis}
                        sel_uni  = st.selectbox("University", list(uni_opts.keys()))
                    with col2:
                        inst_ln   = st.text_input("Last Name *")
                        dept_opts = {
                            f"{d['name']} ({d['uni_name']})": d['department_id']
                            for d in depts
                        }
                        sel_dept = st.selectbox("Department", list(dept_opts.keys()))
                    if st.form_submit_button("Add Instructor", type="primary"):
                        if inst_fn and inst_ln:
                            cursor.execute("""
                                INSERT INTO instructors
                                    (first_name, last_name, university_id, department_id)
                                VALUES (%s,%s,%s,%s)
                            """, (
                                inst_fn, inst_ln,
                                uni_opts[sel_uni], dept_opts[sel_dept]
                            ))
                            conn.commit()
                            st.session_state['toast_message'] = "Changes Updated! Instructor added!"
                            st.session_state['toast_icon'] = "🎉"
                            st.rerun()

                st.markdown("---")
                cursor.execute("""
                    SELECT i.*, u.name as uni_name, d.name as dept_name
                    FROM instructors i
                    LEFT JOIN universities u ON i.university_id = u.university_id
                    LEFT JOIN departments d ON i.department_id = d.department_id
                    ORDER BY i.first_name
                """)
                for inst in cursor.fetchall():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(
                            f"**{inst['first_name']} {inst['last_name']}** — "
                            f"{inst['dept_name'] or 'N/A'}, {inst['uni_name'] or 'N/A'}"
                        )
                    with col2:
                        if st.button("🗑️", key=f"del_inst_{inst['instructor_id']}"):
                            cursor.execute(
                                "DELETE FROM instructors WHERE instructor_id = %s",
                                (inst['instructor_id'],)
                            )
                            conn.commit()
                            st.session_state['toast_message'] = "Changes Updated! Instructor deleted."
                            st.session_state['toast_icon'] = "🎉"
                            st.rerun()
            else:
                st.info("Add universities and departments first.")
            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   MANAGE COURSES
    # ══════════════════════════════════════
    elif selected == "Manage Courses":
        st.title("Manage Courses")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM universities ORDER BY name")
            unis = cursor.fetchall()
            if unis:
                with st.form("add_course"):
                    col1, col2 = st.columns(2)
                    with col1:
                        course_name = st.text_input("Course Name *")
                        uni_opts    = {u['name']: u['university_id'] for u in unis}
                        sel_uni     = st.selectbox("University", list(uni_opts.keys()))
                    with col2:
                        year     = st.number_input(
                            "Year", min_value=2020, max_value=2030, value=2025
                        )
                        semester = st.text_input(
                            "Semester", placeholder="Fall / Spring / Semester 1 etc."
                        )
                    if st.form_submit_button("Add Course", type="primary"):
                        if course_name:
                            cursor.execute("""
                                INSERT INTO courses
                                    (course_name, university_id, year, semester)
                                VALUES (%s,%s,%s,%s)
                            """, (course_name, uni_opts[sel_uni], year, semester))
                            conn.commit()
                            st.session_state['toast_message'] = "Changes Updated! Course added!"
                            st.session_state['toast_icon'] = "🎉"
                            st.rerun()

                st.markdown("---")
                cursor.execute("SELECT * FROM courses ORDER BY course_name")
                courses = cursor.fetchall()
                cursor.execute("SELECT * FROM books ORDER BY title")
                books = cursor.fetchall()
                cursor.execute("SELECT * FROM instructors ORDER BY first_name")
                instructors = cursor.fetchall()

                if courses and books and instructors:
                    st.subheader("Link Book to Course")
                    with st.form("link_book_course"):
                        course_opts = {
                            f"{c['course_name']} (ID:{c['course_id']})": c['course_id']
                            for c in courses
                        }
                        sel_course = st.selectbox("Course", list(course_opts.keys()))
                        book_opts  = {
                            f"{b['title']} (ID:{b['book_id']})": b['book_id']
                            for b in books
                        }
                        sel_book  = st.selectbox("Book", list(book_opts.keys()))
                        inst_opts = {
                            f"{i['first_name']} {i['last_name']}": i['instructor_id']
                            for i in instructors
                        }
                        sel_inst  = st.selectbox("Instructor", list(inst_opts.keys()))
                        req_type  = st.selectbox(
                            "Requirement", ["required", "recommended"]
                        )
                        link_year = st.number_input(
                            "Year", min_value=2020, max_value=2030,
                            value=2025, key="link_yr"
                        )
                        link_sem  = st.text_input(
                            "Semester",
                            placeholder="Fall / Spring / Semester 1 etc.",
                            key="link_sem"
                        )
                        if st.form_submit_button("Link Book", type="primary"):
                            try:
                                cursor.execute("""
                                    INSERT INTO course_books
                                        (course_id, book_id, instructor_id,
                                         year, semester, requirement_type)
                                    VALUES (%s,%s,%s,%s,%s,%s)
                                """, (
                                    course_opts[sel_course], book_opts[sel_book],
                                    inst_opts[sel_inst], link_year, link_sem, req_type
                                ))
                                conn.commit()
                                st.session_state['toast_message'] = "Changes Updated! Book linked to course!"
                                st.session_state['toast_icon'] = "🎉"
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

                st.markdown("---")
                st.subheader("All Courses")
                cursor.execute("""
                    SELECT c.*, u.name as uni_name FROM courses c
                    LEFT JOIN universities u ON c.university_id = u.university_id
                    ORDER BY c.course_name
                """)
                courses = cursor.fetchall()
                if courses:
                    for c in courses:
                        with st.expander(
                            f"{c['course_name']} — "
                            f"{c['uni_name'] or 'N/A'} "
                            f"({c['year']} / {c['semester'] or ''})"
                        ):
                            if st.button(
                                f"Delete Course #{c['course_id']}",
                                key=f"del_course_{c['course_id']}",
                                help=f"Delete course '{c['course_name']}'"
                            ):
                                cursor.execute(
                                    "DELETE FROM courses WHERE course_id = %s",
                                    (c['course_id'],)
                                )
                                conn.commit()
                                st.session_state['toast_message'] = (
                                    f"Changes Updated! "
                                    f"Course '{c['course_name']}' deleted."
                                )
                                st.session_state['toast_icon'] = "🎉"
                                st.rerun()

                            st.markdown("**Linked Books:**")
                            cursor.execute("""
                                SELECT cb.course_id, cb.book_id,
                                       cb.instructor_id,
                                       cb.requirement_type,
                                       cb.year, cb.semester,
                                       b.title,
                                       i.first_name, i.last_name
                                FROM course_books cb
                                JOIN books b ON cb.book_id = b.book_id
                                JOIN instructors i
                                    ON cb.instructor_id = i.instructor_id
                                WHERE cb.course_id = %s
                            """, (c['course_id'],))
                            cbooks = cursor.fetchall()
                            if cbooks:
                                for cb in cbooks:
                                    cb_col1, cb_col2 = st.columns([5, 1])
                                    with cb_col1:
                                        req_color = (
                                            "#27AE60"
                                            if cb['requirement_type'] == 'required'
                                            else "#E67E22"
                                        )
                                        st.markdown(f"""
                                        <div style="background:#F8F9FA;
                                                    border-left:4px solid {req_color};
                                                    border-radius:6px;
                                                    padding:10px 14px;
                                                    margin-bottom:6px;">
                                            <p style="margin:0; font-size:14px;
                                                       font-weight:600;
                                                       color:#2C3E50;">
                                                {cb['title']}
                                            </p>
                                            <p style="margin:3px 0 0 0;
                                                       font-size:12px;
                                                       color:#7F8C8D;">
                                                Dr. {cb['first_name']} {cb['last_name']} &nbsp;|&nbsp;
                                                <span style="color:{req_color};
                                                             font-weight:600;">
                                                    {cb['requirement_type'].upper()}
                                                </span>
                                                &nbsp;|&nbsp;
                                                {cb['year']} / {cb['semester'] or ''}
                                            </p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    with cb_col2:
                                        if st.button(
                                            "🗑️",
                                            key=(
                                                f"del_cb_"
                                                f"{c['course_id']}_"
                                                f"{cb['book_id']}_"
                                                f"{cb['instructor_id']}"
                                            ),
                                            help=(
                                                f"Remove '{cb['title']}' "
                                                f"from this course"
                                            )
                                        ):
                                            cursor.execute("""
                                                DELETE FROM course_books
                                                WHERE course_id    = %s
                                                  AND book_id      = %s
                                                  AND instructor_id = %s
                                            """, (
                                                c['course_id'],
                                                cb['book_id'],
                                                cb['instructor_id']
                                            ))
                                            conn.commit()
                                            st.session_state['toast_message'] = (
                                                f"Changes Updated! "
                                                f"'{cb['title']}' removed "
                                                f"from course."
                                            )
                                            st.session_state['toast_icon'] = "🎉"
                                            st.rerun()
                            else:
                                st.info("No books linked to this course yet.")
                else:
                    st.info("No courses added yet.")
            else:
                st.info("Add a university first.")
            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   TROUBLE TICKETS
    # ══════════════════════════════════════
    elif selected == "Trouble Tickets":
        st.title("Trouble Tickets (Admin View)")
        st.info(
            "Administrators manage tickets with status: "
            "assigned, in-process, completed."
        )
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            status_filter = st.selectbox(
                "Filter",
                ["assigned", "in-process", "completed", "All (view only)"]
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
            if status_filter != "All (view only)":
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
                            f"{t['creator_ln']} ({t['created_by_role']})"
                        )
                        st.write(f"**Problem:** {t['problem_description']}")
                        if t['solution_description']:
                            st.success(f"**Solution:** {t['solution_description']}")
                        st.write(
                            f"**Date:** "
                            f"{t['date_logged'].strftime('%d %b %Y %H:%M')}"
                        )
                        if t['admin_fn']:
                            st.write(
                                f"**Admin:** {t['admin_fn']} {t['admin_ln']}"
                            )

                        if t['ticket_status'] in ('assigned', 'in-process'):
                            st.markdown("---")
                            new_status = st.selectbox(
                                "Change Status",
                                ["assigned", "in-process", "completed"],
                                index=["assigned", "in-process", "completed"].index(
                                    t['ticket_status']
                                ),
                                key=f"admin_status_{t['ticket_id']}"
                            )
                            solution = st.text_area(
                                "Solution Description",
                                value=t['solution_description'] or "",
                                key=f"admin_sol_{t['ticket_id']}"
                            )
                            if st.button(
                                f"Update Ticket #{t['ticket_id']}",
                                key=f"admin_upd_{t['ticket_id']}"
                            ):
                                comp_date = None
                                if new_status == "completed":
                                    from datetime import datetime
                                    comp_date = datetime.now()
                                cursor.execute("""
                                    UPDATE trouble_tickets
                                    SET ticket_status       = %s,
                                        solution_description = %s,
                                        completion_date      = %s,
                                        assigned_admin       = %s
                                    WHERE ticket_id = %s
                                """, (
                                    new_status, solution, comp_date,
                                    user['user_id'], t['ticket_id']
                                ))
                                cursor.execute("""
                                    INSERT INTO ticket_status_history
                                        (ticket_id, old_status, new_status, changed_by)
                                    VALUES (%s,%s,%s,%s)
                                """, (
                                    t['ticket_id'], t['ticket_status'],
                                    new_status, user['user_id']
                                ))
                                conn.commit()
                                st.session_state['toast_message'] = (
                                    f"Changes Updated! "
                                    f"Ticket #{t['ticket_id']} updated!"
                                )
                                st.session_state['toast_icon'] = "🎉"
                                st.rerun()
            else:
                st.info("No tickets found for selected filter.")
            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   MANAGE ORDERS
    # ══════════════════════════════════════
    elif selected == "Manage Orders":
        st.title("Manage Orders")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT o.*, u.first_name, u.last_name FROM orders o
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
                        st.write(f"**Amount:** ₹{order['total_amount']}")
                        st.write(f"**Shipping:** {order['shipping_type']}")

                        cursor.execute("""
                            SELECT oi.*, b.title FROM order_items oi
                            JOIN books b ON oi.book_id = b.book_id
                            WHERE oi.order_id = %s
                        """, (order['order_id'],))
                        items = cursor.fetchall()
                        for it in items:
                            st.write(
                                f"  {it['title']} — "
                                f"Qty:{it['quantity']} — ₹{it['price']}"
                            )

                        if order['order_status'] not in ('canceled', 'shipped'):
                            statuses = [
                                "new", "processed", "awaiting_shipping",
                                "shipped", "canceled"
                            ]
                            new_order_status = st.selectbox(
                                "Update Status", statuses,
                                index=statuses.index(order['order_status']),
                                key=f"order_st_{order['order_id']}"
                            )
                            if st.button(
                                f"Update Order #{order['order_id']}",
                                key=f"upd_order_{order['order_id']}"
                            ):
                                update_q = "UPDATE orders SET order_status = %s"
                                p = [new_order_status]
                                if new_order_status == 'shipped':
                                    from datetime import datetime
                                    update_q += ", date_fulfilled = %s"
                                    p.append(datetime.now())
                                update_q += " WHERE order_id = %s"
                                p.append(order['order_id'])
                                cursor.execute(update_q, p)
                                if new_order_status == 'canceled':
                                    for it in items:
                                        cursor.execute(
                                            "UPDATE books SET quantity = quantity + %s WHERE book_id = %s",
                                            (it['quantity'], it['book_id'])
                                        )
                                conn.commit()
                                st.session_state['toast_message'] = (
                                    f"Changes Updated! "
                                    f"Order #{order['order_id']} updated!"
                                )
                                st.session_state['toast_icon'] = "🎉"
                                st.rerun()
            else:
                st.info("No orders.")
            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   VIEW REVIEWS
    # ══════════════════════════════════════
    elif selected == "View Reviews":
        st.title("View Reviews")
        st.info(
            "View all student reviews for each book. "
            "Reviews are read-only for administrators."
        )

        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)

            # ── Search / Filter ──
            col1, col2 = st.columns(2)
            with col1:
                search = st.text_input(
                    "🔍 Search by book title",
                    placeholder="Type book title..."
                )
            with col2:
                rating_filter = st.selectbox(
                    "Filter by Rating",
                    ["All", "5 ⭐", "4 ⭐", "3 ⭐", "2 ⭐", "1 ⭐"]
                )

            # ── Fetch all books that have at least one review ──
            query = """
                SELECT DISTINCT b.book_id, b.title, b.cover_image,
                       b.avg_rating,
                       COUNT(r.review_id) as review_count
                FROM books b
                JOIN reviews r ON b.book_id = r.book_id
            """
            params = []
            if search:
                query += " WHERE b.title LIKE %s"
                params.append(f"%{search}%")
            query += " GROUP BY b.book_id, b.title, b.cover_image, b.avg_rating"
            query += " ORDER BY review_count DESC"

            cursor.execute(query, params)
            books_with_reviews = cursor.fetchall()

            # ── Apply rating filter ──
            rating_map = {
                "5 ⭐": 5, "4 ⭐": 4, "3 ⭐": 3,
                "2 ⭐": 2, "1 ⭐": 1
            }

            if books_with_reviews:
                st.markdown(
                    f"**Total Books with Reviews: {len(books_with_reviews)}**"
                )
                st.markdown("---")

                for book in books_with_reviews:
                    review_label = (
                        f"{book['review_count']} Review"
                        f"{'s' if book['review_count'] != 1 else ''}"
                    )
                    avg = float(book['avg_rating']) if book['avg_rating'] else 0.0
                    stars_full  = int(avg)
                    stars_str   = '⭐' * stars_full

                    with st.expander(
                        f"{book['title']} — "
                        f"{stars_str} {avg:.1f} — "
                        f"{review_label}"
                    ):
                        # ── Book header ──
                        hcol1, hcol2 = st.columns([1, 4])
                        with hcol1:
                            if book.get('cover_image'):
                                st.markdown(f"""
                                <img src="{book['cover_image']}"
                                     style="width:80px; height:110px;
                                            object-fit:cover;
                                            border-radius:8px;
                                            box-shadow:0 2px 8px rgba(0,0,0,0.15);">
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style="width:80px; height:110px;
                                            background:linear-gradient(135deg,#8E44AD,#6C3483);
                                            border-radius:8px; display:flex;
                                            align-items:center;
                                            justify-content:center;">
                                    <span style="font-size:28px;"></span>
                                </div>
                                """, unsafe_allow_html=True)
                        with hcol2:
                            st.write(f"**Book:** {book['title']}")
                            st.write(
                                f"**⭐ Average Rating:** "
                                f"{stars_str} ({avg:.1f} / 5)"
                            )
                            st.write(
                                f"**Total Reviews:** {book['review_count']}"
                            )

                        st.markdown("---")

                        # ── Fetch individual reviews ──
                        rev_query = """
                            SELECT r.*, u.first_name, u.last_name
                            FROM reviews r
                            JOIN users u ON r.student_id = u.user_id
                            WHERE r.book_id = %s
                        """
                        rev_params = [book['book_id']]

                        if rating_filter != "All":
                            rev_query += " AND r.rating = %s"
                            rev_params.append(rating_map[rating_filter])

                        rev_query += " ORDER BY r.created_at DESC"
                        cursor.execute(rev_query, rev_params)
                        reviews = cursor.fetchall()

                        if reviews:
                            st.subheader(
                                f"Individual Reviews "
                                f"({'All' if rating_filter == 'All' else rating_filter})"
                            )
                            for rev in reviews:
                                rev_date   = rev['created_at'].strftime('%d %b %Y')
                                rev_rating = int(rev['rating'])
                                rev_stars  = '⭐' * rev_rating
                                rev_name   = (
                                    f"{rev['first_name']} {rev['last_name']}"
                                )
                                rev_text   = (
                                    rev['review_text'] or 'No review text.'
                                )

                                # ── Review card ──
                                rcol1, rcol2 = st.columns([1, 8])
                                with rcol1:
                                    st.markdown(f"""
                                    <div style="
                                        width:45px; height:45px;
                                        border-radius:50%;
                                        background:linear-gradient(135deg,#3498DB,#2C3E50);
                                        display:flex; align-items:center;
                                        justify-content:center;
                                        font-size:18px; color:white;
                                        font-weight:700;">
                                        {rev['first_name'][0].upper()}
                                    </div>
                                    """, unsafe_allow_html=True)
                                with rcol2:
                                    st.write(
                                        f"**{rev_name}** — "
                                        f"{rev_stars} ({rev_rating}/5)"
                                    )
                                    st.write(f"{rev_text}")
                                    st.caption(f"{rev_date}")

                                st.markdown(
                                    "<hr style='border:none; "
                                    "border-top:1px solid #F0F0F0; "
                                    "margin:8px 0;'>",
                                    unsafe_allow_html=True
                                )
                        else:
                            st.info(
                                f"No reviews with rating "
                                f"{rating_filter} for this book."
                            )
            else:
                if search:
                    st.info(
                        f"No reviews found for books matching '{search}'."
                    )
                else:
                    st.info("No reviews have been submitted yet.")

            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   PROFILE
    # ══════════════════════════════════════
    elif selected == "Profile":
        show_admin_profile(user)

    show_footer()


# ══════════════════════════════════════
#   ADMIN PROFILE (no salary field)
# ══════════════════════════════════════
def show_admin_profile(user):
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
        st.subheader("Personal Information")
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
        st.subheader("Employment Information")
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
    st.subheader("Change Profile")

    with st.form("admin_change_profile_form", clear_on_submit=False):

        st.markdown("##### Personal Details")
        col1, col2 = st.columns(2)
        with col1:
            new_first = st.text_input(
                "First Name *",
                value=fresh_user['first_name'],
                key="adm_cp_fn"
            )
            new_email = st.text_input(
                "Email *",
                value=fresh_user['email'],
                key="adm_cp_email"
            )
            new_phone = st.text_input(
                "Phone",
                value=fresh_user['phone'] or "",
                key="adm_cp_phone"
            )
        with col2:
            new_last = st.text_input(
                "Last Name *",
                value=fresh_user['last_name'],
                key="adm_cp_ln"
            )
            new_password = st.text_input(
                "New Password (leave blank to keep current)",
                type="password",
                placeholder="Enter new password",
                key="adm_cp_pass"
            )
            confirm_password = st.text_input(
                "Confirm New Password",
                type="password",
                placeholder="Confirm new password",
                key="adm_cp_confirm"
            )
        new_address = st.text_area(
            "Address",
            value=fresh_user['address'] or "",
            key="adm_cp_addr"
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
                key="adm_cp_gender"
            )
        with col4:
            new_aadhaar = st.text_input(
                "Aadhaar Number *",
                value=emp['aadhaar_number']
                      if emp and emp['aadhaar_number'] else "",
                max_chars=12,
                key="adm_cp_aadhaar"
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
                st.error("First name, last name and email are required.")
            elif new_password and new_password != confirm_password:
                st.error("Passwords do not match.")
            elif new_password and len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            elif not new_aadhaar or len(new_aadhaar) != 12 \
                    or not new_aadhaar.isdigit():
                st.error("Aadhaar must be exactly 12 digits.")
            else:
                try:
                    cursor.execute(
                        "SELECT user_id FROM users WHERE email = %s AND user_id != %s",
                        (new_email, fresh_user['user_id'])
                    )
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

                            st.session_state['toast_message'] = "Changes Updated!"
                            st.session_state['toast_icon']    = "🎉"
                            st.rerun()

                except Exception as e:
                    conn.rollback()
                    st.error(f"Error updating profile: {e}")

    cursor.close()
    conn.close()


# ══════════════════════════════════════
#   EDIT BOOK PAGE
# ══════════════════════════════════════
def show_edit_book(book_id):
    conn = get_connection()
    if not conn:
        st.error("Database connection failed.")
        return

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT b.*, c.name as category_name FROM books b
        LEFT JOIN categories c ON b.category_id = c.category_id
        WHERE b.book_id = %s
    """, (book_id,))
    book = cursor.fetchone()

    if not book:
        st.error("Book not found.")
        if st.button("← Back to Manage Books"):
            del st.session_state['edit_book_id']
            st.rerun()
        return

    cursor.execute(
        "SELECT author_name FROM book_authors WHERE book_id = %s",
        (book_id,)
    )
    authors = cursor.fetchall()
    existing_authors = ", ".join(a['author_name'] for a in authors)

    cursor.execute(
        "SELECT keyword FROM book_keywords WHERE book_id = %s",
        (book_id,)
    )
    keywords = cursor.fetchall()
    existing_keywords = ", ".join(k['keyword'] for k in keywords)

    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()

    if st.button("← Back to Manage Books"):
        del st.session_state['edit_book_id']
        st.rerun()

    st.markdown("---")
    st.title(f"Edit Book — {book['title']}")
    st.info("Update the book details below and click Save Changes.")

    with st.form("edit_book_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            new_title = st.text_input(
                "Title *", value=book['title'], key="eb_title"
            )
            new_isbn = st.text_input(
                "ISBN *", value=book['isbn'] or "",
                max_chars=20, key="eb_isbn"
            )
            new_publisher = st.text_input(
                "Publisher", value=book['publisher'] or "",
                key="eb_publisher"
            )
            new_pub_date = st.date_input(
                "Publication Date",
                value=book['publication_date']
                      if book['publication_date'] else date.today(),
                key="eb_pub_date"
            )
            new_edition = st.number_input(
                "Edition", min_value=1,
                value=int(book['edition']) if book['edition'] else 1,
                key="eb_edition"
            )
            new_language = st.text_input(
                "Language",
                value=book['language'] or "English",
                key="eb_language"
            )

        with col2:
            book_type_options = ["new", "used"]
            new_book_type = st.selectbox(
                "Type", book_type_options,
                index=book_type_options.index(book['book_type'])
                      if book['book_type'] in book_type_options else 0,
                key="eb_book_type"
            )
            purchase_options = ["buy", "rent"]
            new_purchase_option = st.selectbox(
                "Purchase Option", purchase_options,
                index=purchase_options.index(book['purchase_option'])
                      if book['purchase_option'] in purchase_options else 0,
                key="eb_purchase_option"
            )
            format_options = ["hardcover", "softcover", "electronic"]
            new_format = st.selectbox(
                "Format", format_options,
                index=format_options.index(book['format'])
                      if book['format'] in format_options else 0,
                key="eb_format"
            )
            new_price = st.number_input(
                "Price (₹)", min_value=0.0, step=10.0,
                value=float(book['price']) if book['price'] else 0.0,
                key="eb_price"
            )
            new_quantity = st.number_input(
                "Quantity", min_value=0, step=1,
                value=int(book['quantity']) if book['quantity'] else 0,
                key="eb_quantity"
            )
            cat_options_list = ["None"] + [c['name'] for c in categories]
            current_cat = book['category_name'] if book['category_name'] else "None"
            new_cat = st.selectbox(
                "Category", cat_options_list,
                index=cat_options_list.index(current_cat)
                      if current_cat in cat_options_list else 0,
                key="eb_category"
            )

        new_authors = st.text_input(
            "Authors (comma-separated)",
            value=existing_authors, key="eb_authors"
        )
        new_keywords = st.text_input(
            "Keywords (comma-separated)",
            value=existing_keywords, key="eb_keywords"
        )
        new_cover_image = st.text_input(
            "Book Cover Image URL (optional)",
            value=book['cover_image'] or "",
            placeholder="https://covers.openlibrary.org/b/isbn/ISBN-L.jpg",
            key="eb_cover"
        )

        if book.get('cover_image'):
            st.markdown("**Current Cover:**")
            st.markdown(f"""
            <img src="{book['cover_image']}"
                 style="width:100px; height:140px; object-fit:cover;
                        border-radius:8px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.15);"
                 alt="Current Cover">
            """, unsafe_allow_html=True)
            st.markdown("")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "Save Changes",
                use_container_width=True,
                type="primary"
            )

        if submitted:
            if not new_title or not new_isbn:
                st.error("Title and ISBN are required.")
            else:
                cat_id = None
                if new_cat != "None":
                    cat_id = next(
                        (c['category_id'] for c in categories
                         if c['name'] == new_cat), None
                    )
                try:
                    cursor.execute("""
                        UPDATE books SET
                            title            = %s,
                            isbn             = %s,
                            publisher        = %s,
                            publication_date = %s,
                            edition          = %s,
                            language         = %s,
                            book_type        = %s,
                            purchase_option  = %s,
                            format           = %s,
                            price            = %s,
                            quantity         = %s,
                            category_id      = %s,
                            cover_image      = %s
                        WHERE book_id = %s
                    """, (
                        new_title, new_isbn, new_publisher,
                        new_pub_date, new_edition, new_language,
                        new_book_type, new_purchase_option,
                        new_format, new_price, new_quantity,
                        cat_id,
                        new_cover_image if new_cover_image else None,
                        book_id
                    ))

                    cursor.execute(
                        "DELETE FROM book_authors WHERE book_id = %s",
                        (book_id,)
                    )
                    if new_authors:
                        for author in new_authors.split(","):
                            author = author.strip()
                            if author:
                                cursor.execute(
                                    "INSERT INTO book_authors VALUES (%s,%s)",
                                    (book_id, author)
                                )

                    cursor.execute(
                        "DELETE FROM book_keywords WHERE book_id = %s",
                        (book_id,)
                    )
                    if new_keywords:
                        for kw in new_keywords.split(","):
                            kw = kw.strip()
                            if kw:
                                cursor.execute(
                                    "INSERT INTO book_keywords VALUES (%s,%s)",
                                    (book_id, kw)
                                )

                    conn.commit()
                    del st.session_state['edit_book_id']
                    st.session_state['toast_message'] = (
                        f"Changes Updated! "
                        f"Book '{new_title}' updated successfully!"
                    )
                    st.session_state['toast_icon'] = "🎉"
                    st.rerun()

                except Exception as e:
                    conn.rollback()
                    st.error(f"Error updating book: {e}")

    cursor.close()
    conn.close()
