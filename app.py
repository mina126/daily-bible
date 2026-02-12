from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date, timedelta
import cloudinary
import cloudinary.uploader
import uuid
import os
import psycopg2

# ==================================================
# 📖 Bible Reading Plan
# ==================================================

BIBLE_PLAN = []

books = {
    "إنجيل متى": 28,
    "إنجيل مرقس": 16,
    "إنجيل لوقا": 24,
    "إنجيل يوحنا": 21,
    "أعمال الرسل": 28
}

for book, chapters in books.items():
    for ch in range(1, chapters + 1):
        BIBLE_PLAN.append(f"{book} - الإصحاح {ch}")

START_DATE = date(2026, 2, 9)

# ==================================================
# ☁️ Cloudinary
# ==================================================

cloudinary.config(
    cloud_name="dpwxa2wzk",
    api_key="578539276511726",
    api_secret="rQCb8Gh0u0GIsMUcj6iwlO6KBwQ"
)

# ==================================================
# 🚀 Flask
# ==================================================

app = Flask(__name__)
app.secret_key = "daily-bible-secret"

ADMIN_PASSWORD = "اشبال اتنين"

# ==================================================
# 🗄 Database
# ==================================================

def get_db():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE,
            total_days INTEGER,
            streak INTEGER,
            last_date TEXT,
            photo TEXT
        )
    """)
    conn.commit()
    conn.close()

# 🔒 الحل هنا (تشغيل مرة واحدة فقط)
if os.environ.get("INIT_DB") == "true":
    init_db()

# ==================================================
# 🏠 Home
# ==================================================

@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    today = date.today()
    day_index = (today - START_DATE).days

    if day_index < 0:
        reading = "البرنامج لم يبدأ بعد"
    elif day_index >= len(BIBLE_PLAN):
        reading = "🎉 خلصنا إنجيل وأعمال الرسل"
    else:
        reading = BIBLE_PLAN[day_index]

    background_folder = os.path.join(app.static_folder, "imged/backgrounds")
    images = []
    if os.path.exists(background_folder):
        images = [
            f"imged/backgrounds/{img}"
            for img in os.listdir(background_folder)
            if img.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        ]

    if request.method == "POST":
        name = request.form.get("name")
        photo = request.files.get("photo")

        if not name or not photo:
            return render_template("index.html", message="❌ لازم الاسم والصورة", reading=reading, images=images)

        upload = cloudinary.uploader.upload(
            photo,
            folder="daily_bible",
            public_id=f"{name}_{uuid.uuid4()}"
        )

        image_url = upload["secure_url"]
        today_str = str(today)

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "SELECT total_days, streak, last_date FROM users WHERE name=%s",
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
                    SET total_days=%s, streak=%s, last_date=%s, photo=%s
                    WHERE name=%s
                """, (total, streak, today_str, image_url, name))
        else:
            c.execute("""
                INSERT INTO users (name, total_days, streak, last_date, photo)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, 1, 1, today_str, image_url))

        conn.commit()
        conn.close()
        message = "✅ الصورة اترفعت واتسجل اليوم بنجاح"

    conn = get_db()
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
# 🔐 Admin
# ==================================================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        return render_template("admin_login.html", error="❌ كلمة السر غلط")
    return render_template("admin_login.html")

@app.route("/admin-dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT name, total_days, streak, last_date
        FROM users
        ORDER BY streak DESC
    """)
    users = c.fetchall()
    conn.close()

    return render_template("users.html", users=users)

@app.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("index"))

# ==================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
