import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'Krishna@2005',
    'database': 'gyanpustak'
}

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def initialize_database():
    # ── Step 1: Create database if not exists ──
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error creating database: {e}")
        return

    # ── Step 2: Connect to database ──
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()

    # ── Step 3: Create all tables ──
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id       INT AUTO_INCREMENT PRIMARY KEY,
            email         VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role          ENUM('student','customer_support',
                               'administrator','super_admin') NOT NULL,
            first_name    VARCHAR(100) NOT NULL,
            last_name     VARCHAR(100) NOT NULL,
            phone         VARCHAR(20),
            address       TEXT,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS student_details (
            student_id     INT PRIMARY KEY,
            date_of_birth  DATE,
            university     VARCHAR(255),
            major          VARCHAR(255),
            student_status ENUM('undergraduate','graduate')
                           DEFAULT 'undergraduate',
            year_of_study  INT DEFAULT 1,
            FOREIGN KEY (student_id) REFERENCES users(user_id)
                ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS employee_details (
            employee_id    INT PRIMARY KEY,
            gender         ENUM('Male','Female','Other'),
            salary         DECIMAL(12,2),
            aadhaar_number VARCHAR(12) UNIQUE,
            FOREIGN KEY (employee_id) REFERENCES users(user_id)
                ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS universities (
            university_id  INT AUTO_INCREMENT PRIMARY KEY,
            name           VARCHAR(255) NOT NULL,
            address        TEXT,
            rep_first_name VARCHAR(100),
            rep_last_name  VARCHAR(100),
            rep_email      VARCHAR(255),
            rep_phone      VARCHAR(20)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS departments (
            department_id INT AUTO_INCREMENT PRIMARY KEY,
            name          VARCHAR(255) NOT NULL,
            university_id INT,
            FOREIGN KEY (university_id)
                REFERENCES universities(university_id)
                ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS instructors (
            instructor_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name    VARCHAR(100) NOT NULL,
            last_name     VARCHAR(100) NOT NULL,
            university_id INT,
            department_id INT,
            FOREIGN KEY (university_id)
                REFERENCES universities(university_id)
                ON DELETE SET NULL,
            FOREIGN KEY (department_id)
                REFERENCES departments(department_id)
                ON DELETE SET NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS courses (
            course_id     INT AUTO_INCREMENT PRIMARY KEY,
            course_name   VARCHAR(255) NOT NULL,
            university_id INT,
            year          INT,
            semester      VARCHAR(50),
            FOREIGN KEY (university_id)
                REFERENCES universities(university_id)
                ON DELETE SET NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS course_departments (
            course_id     INT,
            department_id INT,
            PRIMARY KEY (course_id, department_id),
            FOREIGN KEY (course_id)
                REFERENCES courses(course_id) ON DELETE CASCADE,
            FOREIGN KEY (department_id)
                REFERENCES departments(department_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS course_instructors (
            course_id     INT,
            instructor_id INT,
            PRIMARY KEY (course_id, instructor_id),
            FOREIGN KEY (course_id)
                REFERENCES courses(course_id) ON DELETE CASCADE,
            FOREIGN KEY (instructor_id)
                REFERENCES instructors(instructor_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS categories (
            category_id INT AUTO_INCREMENT PRIMARY KEY,
            name        VARCHAR(255) NOT NULL UNIQUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS subcategories (
            subcategory_id INT AUTO_INCREMENT PRIMARY KEY,
            name           VARCHAR(255) NOT NULL,
            category_id    INT,
            FOREIGN KEY (category_id)
                REFERENCES categories(category_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS books (
            book_id          INT AUTO_INCREMENT PRIMARY KEY,
            title            VARCHAR(500) NOT NULL,
            isbn             VARCHAR(20) UNIQUE,
            publisher        VARCHAR(255),
            publication_date DATE,
            edition          INT DEFAULT 1,
            language         VARCHAR(50) DEFAULT 'English',
            book_type        ENUM('new','used') DEFAULT 'new',
            purchase_option  ENUM('rent','buy') DEFAULT 'buy',
            format           ENUM('hardcover','softcover','electronic')
                             DEFAULT 'hardcover',
            price            DECIMAL(10,2) DEFAULT 0.00,
            quantity         INT DEFAULT 0,
            category_id      INT,
            avg_rating       DECIMAL(3,2) DEFAULT 0.00,
            cover_image      VARCHAR(500) DEFAULT NULL,
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id)
                REFERENCES categories(category_id) ON DELETE SET NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS book_authors (
            book_id     INT,
            author_name VARCHAR(255),
            PRIMARY KEY (book_id, author_name),
            FOREIGN KEY (book_id)
                REFERENCES books(book_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS book_subcategories (
            book_id        INT,
            subcategory_id INT,
            PRIMARY KEY (book_id, subcategory_id),
            FOREIGN KEY (book_id)
                REFERENCES books(book_id) ON DELETE CASCADE,
            FOREIGN KEY (subcategory_id)
                REFERENCES subcategories(subcategory_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS book_keywords (
            book_id INT,
            keyword VARCHAR(100),
            PRIMARY KEY (book_id, keyword),
            FOREIGN KEY (book_id)
                REFERENCES books(book_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS course_books (
            course_id        INT,
            book_id          INT,
            instructor_id    INT,
            year             INT,
            semester         VARCHAR(50),
            requirement_type ENUM('required','recommended')
                             DEFAULT 'required',
            PRIMARY KEY (course_id, book_id, instructor_id),
            FOREIGN KEY (course_id)
                REFERENCES courses(course_id) ON DELETE CASCADE,
            FOREIGN KEY (book_id)
                REFERENCES books(book_id) ON DELETE CASCADE,
            FOREIGN KEY (instructor_id)
                REFERENCES instructors(instructor_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS reviews (
            review_id   INT AUTO_INCREMENT PRIMARY KEY,
            book_id     INT,
            student_id  INT,
            rating      INT CHECK (rating >= 1 AND rating <= 5),
            review_text TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id)
                REFERENCES books(book_id) ON DELETE CASCADE,
            FOREIGN KEY (student_id)
                REFERENCES users(user_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS carts (
            cart_id      INT AUTO_INCREMENT PRIMARY KEY,
            student_id   INT UNIQUE,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                         ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id)
                REFERENCES users(user_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS cart_items (
            cart_item_id    INT AUTO_INCREMENT PRIMARY KEY,
            cart_id         INT,
            book_id         INT,
            quantity        INT DEFAULT 1,
            purchase_option ENUM('rent','buy') DEFAULT 'buy',
            FOREIGN KEY (cart_id)
                REFERENCES carts(cart_id) ON DELETE CASCADE,
            FOREIGN KEY (book_id)
                REFERENCES books(book_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id       INT AUTO_INCREMENT PRIMARY KEY,
            student_id     INT,
            date_created   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_fulfilled TIMESTAMP NULL,
            shipping_type  ENUM('standard','2-day','1-day')
                           DEFAULT 'standard',
            cc_number      VARCHAR(20),
            cc_expiration  VARCHAR(7),
            cc_holder_name VARCHAR(255),
            cc_type        ENUM('Visa','MasterCard','Amex',
                                'Discover','RuPay') DEFAULT 'Visa',
            order_status   ENUM('new','processed','awaiting_shipping',
                                'shipped','canceled') DEFAULT 'new',
            total_amount   DECIMAL(12,2) DEFAULT 0.00,
            FOREIGN KEY (student_id)
                REFERENCES users(user_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id   INT AUTO_INCREMENT PRIMARY KEY,
            order_id        INT,
            book_id         INT,
            quantity        INT DEFAULT 1,
            price           DECIMAL(10,2),
            purchase_option ENUM('rent','buy') DEFAULT 'buy',
            FOREIGN KEY (order_id)
                REFERENCES orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY (book_id)
                REFERENCES books(book_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS trouble_tickets (
            ticket_id            INT AUTO_INCREMENT PRIMARY KEY,
            category             ENUM('user_profile','products',
                                      'cart','orders','other') NOT NULL,
            title                VARCHAR(255) NOT NULL,
            problem_description  TEXT,
            solution_description TEXT,
            date_logged          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completion_date      TIMESTAMP NULL,
            ticket_status        ENUM('new','assigned',
                                      'in-process','completed')
                                 DEFAULT 'new',
            created_by           INT,
            created_by_role      ENUM('student','customer_support')
                                 NOT NULL,
            assigned_admin       INT NULL,
            FOREIGN KEY (created_by)
                REFERENCES users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (assigned_admin)
                REFERENCES users(user_id) ON DELETE SET NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ticket_status_history (
            history_id INT AUTO_INCREMENT PRIMARY KEY,
            ticket_id  INT,
            old_status ENUM('new','assigned','in-process','completed'),
            new_status ENUM('new','assigned','in-process','completed'),
            changed_by INT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id)
                REFERENCES trouble_tickets(ticket_id) ON DELETE CASCADE,
            FOREIGN KEY (changed_by)
                REFERENCES users(user_id) ON DELETE SET NULL
        )
        """
    ]

    for table_sql in tables:
        try:
            cursor.execute(table_sql)
        except Error as e:
            print(f"Error creating table: {e}")

    conn.commit()

    # ── Trigger: Allow only 1 Super Admin ──
    try:
        cursor.execute("DROP TRIGGER IF EXISTS limit_super_admin")
        cursor.execute("""
            CREATE TRIGGER limit_super_admin
            BEFORE INSERT ON users
            FOR EACH ROW
            BEGIN
                IF NEW.role = 'super_admin' THEN
                    IF (SELECT COUNT(*) FROM users
                        WHERE role = 'super_admin') >= 1 THEN
                        SIGNAL SQLSTATE '45000'
                        SET MESSAGE_TEXT =
                            'Only 1 Super Admin is allowed.';
                    END IF;
                END IF;
            END
        """)
        conn.commit()
        print("✅ Super Admin trigger created.")
    except Error as e:
        print(f"Trigger note: {e}")

    cursor.close()
    conn.close()
    print("✅ Database initialized successfully.")