# 📚 GyanPustak — Online Textbook Platform

> A full-stack e-commerce web application for buying, renting, and managing college textbooks. Built with **Python (Streamlit)** and **MySQL**.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38.0-FF4B4B.svg)](https://streamlit.io/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📖 About

**GyanPustak** is an online textbook platform designed for college students. It allows students to **browse, buy, or rent** textbooks in multiple formats (hardcover, softcover, electronic). The system features a complete **role-based access control** with four user types, a **shopping cart**, **order management**, **review system**, and a **trouble ticket workflow**.

The platform also enables universities to link their courses with required or recommended textbooks, making it easier for students to find exactly what they need.

---

## ✨ Key Features

### 🎓 Student
- Self-registration with academic details
- Browse & search books by title, ISBN, keyword, category, and format
- View detailed book pages with course links, instructors, and reviews
- Add books to cart with **quantity controls (+/−)**
- **Rent books** with flexible duration (1, 2, or 3 months) and dynamic pricing
- Secure checkout with payment details
- Order history tracking with status updates
- Write reviews & ratings (1–5 stars) for shipped books
- Submit and track trouble support tickets
- Profile management with password reset

### 🛠️ Customer Support
- Dashboard with ticket statistics and admin workload overview
- View all tickets and assign "new" tickets to administrators
- Create new tickets for technical issues
- Cancel student orders on request

### ⚙️ Administrator
- Complete book inventory management (CRUD + stock updates)
- Manage categories, subcategories, universities, departments, instructors
- Create courses and link books with requirement types
- Handle assigned/in-process trouble tickets with solutions
- Manage order statuses and process cancellations
- View all student reviews (read-only)

### 👑 Super Administrator
- Add new Customer Support and Administrator employees
- Manage employee salaries and accounts
- View all registered users with activity statistics
- System-wide dashboard with full metrics

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Python, Streamlit 1.38.0, streamlit-option-menu |
| **Backend** | MySQL 8.0+, mysql-connector-python 8.3.0 |
| **Authentication** | Bcrypt 4.1.2 (salt-hashed passwords) |
| **Database Design** | 18 normalized tables (3NF / BCNF) |
| **Security** | Parameterized queries, RBAC, Bcrypt hashing |
| **Concurrency** | Pessimistic locking (SELECT ... FOR UPDATE) |
| **Version Control** | Git, GitHub |

---

## 🗄️ Database Schema

The database consists of **18 tables** with proper normalization up to **BCNF**:

| Table | Description |
|-------|-------------|
| users | Central user table (all roles) |
| student_details | Academic info for students |
| employee_details | Employment info for staff |
| universities | University records |
| departments | Academic departments |
| instructors | Instructor profiles |
| courses | Course listings |
| course_departments | Course–Department mapping (M:N) |
| course_instructors | Course–Instructor mapping (M:N) |
| categories | Book categories |
| subcategories | Book subcategories |
| books | Book inventory |
| book_authors | Book–Author mapping |
| book_keywords | Searchable keywords |
| book_subcategories | Book–Subcategory mapping |
| course_books | Course–Book–Instructor mapping |
| reviews | Student reviews & ratings |
| carts | Student shopping carts |
| cart_items | Cart line items |
| orders | Placed orders |
| order_items | Order line items |
| trouble_tickets | Support tickets |
| ticket_status_history | Ticket audit trail |

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0 or higher
- Git

### Step 1: Clone the Repository

    git clone https://github.com/your-username/gyanpustak.git
    cd gyanpustak

### Step 2: Install Dependencies

    pip install -r requirements.txt

### Step 3: Configure Database

Update the MySQL credentials in **database.py** and **create_super_admin.py**:

    DB_CONFIG = {
        'host':     'localhost',
        'user':     'root',
        'password': 'your_mysql_password',
        'database': 'gyanpustak'
    }

### Step 4: Initialize Database & Create Super Admin

    # Run the app once to auto-create database + tables + triggers
    streamlit run app.py
    # Close the app (Ctrl+C)

    # Create the Super Admin account
    python create_super_admin.py

### Step 5: Run the Application

    streamlit run app.py

The app will open in your browser at **http://localhost:8501**

---

## 📁 Project Structure

    gyanpustak/
    ├── app.py                    # Main entry point, routing, session management
    ├── auth.py                   # Login, registration, password reset
    ├── database.py               # DB connection, schema init, triggers
    ├── student.py                # Student dashboard module
    ├── customer_support.py       # Customer support dashboard module
    ├── administrator.py          # Administrator dashboard module
    ├── super_admin.py            # Super admin dashboard module
    ├── create_super_admin.py     # CLI script to create super admin
    ├── requirements.txt          # Python dependencies
    └── README.md                 # Project documentation

---

## 🔐 Security Features

- **Password Hashing:** All passwords stored using Bcrypt with auto-generated salts
- **SQL Injection Prevention:** 100% parameterized queries (%s placeholders)
- **Role-Based Access Control:** Four distinct roles with isolated dashboards
- **Session Management:** Secure session persistence using query parameters
- **Database Constraints:** UNIQUE, ENUM, CHECK, and FOREIGN KEY constraints
- **Trigger Enforcement:** MySQL trigger limits Super Admin to exactly one account

---

## 💰 Rent Pricing Formula

For books with the **rent** purchase option:

    Rent Price = (Full Price / 6) × Number of Months

| Duration | Calculation (₹1000 book) | Rent Price |
|----------|--------------------------|------------|
| 1 Month  | ₹1000 / 6 × 1           | ₹166.67    |
| 2 Months | ₹1000 / 6 × 2           | ₹333.33    |
| 3 Months | ₹1000 / 6 × 3           | ₹500.00    |

---

## 🔄 Concurrency Control

The checkout process uses **pessimistic locking** to prevent overselling:

1. Transaction begins
2. All book rows in cart are locked using SELECT ... FOR UPDATE
3. Stock is validated for each item
4. If insufficient stock → rollback + error message
5. If sufficient → insert order, deduct stock, clear cart, commit

This ensures two students cannot simultaneously purchase more copies than available.

---

## 🎯 User Account Setup

| Role | How to Create |
|------|--------------|
| Super Admin | python create_super_admin.py |
| Administrator | Super Admin → Add Employee |
| Customer Support | Super Admin → Add Employee |
| Student | Self-registration on login page |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (git checkout -b feature/new-feature)
3. Commit your changes (git commit -m 'Add new feature')
4. Push to the branch (git push origin feature/new-feature)
5. Open a Pull Request

---

<p align="center">
  <strong>© 2025 GyanPustak. All rights reserved.</strong><br>
  Built with ❤️ for college students.
</p>
