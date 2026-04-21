import streamlit as st
from streamlit_option_menu import option_menu
from database import get_connection

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

def show_student_dashboard():
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
                background:linear-gradient(135deg,#3498DB,#2C3E50);
                display:flex; align-items:center; justify-content:center;
                margin:0 auto; font-size:32px; color:white; font-weight:700;
                box-shadow: 0 4px 12px rgba(52,152,219,0.4);
            ">
                {user['first_name'][0].upper()}
            </div>
            <h3 style="margin-top:10px; margin-bottom:2px;
                       color:#2C3E50; font-size:16px;">
                {user['first_name']} {user['last_name']}
            </h3>
            <p style="color:#7F8C8D; font-size:12px; margin:0;">
                Student
            </p>
        </div>
        <hr style="border:none; border-top:1px solid #E5E7E9; margin:10px 0;">
        """, unsafe_allow_html=True)

        selected = option_menu(
            menu_title=None,
            options=[
                "Dashboard", "Browse Books", "My Cart",
                "My Orders", "My Reviews", "Trouble Tickets",
                "Profile", "Logout"
            ],
            icons=[
                "speedometer2", "book", "cart3", "bag-check",
                "star", "ticket-detailed", "person-circle", "box-arrow-right"
            ],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {"padding": "0px", "background-color": "transparent"},
                "icon": {"color": "#3498DB", "font-size": "17px"},
                "nav-link": {
                    "font-size": "14px", "text-align": "left",
                    "margin": "3px 0", "padding": "10px 15px",
                    "border-radius": "8px", "color": "#2C3E50",
                    "font-weight": "500",
                },
                "nav-link-selected": {
                    "background-color": "#3498DB",
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
        st.title("Student Dashboard")
        st.markdown(f"### Welcome back, **{user['first_name']}**! 👋")

        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT COUNT(*) as cnt FROM orders WHERE student_id = %s",
                (user['user_id'],)
            )
            order_count = cursor.fetchone()['cnt']

            cursor.execute(
                "SELECT COUNT(*) as cnt FROM reviews WHERE student_id = %s",
                (user['user_id'],)
            )
            review_count = cursor.fetchone()['cnt']

            cursor.execute("""
                SELECT COUNT(*) as cnt FROM cart_items ci
                JOIN carts c ON ci.cart_id = c.cart_id
                WHERE c.student_id = %s
            """, (user['user_id'],))
            cart_count = cursor.fetchone()['cnt']

            cursor.execute(
                "SELECT COUNT(*) as cnt FROM trouble_tickets WHERE created_by = %s",
                (user['user_id'],)
            )
            ticket_count = cursor.fetchone()['cnt']

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("My Orders", order_count)
            with col2:
                st.metric("Cart Items", cart_count)
            with col3:
                st.metric("My Reviews", review_count)
            with col4:
                st.metric("My Tickets", ticket_count)

            st.markdown("---")
            st.subheader("Recent Orders")
            cursor.execute("""
                SELECT order_id, date_created, order_status, total_amount
                FROM orders WHERE student_id = %s
                ORDER BY date_created DESC LIMIT 5
            """, (user['user_id'],))
            orders = cursor.fetchall()
            if orders:
                for o in orders:
                    status_color = {
                        "new": "🟢", "processed": "🔵",
                        "awaiting_shipping": "🟡",
                        "shipped": "✅", "canceled": "🔴"
                    }
                    st.markdown(
                        f"**Order #{o['order_id']}** | "
                        f"{status_color.get(o['order_status'], '⚪')} "
                        f"{o['order_status'].upper()} | "
                        f"₹{o['total_amount']} | "
                        f"{o['date_created'].strftime('%d %b %Y')}"
                    )
            else:
                st.info("No orders yet. Start browsing books!")

            cursor.close()
            conn.close()

        # ══════════════════════════════════════
    #   BROWSE BOOKS
    # ══════════════════════════════════════
    elif selected == "Browse Books":
        st.title("Browse Books")

        if st.session_state.get('view_book_id'):
            show_book_detail(user)
            return

        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                search = st.text_input("🔍 Search by title, ISBN or keyword", "")
            with col2:
                cursor.execute(
                    "SELECT DISTINCT category_id, name FROM categories ORDER BY name"
                )
                categories = cursor.fetchall()
                cat_options  = ["All"] + [c['name'] for c in categories]
                selected_cat = st.selectbox("Category", cat_options)
            with col3:
                format_filter = st.selectbox(
                    "Format", ["All", "hardcover", "softcover", "electronic"]
                )

            query = """
                SELECT DISTINCT b.* FROM books b
                LEFT JOIN book_keywords bk ON b.book_id = bk.book_id
                WHERE 1=1
            """
            params = []
            if search:
                query += """
                    AND (
                        b.title    LIKE %s OR
                        b.isbn     LIKE %s OR
                        bk.keyword LIKE %s
                    )
                """
                params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            if selected_cat != "All":
                cat_id = next(
                    (c['category_id'] for c in categories
                     if c['name'] == selected_cat), None
                )
                if cat_id:
                    query += " AND b.category_id = %s"
                    params.append(cat_id)
            if format_filter != "All":
                query += " AND b.format = %s"
                params.append(format_filter)
            query += " ORDER BY b.created_at DESC"

            cursor.execute(query, params)
            books = cursor.fetchall()

            # ── Fetch shipped book_ids for this student ──
            cursor.execute("""
                SELECT DISTINCT oi.book_id
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                WHERE o.student_id = %s
                  AND o.order_status = 'shipped'
            """, (user['user_id'],))
            shipped_book_ids = {row['book_id'] for row in cursor.fetchall()}

            # ── Fetch already reviewed book_ids for this student ──
            cursor.execute("""
                SELECT DISTINCT book_id FROM reviews
                WHERE student_id = %s
            """, (user['user_id'],))
            reviewed_book_ids = {row['book_id'] for row in cursor.fetchall()}

            if books:
                for i in range(0, len(books), 3):
                    cols = st.columns(3)
                    for j, col in enumerate(cols):
                        if i + j < len(books):
                            book = books[i + j]
                            with col:
                                # ── Book Cover Image ──
                                if book.get('cover_image'):
                                    st.markdown(f"""
                                    <div style="text-align:center;
                                                margin-bottom:10px;">
                                        <img src="{book['cover_image']}"
                                             style="width:100%;
                                                    max-width:200px;
                                                    height:250px;
                                                    object-fit:cover;
                                                    border-radius:10px;
                                                    box-shadow:0 4px 12px rgba(0,0,0,0.15);"
                                             alt="{book['title']}">
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown("""
                                    <div style="width:100%; height:220px;
                                                background:linear-gradient(135deg,#3498DB,#2C3E50);
                                                border-radius:10px; display:flex;
                                                align-items:center;
                                                justify-content:center;
                                                margin-bottom:10px;
                                                box-shadow:0 4px 12px rgba(0,0,0,0.15);">
                                        <span style="font-size:60px;"></span>
                                    </div>
                                    """, unsafe_allow_html=True)

                                # ── Fetch Instructors + Requirement Type ──
                                cursor.execute("""
                                    SELECT DISTINCT
                                        i.first_name,
                                        i.last_name,
                                        cb.requirement_type
                                    FROM course_books cb
                                    JOIN instructors i
                                        ON cb.instructor_id = i.instructor_id
                                    WHERE cb.book_id = %s
                                """, (book['book_id'],))
                                instructors = cursor.fetchall()

                                if instructors:
                                    inst_lines = []
                                    for ins in instructors:
                                        req       = ins['requirement_type'].capitalize()
                                        req_color = (
                                            "#27AE60"
                                            if ins['requirement_type'] == 'required'
                                            else "#E67E22"
                                        )
                                        inst_lines.append(
                                            f"<span style='color:{req_color};'>"
                                            f"Dr. {ins['first_name']} "
                                            f"{ins['last_name']} "
                                            f"({req})"
                                            f"</span>"
                                        )
                                    inst_str = "<br>".join(inst_lines)
                                else:
                                    inst_str = (
                                        "<span style='color:#95A5A6;'>N/A</span>"
                                    )

                                # ── Fetch review count ──
                                cursor.execute("""
                                    SELECT COUNT(*) as cnt FROM reviews
                                    WHERE book_id = %s
                                """, (book['book_id'],))
                                rev_cnt = cursor.fetchone()['cnt']
                                review_label = (
                                    f"{rev_cnt} Review"
                                    f"{'s' if rev_cnt != 1 else ''}"
                                )

                                # ── Book Details Card ──
                                st.markdown(f"""
                                <div style="border:1px solid #E5E7E9;
                                            border-radius:12px; padding:15px;
                                            margin-bottom:10px; background:white;
                                            box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                                    <h4 style="color:#2C3E50; margin-bottom:5px;
                                               font-size:15px; line-height:1.3;">
                                        {book['title']}
                                    </h4>
                                    <p style="color:#7F8C8D; font-size:12px;
                                              margin:3px 0;">
                                        ISBN: {book['isbn'] or 'N/A'}
                                    </p>
                                    <p style="font-size:12px;
                                              margin:3px 0; line-height:1.6;">
                                        👨&#8205;🏫 {inst_str}
                                    </p>
                                    <p style="color:#27AE60; font-size:22px;
                                              font-weight:700; margin:8px 0;">
                                        &#8377;{book['price']}
                                    </p>
                                    <p style="font-size:11px; color:#95A5A6;
                                              margin:3px 0;">
                                        {book['book_type'].upper()} |
                                        {book['format'].upper()} |
                                        {book['purchase_option'].upper()}
                                    </p>
                                    <p style="font-size:11px; color:#95A5A6;
                                              margin:3px 0;">
                                        &#11088; {book['avg_rating']} |
                                        Stock: {book['quantity']} |
                                        &#128172; {review_label}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)

                                # ── Check eligibility ──
                                can_review      = book['book_id'] in shipped_book_ids
                                already_reviewed = book['book_id'] in reviewed_book_ids

                                if can_review and not already_reviewed:
                                    # ── Show View, Cart, Rate ──
                                    bcol1, bcol2, bcol3 = st.columns(3)
                                    with bcol1:
                                        if st.button(
                                            "View",
                                            key=f"view_{book['book_id']}"
                                        ):
                                            st.session_state['view_book_id'] = book['book_id']
                                            st.rerun()
                                    with bcol2:
                                        if st.button(
                                            "Cart",
                                            key=f"cart_{book['book_id']}"
                                        ):
                                            add_to_cart(
                                                user['user_id'],
                                                book['book_id'],
                                                book['purchase_option']
                                            )
                                            st.session_state['toast_message'] = "Book added to cart!"
                                            st.session_state['toast_icon']    = "🛒"
                                            st.rerun()
                                    with bcol3:
                                        if st.button(
                                            "Rate",
                                            key=f"review_{book['book_id']}"
                                        ):
                                            st.session_state['review_book']       = book['book_id']
                                            st.session_state['review_book_title'] = book['title']

                                elif can_review and already_reviewed:
                                    # ── Show View, Cart only + reviewed badge ──
                                    bcol1, bcol2 = st.columns(2)
                                    with bcol1:
                                        if st.button(
                                            "View",
                                            key=f"view_{book['book_id']}"
                                        ):
                                            st.session_state['view_book_id'] = book['book_id']
                                            st.rerun()
                                    with bcol2:
                                        if st.button(
                                            "Cart",
                                            key=f"cart_{book['book_id']}"
                                        ):
                                            add_to_cart(
                                                user['user_id'],
                                                book['book_id'],
                                                book['purchase_option']
                                            )
                                            st.session_state['toast_message'] = "Book added to cart!"
                                            st.session_state['toast_icon']    = "🛒"
                                            st.rerun()
                                    # ── Already reviewed badge ──
                                    st.markdown(
                                        "<p style='color:#27AE60; font-size:12px; "
                                        "margin:4px 0;'>Already Reviewed</p>",
                                        unsafe_allow_html=True
                                    )

                                else:
                                    # ── Show View, Cart only ──
                                    bcol1, bcol2 = st.columns(2)
                                    with bcol1:
                                        if st.button(
                                            "View",
                                            key=f"view_{book['book_id']}"
                                        ):
                                            st.session_state['view_book_id'] = book['book_id']
                                            st.rerun()
                                    with bcol2:
                                        if st.button(
                                            "Cart",
                                            key=f"cart_{book['book_id']}"
                                        ):
                                            add_to_cart(
                                                user['user_id'],
                                                book['book_id'],
                                                book['purchase_option']
                                            )
                                            st.session_state['toast_message'] = "Book added to cart!"
                                            st.session_state['toast_icon']    = "🛒"
                                            st.rerun()
            else:
                st.info("📭 No books available at the moment. Check back later!")

            # ── Review Form ──
            if 'review_book' in st.session_state:
                st.markdown("---")
                st.subheader(
                    f"Write Review for: "
                    f"{st.session_state.get('review_book_title', '')}"
                )
                with st.form("review_form"):
                    rating      = st.slider("Rating", 1, 5, 3)
                    review_text = st.text_area("Your Review")
                    col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
                    with col_r2:
                        if st.form_submit_button(
                            "Submit Review",
                            use_container_width=True,
                            type="primary"
                        ):
                            cursor2 = conn.cursor()
                            cursor2.execute("""
                                INSERT INTO reviews
                                    (book_id, student_id, rating, review_text)
                                VALUES (%s, %s, %s, %s)
                            """, (
                                st.session_state['review_book'],
                                user['user_id'], rating, review_text
                            ))
                            cursor2.execute("""
                                UPDATE books SET avg_rating = (
                                    SELECT AVG(rating) FROM reviews
                                    WHERE book_id = %s
                                ) WHERE book_id = %s
                            """, (
                                st.session_state['review_book'],
                                st.session_state['review_book']
                            ))
                            conn.commit()
                            cursor2.close()
                            del st.session_state['review_book']
                            del st.session_state['review_book_title']
                            st.session_state['toast_message'] = "Review submitted!"
                            st.session_state['toast_icon']    = "🎉"
                            st.rerun()

            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   MY CART
    # ══════════════════════════════════════
    elif selected == "My Cart":
        st.title("My Cart")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT cart_id FROM carts WHERE student_id = %s",
                (user['user_id'],)
            )
            cart = cursor.fetchone()
            if cart:
                cursor.execute("""
                    SELECT ci.cart_item_id, ci.quantity, ci.purchase_option,
                           b.title, b.price, b.book_id,
                           b.quantity as stock, b.cover_image
                    FROM cart_items ci
                    JOIN books b ON ci.book_id = b.book_id
                    WHERE ci.cart_id = %s
                """, (cart['cart_id'],))
                items = cursor.fetchall()
                if items:
                    total = 0
                    for item in items:
                        col1, col2, col3, col4, col5 = st.columns([1, 3, 1, 1, 1])
                        with col1:
                            if item.get('cover_image'):
                                st.markdown(f"""
                                <img src="{item['cover_image']}"
                                     style="width:60px; height:80px;
                                            object-fit:cover;
                                            border-radius:6px;">
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style="width:60px; height:80px;
                                            background:linear-gradient(135deg,#3498DB,#2C3E50);
                                            border-radius:6px; display:flex;
                                            align-items:center; justify-content:center;">
                                    <span style="font-size:20px;"></span>
                                </div>
                                """, unsafe_allow_html=True)
                        with col2:
                            st.write(f"**{item['title']}**")
                            st.caption(f"Option: {item['purchase_option'].upper()}")
                        with col3:
                            st.write(f"₹{item['price']}")
                        with col4:
                            st.write(f"Qty: {item['quantity']}")
                        with col5:
                            if st.button(
                                "🗑️",
                                key=f"rm_{item['cart_item_id']}"
                            ):
                                cursor.execute(
                                    "DELETE FROM cart_items WHERE cart_item_id = %s",
                                    (item['cart_item_id'],)
                                )
                                conn.commit()
                                st.session_state['toast_message'] = "Changes Updated! Item removed."
                                st.session_state['toast_icon']    = "🗑️"
                                st.rerun()
                        total += float(item['price']) * item['quantity']
                        st.markdown("---")

                    st.markdown(f"### Total: ₹{total:.2f}")
                    st.subheader("Checkout")
                    with st.form("checkout_form"):
                        shipping  = st.selectbox(
                            "Shipping Type", ["standard", "2-day", "1-day"]
                        )
                        cc_number = st.text_input("Credit Card Number", max_chars=16)
                        cc_exp    = st.text_input("Expiration (MM/YY)", max_chars=5)
                        cc_name   = st.text_input("Card Holder Name")
                        cc_type   = st.selectbox(
                            "Card Type",
                            ["Visa", "MasterCard", "Amex", "Discover", "RuPay"]
                        )
                        if st.form_submit_button(
                            "Place Order",
                            use_container_width=True,
                            type="primary"
                        ):
                            if not cc_number or not cc_exp or not cc_name:
                                st.error("Please fill all payment details")
                            else:
                                cursor.execute("""
                                    INSERT INTO orders
                                        (student_id, shipping_type, cc_number,
                                         cc_expiration, cc_holder_name,
                                         cc_type, total_amount)
                                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                                """, (
                                    user['user_id'], shipping, cc_number,
                                    cc_exp, cc_name, cc_type, total
                                ))
                                order_id = cursor.lastrowid
                                for item in items:
                                    cursor.execute("""
                                        INSERT INTO order_items
                                            (order_id, book_id, quantity,
                                             price, purchase_option)
                                        VALUES (%s,%s,%s,%s,%s)
                                    """, (
                                        order_id, item['book_id'],
                                        item['quantity'], item['price'],
                                        item['purchase_option']
                                    ))
                                    cursor.execute(
                                        "UPDATE books SET quantity = quantity - %s WHERE book_id = %s",
                                        (item['quantity'], item['book_id'])
                                    )
                                cursor.execute(
                                    "DELETE FROM cart_items WHERE cart_id = %s",
                                    (cart['cart_id'],)
                                )
                                conn.commit()
                                st.session_state['toast_message'] = f"Changes Updated! Order #{order_id} placed!"
                                st.session_state['toast_icon']    = "🎉"
                                st.rerun()
                else:
                    st.info("Your cart is empty. Browse books to add items!")
            cursor.close()
            conn.close()

        # ══════════════════════════════════════
    #   MY ORDERS
    # ══════════════════════════════════════
    elif selected == "My Orders":
        st.title("My Orders")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM orders WHERE student_id = %s
                ORDER BY date_created DESC
            """, (user['user_id'],))
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
                        f"{status_icons.get(order['order_status'], '⚪')} "
                        f"{order['order_status'].upper()} — "
                        f"₹{order['total_amount']}"
                    ):
                        st.write(
                            f"**Date:** "
                            f"{order['date_created'].strftime('%d %b %Y %H:%M')}"
                        )
                        st.write(f"**Shipping:** {order['shipping_type']}")
                        st.write(f"**Status:** {order['order_status']}")

                        # ── Fetch order items ──
                        cursor.execute("""
                            SELECT oi.*, b.title, b.cover_image
                            FROM order_items oi
                            JOIN books b ON oi.book_id = b.book_id
                            WHERE oi.order_id = %s
                        """, (order['order_id'],))
                        items = cursor.fetchall()

                        if not items:
                            st.info("No items found for this order.")
                        else:
                            for it in items:
                                col1, col2 = st.columns([1, 5])
                                with col1:
                                    if it.get('cover_image'):
                                        st.markdown(f"""
                                        <img src="{it['cover_image']}"
                                             style="width:50px; height:65px;
                                                    object-fit:cover;
                                                    border-radius:5px;">
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown("""
                                        <div style="width:50px; height:65px;
                                                    background:linear-gradient(135deg,#3498DB,#2C3E50);
                                                    border-radius:5px; display:flex;
                                                    align-items:center;
                                                    justify-content:center;">
                                            <span style="font-size:16px;"></span>
                                        </div>
                                        """, unsafe_allow_html=True)
                                with col2:
                                    st.write(
                                        f"**{it['title']}** — "
                                        f"Qty: {it['quantity']} — "
                                        f"₹{it['price']} ({it['purchase_option']})"
                                    )

                                # ── Write Review only if shipped ──
                                if order['order_status'] == 'shipped':
                                    cursor.execute("""
                                        SELECT review_id FROM reviews
                                        WHERE book_id = %s AND student_id = %s
                                    """, (it['book_id'], user['user_id']))
                                    already_reviewed = cursor.fetchone()

                                    if already_reviewed:
                                        st.success("Already Reviewed")
                                    else:
                                        if st.button(
                                            f"Write Review for '{it['title']}'",
                                            key=f"review_order_{order['order_id']}_{it['book_id']}"
                                        ):
                                            st.session_state['review_book']       = it['book_id']
                                            st.session_state['review_book_title'] = it['title']
                                            st.session_state['review_order_id']   = order['order_id']

                            # ── Inline Review Form ──
                            # ── Only show for THIS order ──
                            if (
                                st.session_state.get('review_order_id') == order['order_id'] and
                                st.session_state.get('review_book') is not None and
                                st.session_state.get('review_book') in
                                [it['book_id'] for it in items]
                            ):
                                st.markdown("---")
                                st.subheader(
                                    f"Write Review for: "
                                    f"{st.session_state.get('review_book_title', '')}"
                                )
                                form_key = (
                                    f"order_review_form_"
                                    f"{order['order_id']}_"
                                    f"{st.session_state.get('review_book', 0)}"
                                )
                                with st.form(form_key):
                                    rating      = st.slider("Rating", 1, 5, 3)
                                    review_text = st.text_area("Your Review")
                                    col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
                                    with col_r2:
                                        if st.form_submit_button(
                                            "Submit Review",
                                            use_container_width=True,
                                            type="primary"
                                        ):
                                            try:
                                                cursor2 = conn.cursor()
                                                cursor2.execute("""
                                                    INSERT INTO reviews
                                                        (book_id, student_id,
                                                         rating, review_text)
                                                    VALUES (%s, %s, %s, %s)
                                                """, (
                                                    st.session_state['review_book'],
                                                    user['user_id'],
                                                    rating, review_text
                                                ))
                                                cursor2.execute("""
                                                    UPDATE books
                                                    SET avg_rating = (
                                                        SELECT AVG(rating)
                                                        FROM reviews
                                                        WHERE book_id = %s
                                                    ) WHERE book_id = %s
                                                """, (
                                                    st.session_state['review_book'],
                                                    st.session_state['review_book']
                                                ))
                                                conn.commit()
                                                cursor2.close()
                                                # ── Clear review session keys ──
                                                for k in [
                                                    'review_book',
                                                    'review_book_title',
                                                    'review_order_id',
                                                    'review_from_order'
                                                ]:
                                                    if k in st.session_state:
                                                        del st.session_state[k]
                                                st.session_state['toast_message'] = "Review submitted!"
                                                st.session_state['toast_icon']    = "🎉"
                                                st.rerun()
                                            except Exception as e:
                                                conn.rollback()
                                                st.error(f"Error: {e}")

                        # ── Cancel Button ──
                        # ── Only when status is 'new' ──
                        if order['order_status'] == 'new':
                            st.markdown("")
                            st.info(
                                "ℹ️ You can only cancel orders "
                                "that are still **New**. "
                                "For other cancellations, please "
                                "contact Customer Support."
                            )
                            if st.button(
                                f"Cancel Order #{order['order_id']}",
                                key=f"cancel_{order['order_id']}"
                            ):
                                cursor.execute(
                                    "UPDATE orders SET order_status = 'canceled' "
                                    "WHERE order_id = %s",
                                    (order['order_id'],)
                                )
                                # ── Restore stock ──
                                cursor.execute("""
                                    SELECT oi.book_id, oi.quantity
                                    FROM order_items oi
                                    WHERE oi.order_id = %s
                                """, (order['order_id'],))
                                order_items_to_restore = cursor.fetchall()
                                for it in order_items_to_restore:
                                    cursor.execute(
                                        "UPDATE books SET quantity = quantity + %s "
                                        "WHERE book_id = %s",
                                        (it['quantity'], it['book_id'])
                                    )
                                conn.commit()
                                st.session_state['toast_message'] = (
                                    f"Changes Updated! "
                                    f"Order #{order['order_id']} canceled."
                                )
                                st.session_state['toast_icon'] = "🎉"
                                st.rerun()
            else:
                st.info("No orders yet.")
            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   MY REVIEWS
    # ══════════════════════════════════════
    elif selected == "My Reviews":
        st.title("My Reviews")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.*, b.title, b.cover_image FROM reviews r
                JOIN books b ON r.book_id = b.book_id
                WHERE r.student_id = %s ORDER BY r.created_at DESC
            """, (user['user_id'],))
            reviews = cursor.fetchall()
            if reviews:
                for rev in reviews:
                    rev_date = rev['created_at'].strftime('%d %b %Y')
                    stars    = '⭐' * rev['rating']
                    with st.expander(
                        f"{stars} — {rev['title']} — {rev_date}"
                    ):
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            if rev.get('cover_image'):
                                st.markdown(f"""
                                <img src="{rev['cover_image']}"
                                     style="width:80px; height:110px;
                                            object-fit:cover;
                                            border-radius:8px;
                                            box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style="width:80px; height:110px;
                                            background:linear-gradient(135deg,#3498DB,#2C3E50);
                                            border-radius:8px; display:flex;
                                            align-items:center;
                                            justify-content:center;">
                                    <span style="font-size:28px;"></span>
                                </div>
                                """, unsafe_allow_html=True)
                        with col2:
                            st.write(f"**Book:** {rev['title']}")
                            st.write(
                                f"**Rating:** {stars} ({rev['rating']}/5)"
                            )
                            st.write(
                                f"**Review:** "
                                f"{rev['review_text'] or 'No text provided.'}"
                            )
                            st.write(f"**Date:** {rev_date}")
            else:
                st.info("You haven't written any reviews yet.")
            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   TROUBLE TICKETS
    # ══════════════════════════════════════
    elif selected == "Trouble Tickets":
        st.title("My Trouble Tickets")
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)

            st.subheader("Submit New Ticket")
            with st.form("student_ticket_form"):
                t_cat   = st.selectbox(
                    "Category",
                    ["user_profile", "products", "cart", "orders", "other"]
                )
                t_title = st.text_input("Title *")
                t_desc  = st.text_area("Problem Description *")
                if st.form_submit_button(
                    "Submit Ticket",
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
                            VALUES (%s, %s, %s, 'new', %s, 'student')
                        """, (t_cat, t_title, t_desc, user['user_id']))
                        conn.commit()
                        st.session_state['toast_message'] = "Changes Updated! Ticket submitted!"
                        st.session_state['toast_icon']    = "🎉"
                        st.rerun()

            st.markdown("---")
            st.subheader("My Tickets")
            cursor.execute("""
                SELECT * FROM trouble_tickets
                WHERE created_by = %s ORDER BY date_logged DESC
            """, (user['user_id'],))
            tickets = cursor.fetchall()
            if tickets:
                for t in tickets:
                    status_colors = {
                        "new": "🟢", "assigned": "🔵",
                        "in-process": "🟡", "completed": "✅"
                    }
                    with st.expander(
                        f"#{t['ticket_id']} — {t['title']} — "
                        f"{status_colors.get(t['ticket_status'], '⚪')} "
                        f"{t['ticket_status']}"
                    ):
                        st.write(f"**Category:** {t['category']}")
                        st.write(f"**Status:** {t['ticket_status']}")
                        st.write(f"**Problem:** {t['problem_description']}")
                        if t['solution_description']:
                            st.success(
                                f"**Solution:** {t['solution_description']}"
                            )
                        st.write(
                            f"**Logged:** "
                            f"{t['date_logged'].strftime('%d %b %Y %H:%M')}"
                        )
                        if t['completion_date']:
                            st.write(
                                f"**Completed:** "
                                f"{t['completion_date'].strftime('%d %b %Y %H:%M')}"
                            )
            else:
                st.info("No tickets submitted yet.")
            cursor.close()
            conn.close()

    # ══════════════════════════════════════
    #   PROFILE
    # ══════════════════════════════════════
    elif selected == "Profile":
        show_profile(user)

    show_footer()


# ══════════════════════════════════════
#   BOOK DETAIL PAGE
# ══════════════════════════════════════
def show_book_detail(user):
    book_id = st.session_state.get('view_book_id')

    conn = get_connection()
    if not conn:
        st.error("Database connection failed.")
        return

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT b.*, c.name as category_name
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.category_id
        WHERE b.book_id = %s
    """, (book_id,))
    book = cursor.fetchone()

    if not book:
        st.error("Book not found.")
        if st.button("← Back to Browse"):
            del st.session_state['view_book_id']
            st.rerun()
        return

    # ── Check shipped ──
    cursor.execute("""
        SELECT COUNT(*) as cnt
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.student_id   = %s
          AND oi.book_id     = %s
          AND o.order_status = 'shipped'
    """, (user['user_id'], book_id))
    can_review = cursor.fetchone()['cnt'] > 0

    # ── Check already reviewed ──
    cursor.execute("""
        SELECT review_id FROM reviews
        WHERE book_id = %s AND student_id = %s
    """, (book_id, user['user_id']))
    already_reviewed = cursor.fetchone()

    # ── Back Button ──
    if st.button("← Back to Browse Books"):
        del st.session_state['view_book_id']
        if 'review_book' in st.session_state:
            del st.session_state['review_book']
        if 'review_book_title' in st.session_state:
            del st.session_state['review_book_title']
        st.rerun()

    st.markdown("---")

    col1, col2 = st.columns([1, 2])
    with col1:
        if book.get('cover_image'):
            st.markdown(f"""
            <div style="text-align:center;">
                <img src="{book['cover_image']}"
                     style="width:100%; max-width:220px;
                            height:300px; object-fit:cover;
                            border-radius:12px;
                            box-shadow:0 6px 20px rgba(0,0,0,0.2);"
                     alt="{book['title']}">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="width:100%; height:300px;
                        background:linear-gradient(135deg,#3498DB,#2C3E50);
                        border-radius:12px; display:flex;
                        align-items:center; justify-content:center;
                        box-shadow:0 6px 20px rgba(0,0,0,0.2);">
                <span style="font-size:80px;"></span>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <h2 style="color:#2C3E50; margin-bottom:5px;">
            {book['title']}
        </h2>
        """, unsafe_allow_html=True)

        cursor.execute(
            "SELECT author_name FROM book_authors WHERE book_id = %s",
            (book_id,)
        )
        authors = cursor.fetchall()
        if authors:
            st.markdown(
                f"**Author(s):** "
                f"{', '.join(a['author_name'] for a in authors)}"
            )
        else:
            st.markdown("**✍️ Author(s):** N/A")

        st.markdown(f"**ISBN:** {book['isbn'] or 'N/A'}")
        st.markdown(f"**Publisher:** {book['publisher'] or 'N/A'}")
        st.markdown(
            f"**Publication Date:** {book['publication_date'] or 'N/A'}"
        )
        st.markdown(f"**Edition:** {book['edition']}")
        st.markdown(f"**Language:** {book['language']}")
        st.markdown(f"**Category:** {book['category_name'] or 'N/A'}")

        cursor.execute(
            "SELECT keyword FROM book_keywords WHERE book_id = %s",
            (book_id,)
        )
        keywords = cursor.fetchall()
        if keywords:
            st.markdown(
                f"**Keywords:** "
                f"{', '.join(k['keyword'] for k in keywords)}"
            )

        cursor.execute(
            "SELECT COUNT(*) as cnt FROM reviews WHERE book_id = %s",
            (book_id,)
        )
        review_count = cursor.fetchone()['cnt']
        review_label = (
            f"{review_count} Review{'s' if review_count != 1 else ''}"
        )

        st.markdown("---")

        st.markdown(
            f"<div style='background:#EBF5FB; border-radius:10px; padding:15px;'>"
            f"<p style='font-size:28px; font-weight:700; "
            f"color:#27AE60; margin:0;'>&#8377;{book['price']}</p>"
            f"<p style='font-size:13px; color:#7F8C8D; margin:5px 0 0 0;'>"
            f"{book['book_type'].upper()} | {book['format'].upper()} | "
            f"{book['purchase_option'].upper()} | "
            f"&#11088; {book['avg_rating']} | "
            f"Stock: {book['quantity']} | "
            f"&#128172; {review_label}</p></div>",
            unsafe_allow_html=True
        )

        st.markdown("")

        if can_review and not already_reviewed:
            bcol1, bcol2, bcol3 = st.columns(3)
            with bcol1:
                if st.button(
                    "Add to Cart",
                    key=f"detail_cart_{book_id}",
                    use_container_width=True,
                    type="primary"
                ):
                    add_to_cart(
                        user['user_id'], book_id, book['purchase_option']
                    )
                    st.session_state['toast_message'] = "Book added to cart!"
                    st.session_state['toast_icon']    = "🛒"
                    st.rerun()
            with bcol2:
                if st.button(
                    "Write Review",
                    key=f"detail_review_{book_id}",
                    use_container_width=True
                ):
                    st.session_state['review_book']       = book_id
                    st.session_state['review_book_title'] = book['title']
            with bcol3:
                st.success("Purchase verified")

        elif can_review and already_reviewed:
            bcol1, bcol2 = st.columns(2)
            with bcol1:
                if st.button(
                    "Add to Cart",
                    key=f"detail_cart_{book_id}",
                    use_container_width=True,
                    type="primary"
                ):
                    add_to_cart(
                        user['user_id'], book_id, book['purchase_option']
                    )
                    st.session_state['toast_message'] = "Book added to cart!"
                    st.session_state['toast_icon']    = "🛒"
                    st.rerun()
            with bcol2:
                st.success("Already Reviewed")

        else:
            bcol1, bcol2 = st.columns(2)
            with bcol1:
                if st.button(
                    "Add to Cart",
                    key=f"detail_cart_{book_id}",
                    use_container_width=True,
                    type="primary"
                ):
                    add_to_cart(
                        user['user_id'], book_id, book['purchase_option']
                    )
                    st.session_state['toast_message'] = "Book added to cart!"
                    st.session_state['toast_icon']    = "🛒"
                    st.rerun()
            with bcol2:
                st.info("Purchase & ship to review")

    st.markdown("---")

    # ══════════════════════════════════════
    #   COURSES & INSTRUCTORS
    # ══════════════════════════════════════
    st.subheader("Courses & Instructors")
    cursor.execute("""
        SELECT cb.requirement_type, cb.year, cb.semester,
               c.course_name,
               u.name as university_name,
               i.first_name as inst_fn, i.last_name as inst_ln,
               d.name as dept_name
        FROM course_books cb
        JOIN courses c ON cb.course_id = c.course_id
        LEFT JOIN universities u ON c.university_id = u.university_id
        JOIN instructors i ON cb.instructor_id = i.instructor_id
        LEFT JOIN departments d ON i.department_id = d.department_id
        WHERE cb.book_id = %s
    """, (book_id,))
    course_links = cursor.fetchall()

    if course_links:
        for cl in course_links:
            dept_str  = f"({cl['dept_name']})" if cl['dept_name'] else ''
            req_type  = cl['requirement_type']
            uni_name  = cl['university_name'] or 'N/A'
            cl_year   = cl['year']
            cl_sem    = cl['semester'] or 'N/A'
            inst_name = f"Dr. {cl['inst_fn']} {cl['inst_ln']}"

            with st.expander(
                f"{cl['course_name']} — {uni_name} ({cl_year})"
            ):
                st.write(f"**Course:** {cl['course_name']}")
                st.write(f"**University:** {uni_name}")
                st.write(f"**Year / Semester:** {cl_year} / {cl_sem}")
                st.write(
                    f"**Instructor:** {inst_name} {dept_str}"
                )
                if req_type == 'required':
                    st.success("📌 REQUIRED")
                else:
                    st.warning("📌 RECOMMENDED")
    else:
        st.info("This book is not linked to any course yet.")

    st.markdown("---")

    # ══════════════════════════════════════
    #   REVIEWS SECTION
    # ══════════════════════════════════════
    cursor.execute(
        "SELECT COUNT(*) as cnt FROM reviews WHERE book_id = %s",
        (book_id,)
    )
    total_reviews = cursor.fetchone()['cnt']
    st.subheader(f"Student Reviews ({total_reviews})")

    cursor.execute("""
        SELECT r.*, u.first_name, u.last_name
        FROM reviews r
        JOIN users u ON r.student_id = u.user_id
        WHERE r.book_id = %s
        ORDER BY r.created_at DESC
    """, (book_id,))
    reviews = cursor.fetchall()

    if reviews:
        for rev in reviews:
            rev_date   = rev['created_at'].strftime('%d %b %Y')
            rev_rating = int(rev['rating'])
            rev_stars  = '⭐' * rev_rating
            rev_name   = f"{rev['first_name']} {rev['last_name']}"
            rev_text   = rev['review_text'] or 'No review text.'

            with st.expander(
                f"{rev_stars} — {rev_name} — {rev_date}"
            ):
                st.write(f"**Rating:** {rev_stars} ({rev_rating}/5)")
                st.write(f"**Review:** {rev_text}")
                st.caption(f"{rev_date}")
    else:
        st.info(
            "No reviews yet. "
            "Purchase and receive this book to review it!"
        )

    # ── Inline Review Form ──
    if (
        st.session_state.get('review_book') == book_id and
        can_review and
        not already_reviewed
    ):
        st.markdown("---")
        st.subheader(f"✍️ Write Your Review for: {book['title']}")
        with st.form("detail_review_form"):
            rating      = st.slider("Rating", 1, 5, 3)
            review_text = st.text_area("Your Review")
            col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
            with col_r2:
                if st.form_submit_button(
                    "Submit Review",
                    use_container_width=True,
                    type="primary"
                ):
                    cursor2 = conn.cursor()
                    cursor2.execute("""
                        INSERT INTO reviews
                            (book_id, student_id, rating, review_text)
                        VALUES (%s, %s, %s, %s)
                    """, (book_id, user['user_id'], rating, review_text))
                    cursor2.execute("""
                        UPDATE books SET avg_rating = (
                            SELECT AVG(rating) FROM reviews
                            WHERE book_id = %s
                        ) WHERE book_id = %s
                    """, (book_id, book_id))
                    conn.commit()
                    cursor2.close()
                    del st.session_state['review_book']
                    if 'review_book_title' in st.session_state:
                        del st.session_state['review_book_title']
                    st.session_state['toast_message'] = "Review submitted!"
                    st.session_state['toast_icon']    = "🎉"
                    st.rerun()

    cursor.close()
    conn.close()
    show_footer()


# ══════════════════════════════════════
#   ADD TO CART HELPER
# ══════════════════════════════════════
def add_to_cart(student_id, book_id, purchase_option):
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT cart_id FROM carts WHERE student_id = %s",
            (student_id,)
        )
        cart = cursor.fetchone()
        if not cart:
            cursor.execute(
                "INSERT INTO carts (student_id) VALUES (%s)",
                (student_id,)
            )
            cart_id = cursor.lastrowid
        else:
            cart_id = cart['cart_id']
        cursor.execute(
            "SELECT cart_item_id FROM cart_items "
            "WHERE cart_id = %s AND book_id = %s",
            (cart_id, book_id)
        )
        existing = cursor.fetchone()
        if existing:
            cursor.execute(
                "UPDATE cart_items SET quantity = quantity + 1 "
                "WHERE cart_item_id = %s",
                (existing['cart_item_id'],)
            )
        else:
            cursor.execute(
                "INSERT INTO cart_items "
                "(cart_id, book_id, quantity, purchase_option) "
                "VALUES (%s,%s,1,%s)",
                (cart_id, book_id, purchase_option)
            )
        conn.commit()
        cursor.close()
        conn.close()


# ══════════════════════════════════════
#   SHOW PROFILE
# ══════════════════════════════════════
def show_profile(user):
    st.title("My Profile")

    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE user_id = %s",
            (user['user_id'],)
        )
        fresh_user = cursor.fetchone()

        if fresh_user['role'] == 'student':
            cursor.execute(
                "SELECT * FROM student_details WHERE student_id = %s",
                (fresh_user['user_id'],)
            )
            details = cursor.fetchone()

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
                st.subheader("Academic Information")
                if details:
                    st.write(f"**University:** {details['university'] or 'N/A'}")
                    st.write(f"**Major:** {details['major'] or 'N/A'}")
                    st.write(f"**Status:** {details['student_status'] or 'N/A'}")
                    st.write(f"**Year:** {details['year_of_study'] or 'N/A'}")
                    st.write(f"**DOB:** {details['date_of_birth'] or 'N/A'}")
                else:
                    st.info("No academic details found.")

        else:
            cursor.execute(
                "SELECT * FROM employee_details WHERE employee_id = %s",
                (fresh_user['user_id'],)
            )
            details = cursor.fetchone()

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
                st.subheader("💼 Employment Information")
                if details:
                    st.write(f"**Gender:** {details['gender'] or 'N/A'}")
                    st.write(f"**Salary:** ₹{details['salary'] or '0.00'}")
                    st.write(
                        f"**Aadhaar:** XXXX-XXXX-"
                        f"{details['aadhaar_number'][-4:] if details['aadhaar_number'] else 'N/A'}"
                    )
                    st.write(f"**Employee ID:** {details['employee_id']}")
                else:
                    st.info("No employment details found.")

        st.markdown("---")
        st.subheader("Change Profile")

        with st.form("change_profile_form", clear_on_submit=False):

            st.markdown("##### Personal Details")
            col1, col2 = st.columns(2)
            with col1:
                new_first = st.text_input(
                    "First Name *",
                    value=fresh_user['first_name'],
                    key="cp_fn"
                )
                new_email = st.text_input(
                    "Email *",
                    value=fresh_user['email'],
                    key="cp_email"
                )
                new_phone = st.text_input(
                    "Phone",
                    value=fresh_user['phone'] or "",
                    key="cp_phone"
                )
            with col2:
                new_last = st.text_input(
                    "Last Name *",
                    value=fresh_user['last_name'],
                    key="cp_ln"
                )
                new_password = st.text_input(
                    "New Password (leave blank to keep current)",
                    type="password",
                    placeholder="Enter new password",
                    key="cp_pass"
                )
                confirm_password = st.text_input(
                    "Confirm New Password",
                    type="password",
                    placeholder="Confirm new password",
                    key="cp_confirm"
                )
            new_address = st.text_area(
                "Address",
                value=fresh_user['address'] or "",
                key="cp_addr"
            )

            if fresh_user['role'] == 'student':
                cursor.execute(
                    "SELECT * FROM student_details WHERE student_id = %s",
                    (fresh_user['user_id'],)
                )
                std = cursor.fetchone()
                st.markdown("##### Academic Details")
                col3, col4 = st.columns(2)
                with col3:
                    new_university = st.text_input(
                        "University",
                        value=std['university'] or "" if std else "",
                        key="cp_uni"
                    )
                    status_options = ["undergraduate", "graduate"]
                    current_status = (
                        std['student_status'] if std else "undergraduate"
                    )
                    new_status = st.selectbox(
                        "Student Status",
                        status_options,
                        index=status_options.index(current_status),
                        key="cp_status"
                    )
                with col4:
                    new_major = st.text_input(
                        "Major",
                        value=std['major'] or "" if std else "",
                        key="cp_major"
                    )
                    new_year = st.selectbox(
                        "Year of Study",
                        [1, 2, 3, 4, 5, 6],
                        index=(std['year_of_study'] - 1)
                              if std and std['year_of_study'] else 0,
                        key="cp_year"
                    )

            elif fresh_user['role'] in (
                'customer_support', 'administrator', 'super_admin'
            ):
                cursor.execute(
                    "SELECT * FROM employee_details WHERE employee_id = %s",
                    (fresh_user['user_id'],)
                )
                emp = cursor.fetchone()
                st.markdown("##### 💼 Employment Details")
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
                        key="cp_gender"
                    )
                    new_salary = st.number_input(
                        "Salary (₹)",
                        min_value=0.00,
                        step=1000.00,
                        value=float(emp['salary'])
                              if emp and emp['salary'] else 0.00,
                        format="%.2f",
                        key="cp_salary"
                    )
                with col4:
                    new_aadhaar = st.text_input(
                        "Aadhaar Number *",
                        value=emp['aadhaar_number']
                              if emp and emp['aadhaar_number'] else "",
                        max_chars=12,
                        key="cp_aadhaar"
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
                elif fresh_user['role'] in (
                    'customer_support', 'administrator', 'super_admin'
                ):
                    if not new_aadhaar or len(new_aadhaar) != 12 \
                            or not new_aadhaar.isdigit():
                        st.error("⚠️ Aadhaar must be exactly 12 digits.")
                    else:
                        _save_profile(
                            cursor, conn, fresh_user,
                            new_first, new_last, new_email,
                            new_phone, new_address,
                            new_password, confirm_password,
                            role_extra={
                                'gender':  new_gender,
                                'salary':  new_salary,
                                'aadhaar': new_aadhaar
                            }
                        )
                else:
                    _save_profile(
                        cursor, conn, fresh_user,
                        new_first, new_last, new_email,
                        new_phone, new_address,
                        new_password, confirm_password,
                        role_extra={
                            'university': new_university,
                            'major':      new_major,
                            'status':     new_status,
                            'year':       new_year
                        }
                    )

        cursor.close()
        conn.close()


# ══════════════════════════════════════
#   SAVE PROFILE HELPER
# ══════════════════════════════════════
def _save_profile(cursor, conn, fresh_user,
                  new_first, new_last, new_email,
                  new_phone, new_address,
                  new_password, confirm_password,
                  role_extra):
    try:
        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s AND user_id != %s",
            (new_email, fresh_user['user_id'])
        )
        if cursor.fetchone():
            st.error("This email is already used by another account.")
            return

        if fresh_user['role'] in (
            'customer_support', 'administrator', 'super_admin'
        ):
            cursor.execute("""
                SELECT employee_id FROM employee_details
                WHERE aadhaar_number = %s AND employee_id != %s
            """, (role_extra['aadhaar'], fresh_user['user_id']))
            if cursor.fetchone():
                st.error("This Aadhaar is already used by another account.")
                return

        if new_password:
            import bcrypt
            pw_hash = bcrypt.hashpw(
                new_password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            cursor.execute("""
                UPDATE users
                SET first_name    = %s, last_name     = %s,
                    email         = %s, phone         = %s,
                    address       = %s, password_hash = %s
                WHERE user_id = %s
            """, (
                new_first, new_last, new_email,
                new_phone, new_address, pw_hash,
                fresh_user['user_id']
            ))
        else:
            cursor.execute("""
                UPDATE users
                SET first_name = %s, last_name = %s,
                    email      = %s, phone     = %s,
                    address    = %s
                WHERE user_id = %s
            """, (
                new_first, new_last, new_email,
                new_phone, new_address,
                fresh_user['user_id']
            ))

        if fresh_user['role'] == 'student':
            cursor.execute("""
                UPDATE student_details
                SET university     = %s, major         = %s,
                    student_status = %s, year_of_study = %s
                WHERE student_id = %s
            """, (
                role_extra['university'], role_extra['major'],
                role_extra['status'],    role_extra['year'],
                fresh_user['user_id']
            ))

        elif fresh_user['role'] in (
            'customer_support', 'administrator', 'super_admin'
        ):
            cursor.execute("""
                UPDATE employee_details
                SET gender         = %s,
                    salary         = %s,
                    aadhaar_number = %s
                WHERE employee_id = %s
            """, (
                role_extra['gender'],
                role_extra['salary'],
                role_extra['aadhaar'],
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


# ══════════════════════════════════════
#   FOOTER
# ══════════════════════════════════════
def show_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:20px; color:#7F8C8D;">
        <p style="font-size:14px;">
            &#128218; <strong>GyanPustak</strong> &mdash;
            Your Trusted Online Textbook Platform
        </p>
        <p style="font-size:12px;">
            &#128231; support@gyanpustak.com |
            &#128222; +91-1800-XXX-XXXX
        </p>
        <p style="font-size:11px; color:#BDC3C7;">
            &copy; 2025 GyanPustak. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)
