import bcrypt
import mysql.connector

# ── Database Config ──
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'Krishna@2005',         # ← Change to your MySQL password
    'database': 'gyanpustak'
}

# ══════════════════════════════════════
#   SUPER ADMIN DETAILS — CHANGE THESE
# ══════════════════════════════════════
SUPER_ADMIN = {
    'first_name': 'Krishna',
    'last_name':  'Teja',
    'email':      'krish@gmail.com',
    'password':   'krish',
    'phone':      '+91-9999999999',
    'address':    'GyanPustak HQ, India',
    'gender':     'Male',
    'salary':     0.00,
    'aadhaar':    '123456789012'    # ← 12 digit Aadhaar
}

def create_super_admin():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # ── Check if super admin already exists ──
        cursor.execute(
            "SELECT user_id FROM users WHERE role = 'super_admin'"
        )
        existing = cursor.fetchone()

        # ── Hash the password ──
        pw_hash = bcrypt.hashpw(
            SUPER_ADMIN['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        if existing:
            # ════════════════════════════════════
            #   SUPER ADMIN EXISTS — ASK TO UPDATE
            # ════════════════════════════════════
            old_user_id = existing['user_id']
            print("\n⚠️  A Super Admin already exists in the system.")
            print(f"   Current Super Admin ID : {old_user_id}")
            print("   Do you want to UPDATE the existing Super Admin?")
            print("   The User ID will remain the SAME.")
            print()
            confirm = input(
                "   Type 'YES' or 'Y' to confirm update: "
            ).strip()

            if confirm.strip().lower() not in ['yes', 'y']:
                print(
                    "\n❌ Operation cancelled. "
                    "Existing Super Admin is unchanged."
                )
                cursor.close()
                conn.close()
                return

            # ── Check if new email is used by someone else ──
            cursor.execute("""
                SELECT user_id FROM users
                WHERE email = %s AND user_id != %s
            """, (SUPER_ADMIN['email'], old_user_id))
            if cursor.fetchone():
                print(
                    f"\n❌ Email '{SUPER_ADMIN['email']}' is already "
                    f"used by another account."
                )
                print(
                    "   Please change the email in "
                    "SUPER_ADMIN details and try again."
                )
                cursor.close()
                conn.close()
                return

            # ── Check if new Aadhaar is used by someone else ──
            cursor.execute("""
                SELECT employee_id FROM employee_details
                WHERE aadhaar_number = %s AND employee_id != %s
            """, (SUPER_ADMIN['aadhaar'], old_user_id))
            if cursor.fetchone():
                print(
                    f"\n❌ Aadhaar '{SUPER_ADMIN['aadhaar']}' is already "
                    f"used by another account."
                )
                print(
                    "   Please change the Aadhaar in "
                    "SUPER_ADMIN details and try again."
                )
                cursor.close()
                conn.close()
                return

            # ── UPDATE users table (same user_id) ──
            cursor.execute("""
                UPDATE users
                SET first_name    = %s,
                    last_name     = %s,
                    email         = %s,
                    password_hash = %s,
                    phone         = %s,
                    address       = %s
                WHERE user_id = %s
            """, (
                SUPER_ADMIN['first_name'],
                SUPER_ADMIN['last_name'],
                SUPER_ADMIN['email'],
                pw_hash,
                SUPER_ADMIN['phone'],
                SUPER_ADMIN['address'],
                old_user_id
            ))

            # ── UPDATE employee_details table (same user_id) ──
            cursor.execute("""
                UPDATE employee_details
                SET gender         = %s,
                    salary         = %s,
                    aadhaar_number = %s
                WHERE employee_id = %s
            """, (
                SUPER_ADMIN['gender'],
                SUPER_ADMIN['salary'],
                SUPER_ADMIN['aadhaar'],
                old_user_id
            ))

            conn.commit()

            # ── Success message ──
            print(f"\n✅ Super Admin updated successfully!")
            print("=" * 45)
            print(f"  User ID  : {old_user_id} (unchanged)")
            print(f"  Name     : {SUPER_ADMIN['first_name']} {SUPER_ADMIN['last_name']}")
            print(f"  Email    : {SUPER_ADMIN['email']}")
            print(f"  Password : {SUPER_ADMIN['password']}")
            print(f"  Role     : Super Administrator")
            print(f"  Phone    : {SUPER_ADMIN['phone']}")
            print("=" * 45)
            print("\n👉 You can now login with the new credentials.")
            print("⚠️  Please keep your credentials safe!\n")

        else:
            # ════════════════════════════════════
            #   NO SUPER ADMIN — CREATE FRESH
            # ════════════════════════════════════

            # ── Check if email already used ──
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s",
                (SUPER_ADMIN['email'],)
            )
            if cursor.fetchone():
                print(
                    f"\n❌ Email '{SUPER_ADMIN['email']}' is already "
                    f"used by another account."
                )
                print(
                    "   Please change the email in "
                    "SUPER_ADMIN details and try again."
                )
                cursor.close()
                conn.close()
                return

            # ── Check if Aadhaar already used ──
            cursor.execute(
                "SELECT employee_id FROM employee_details "
                "WHERE aadhaar_number = %s",
                (SUPER_ADMIN['aadhaar'],)
            )
            if cursor.fetchone():
                print(
                    f"\n❌ Aadhaar '{SUPER_ADMIN['aadhaar']}' is already "
                    f"used by another account."
                )
                print(
                    "   Please change the Aadhaar in "
                    "SUPER_ADMIN details and try again."
                )
                cursor.close()
                conn.close()
                return

            # ── INSERT into users table ──
            cursor.execute("""
                INSERT INTO users
                    (email, password_hash, role,
                     first_name, last_name, phone, address)
                VALUES (%s, %s, 'super_admin', %s, %s, %s, %s)
            """, (
                SUPER_ADMIN['email'],
                pw_hash,
                SUPER_ADMIN['first_name'],
                SUPER_ADMIN['last_name'],
                SUPER_ADMIN['phone'],
                SUPER_ADMIN['address']
            ))
            new_user_id = cursor.lastrowid

            # ── INSERT into employee_details table ──
            cursor.execute("""
                INSERT INTO employee_details
                    (employee_id, gender, salary, aadhaar_number)
                VALUES (%s, %s, %s, %s)
            """, (
                new_user_id,
                SUPER_ADMIN['gender'],
                SUPER_ADMIN['salary'],
                SUPER_ADMIN['aadhaar']
            ))

            conn.commit()

            # ── Success message ──
            print("\n✅ Super Admin created successfully!")
            print("=" * 45)
            print(f"  User ID  : {new_user_id}")
            print(f"  Name     : {SUPER_ADMIN['first_name']} {SUPER_ADMIN['last_name']}")
            print(f"  Email    : {SUPER_ADMIN['email']}")
            print(f"  Password : {SUPER_ADMIN['password']}")
            print(f"  Role     : Super Administrator")
            print(f"  Phone    : {SUPER_ADMIN['phone']}")
            print("=" * 45)
            print("\n👉 You can now login at the GyanPustak website.")
            print("⚠️  Please change your password after first login!\n")

        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        print(f"\n❌ Database Error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    create_super_admin()