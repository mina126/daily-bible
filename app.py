# from flask import Flask, render_template, request
# import sqlite3
# from datetime import date
# from datetime import timedelta
# import os
# import uuid
# from werkzeug.utils import secure_filename
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
# from google.oauth2 import service_account


# app = Flask(__name__)

# # إنشاء فولدر uploads لو مش موجود
# UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # إنشاء قاعدة البيانات لو مش موجودة
# def init_db():
#     conn = sqlite3.connect("database.db")
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT UNIQUE,
#             total_days INTEGER DEFAULT 0,
#             streak INTEGER DEFAULT 0,
#             last_date TEXT,
#             photo TEXT
#         )
#     """)
#     conn.commit()
#     conn.close()

# init_db()
# def upload_to_drive(file_path, filename):
#     SCOPES = ['https://www.googleapis.com/auth/drive']
#     SERVICE_ACCOUNT_FILE = 'credentials.json'

#     creds = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE, scopes=SCOPES)

#     service = build('drive', 'v3', credentials=creds)

#     file_metadata = {
#         'name': filename,
#         'parents': ['1nKHEp24cCOeVAQkXE-76lM8h-xDoP6BB']  # 👈 هنحط ID الفولدر هنا
#     }

#     media = MediaFileUpload(file_path, resumable=True)

#     file = service.files().create(
#         body=file_metadata,
#         media_body=media,
#         fields='id',
#         supportsAllDrives=True
#     ).execute()

#     return file.get('id')

# @app.route("/", methods=["GET", "POST"])
# def index():
#     name = None
#     streak = 0
#     total = 0
#     message = None

#     if request.method == "POST":
#         name = request.form.get("name")

#         # رفع الصورة
#         photo = request.files.get("photo")

#         if not photo or photo.filename == "":
#             message = "❌ لازم ترفع صورة."
#             return render_template("index.html", message=message)

#         # اسم فريد للصورة
#         filename = str(uuid.uuid4()) + "_" + secure_filename(photo.filename)
#         filepath = os.path.join(UPLOAD_FOLDER, filename)
#         photo.save(filepath)
#         drive_file_id = upload_to_drive(filepath, filename)
#         print("Uploaded to Drive:", drive_file_id)

#         today = str(date.today())

#         conn = sqlite3.connect("database.db")
#         cursor = conn.cursor()

#         cursor.execute("SELECT total_days, streak, last_date FROM users WHERE name=?", (name,))
#         user = cursor.fetchone()

#         if user:
#             total_days, old_streak, last_date = user

#             if last_date == today:
#                 streak = old_streak
#                 total = total_days
#             else:
#                 yesterday = str(date.fromisoformat(today) - timedelta(days=1))

#                 if last_date == yesterday:
#                     streak = old_streak + 1
#                 else:
#                     streak = 1

#                 total = total_days + 1

#                 cursor.execute("""
#                     UPDATE users
#                     SET total_days=?, streak=?, last_date=?, photo=?
#                     WHERE name=?
#                 """, (total, streak, today, filename, name))

#         else:
#             streak = 1
#             total = 1
#             cursor.execute("""
#                 INSERT INTO users (name, total_days, streak, last_date, photo)
#                 VALUES (?, ?, ?, ?, ?)
#             """, (name, total, streak, today, filename))

#         conn.commit()
#         conn.close()

#         message = "✅ تم رفع الصورة وتسجيل اليوم بنجاح!"

#     return render_template("index.html", name=name, streak=streak, total=total, message=message)


# @app.route("/users")
# def show_users():
#     conn = sqlite3.connect("database.db")
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT name, total_days, streak, last_date, photo
#         FROM users
#         ORDER BY streak DESC
#     """)

#     users = cursor.fetchall()
#     conn.close()

#     return render_template("users.html", users=users)


# if __name__ == "__main__":
#     app.run(debug=True)
#########################################################################
# from flask import Flask, render_template, request
# import sqlite3
# from datetime import date, timedelta
# import os
# import uuid
# from werkzeug.utils import secure_filename
# import cloudinary
# import cloudinary.uploader
# import cloudinary.api
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
# from google.oauth2 import service_account
# cloudinary.config(
#     cloud_name="dpwxa2wzk",
#     api_key="578539276511726",
#     api_secret="rQCb8Gh0u0GIsMUcj6iwlO6KBwQ"
# )

# app = Flask(__name__)

# # ---------------- Upload Folder ----------------
# UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # ---------------- Google Drive ----------------
# SCOPES = ['https://www.googleapis.com/auth/drive']
# SERVICE_ACCOUNT_FILE = 'credentials.json'
# DRIVE_FOLDER_ID = "1nKHEp24cCOeVAQkXE-76lM8h-xDoP6BB"

# def get_drive_service():
#     creds = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE,
#         scopes=SCOPES
#     )
#     return build('drive', 'v3', credentials=creds)

# def upload_to_drive(file_path, filename):
#     service = get_drive_service()

#     file_metadata = {
#         'name': filename,
#         'parents': [DRIVE_FOLDER_ID]
#     }

#     media = MediaFileUpload(file_path, resumable=True)

#     file = service.files().create(
#         body=file_metadata,
#         media_body=media,
#         fields='id'
#     ).execute()

#     return file.get('id')

# # ---------------- Database ----------------
# def init_db():
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT UNIQUE,
#             total_days INTEGER,
#             streak INTEGER,
#             last_date TEXT,
#             photo TEXT
#         )
#     """)
#     conn.commit()
#     conn.close()

# init_db()

# # ---------------- Routes ----------------
# @app.route("/", methods=["GET", "POST"])
# def index():
#     message = None

#     if request.method == "POST":
#         name = request.form.get("name")
#         photo = request.files.get("photo")

#         if not name or not photo or photo.filename == "":
#             return render_template("index.html", message="❌ لازم الاسم والصورة")

#         filename = f"{uuid.uuid4()}_{secure_filename(photo.filename)}"
#         local_path = os.path.join(UPLOAD_FOLDER, filename)
#         photo.save(local_path)

#         drive_id = upload_to_drive(local_path, filename)

#         today = str(date.today())
#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()

#         c.execute(
#             "SELECT total_days, streak, last_date FROM users WHERE name=?",
#             (name,)
#         )
#         user = c.fetchone()

#         if user:
#             total, streak, last = user

#             if last != today:
#                 yesterday = str(date.fromisoformat(today) - timedelta(days=1))
#                 streak = streak + 1 if last == yesterday else 1
#                 total += 1

#                 c.execute("""
#                     UPDATE users
#                     SET total_days=?, streak=?, last_date=?, photo=?
#                     WHERE name=?
#                 """, (total, streak, today, drive_id, name))
#         else:
#             c.execute("""
#                 INSERT INTO users (name, total_days, streak, last_date, photo)
#                 VALUES (?, ?, ?, ?, ?)
#             """, (name, 1, 1, today, drive_id))

#         conn.commit()
#         conn.close()

#         message = "✅ الصورة اترفعت واتسجل اليوم بنجاح"

#     return render_template("index.html", message=message)

# @app.route("/users")
# def users():
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute("""
#         SELECT name, total_days, streak, last_date
#         FROM users
#         ORDER BY streak DESC
#     """)
#     users = c.fetchall()
#     conn.close()
#     return render_template("users.html", users=users)

# # ---------------- Run ----------------
# if __name__ == "__main__":
#     app.run(debug=True)


####################################################################
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import date, timedelta
import cloudinary
import cloudinary.uploader
import uuid
import os

# ==================================================
# 📖 Bible Reading Plan
# ==================================================

# قائمة القراءة اليومية
BIBLE_PLAN = []

books = {
    "إنجيل متى": 28,
    "إنجيل مرقس": 16,
    "إنجيل لوقا": 24,
    "إنجيل يوحنا": 21,
    "أعمال الرسل": 28
}

# توليد الخطة كاملة (كتاب + إصحاح)
for book, chapters in books.items():
    for ch in range(1, chapters + 1):
        BIBLE_PLAN.append(f"{book} - الإصحاح {ch}")

# تاريخ بداية البرنامج
START_DATE = date(2026, 2, 9)

# ==================================================
# ☁️ Cloudinary Config
# ==================================================

cloudinary.config(
    cloud_name="dpwxa2wzk",
    api_key="578539276511726",
    api_secret="rQCb8Gh0u0GIsMUcj6iwlO6KBwQ"
)

# ==================================================
# 🚀 Flask App
# ==================================================

app = Flask(__name__)
app.secret_key = "daily-bible-secret"  # مهم للـ session

ADMIN_PASSWORD = "اشبال اتنين"  # غيره براحتك

# ==================================================
# 🗄 Database
# ==================================================


def init_db():
    """
    إنشاء قاعدة البيانات لو مش موجودة
    """
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            total_days INTEGER,
            streak INTEGER,
            last_date TEXT,
            photo TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()

# ==================================================
# 🏠 Home Page
# ==================================================


@app.route("/", methods=["GET", "POST"])
def index():
    """
    الصفحة الرئيسية
    - تعرض قراءة اليوم
    - تسجيل المستخدم بالصورة
    - حساب streak و total
    """
    message = None
    today = date.today()
    day_index = (today - START_DATE).days

    # تحديد قراءة اليوم
    if day_index < 0:
        reading = "البرنامج لم يبدأ بعد"
    elif day_index >= len(BIBLE_PLAN):
        reading = "🎉 خلصنا إنجيل وأعمال الرسل"
    else:
        reading = BIBLE_PLAN[day_index]

    # تحميل صور الخلفية تلقائي
    background_folder = os.path.join(app.static_folder, "imged/backgrounds")
    images = []
    if os.path.exists(background_folder):
        images = [
            f"imged/backgrounds/{img}"
            for img in os.listdir(background_folder)
            if img.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        ]

    # تسجيل قراءة المستخدم
    if request.method == "POST":
        name = request.form.get("name")
        photo = request.files.get("photo")

        if not name or not photo or photo.filename == "":
            return render_template(
                "index.html",
                message="❌ لازم الاسم والصورة",
                reading=reading,
                images=images
            )

        # رفع الصورة على Cloudinary
        upload = cloudinary.uploader.upload(
            photo,
            folder="daily_bible",
            public_id=f"{name}_{uuid.uuid4()}"
        )

        image_url = upload["secure_url"]
        today_str = str(today)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # هل المستخدم مسجل قبل كده؟
        c.execute(
            "SELECT total_days, streak, last_date FROM users WHERE name=?",
            (name,)
        )
        user = c.fetchone()

        if user:
            total, streak, last = user
            if last != today_str:
                yesterday = str(today - timedelta(days=1))
                streak = streak + 1 if last == yesterday else 1
                total += 1

                c.execute("""
                    UPDATE users
                    SET total_days=?, streak=?, last_date=?, photo=?
                    WHERE name=?
                """, (total, streak, today_str, image_url, name))
        else:
            c.execute("""
                INSERT INTO users (name, total_days, streak, last_date, photo)
                VALUES (?, ?, ?, ?, ?)
            """, (name, 1, 1, today_str, image_url))

        conn.commit()
        conn.close()
        message = "✅ الصورة اترفعت واتسجل اليوم بنجاح"

    # إحصائيات
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        SELECT name, streak FROM users
        ORDER BY streak DESC
        LIMIT 1
    """)
    top_user = c.fetchone()

    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        message=message,
        reading=reading,
        images=images,
        top_user=top_user,
        total_users=total_users
    )

# ==================================================
# 🔐 Admin Login
# ==================================================


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    """
    صفحة تسجيل دخول الأدمن
    """
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))

        return render_template("admin_login.html", error="❌ كلمة السر غلط")

    return render_template("admin_login.html")

# ==================================================
# 📊 Admin Dashboard
# ==================================================


@app.route("/admin-dashboard")
def admin_dashboard():
    """
    لوحة تحكم الأدمن
    - عرض المستخدمين
    - ترتيب حسب streak
    """
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        SELECT name, total_days, streak, last_date
        FROM users
        ORDER BY streak DESC
    """)
    users = c.fetchall()
    conn.close()

    return render_template("users.html", users=users)

# ==================================================
# 🚪 Logout
# ==================================================


@app.route("/admin-logout")
def admin_logout():
    """
    تسجيل خروج الأدمن
    """
    session.pop("admin", None)
    return redirect(url_for("index"))

# ==================================================
# ▶ Run App
# ==================================================


if __name__ == "__main__":
    app.run(debug=True)
