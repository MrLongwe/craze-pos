# -----------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------

# Flask core tools
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -----------------------------------------------------------
# APP INITIALIZATION
# -----------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-me')  # Required for sessions
app.permanent_session_lifetime = timedelta(days=30)  # Session lasts 30 days

DATABASE = "database.db"

# -----------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------

STREAK_BONUS = 2  # Points for 7-day streak
REFERRAL_BONUS = 1
BADGES = {
    'first_blood': {'name': 'First Timer', 'icon': '🎯', 'threshold': 1},
    'regular': {'name': 'Regular', 'icon': '🔄', 'threshold': 5},
    'loyalist': {'name': 'Loyalist', 'icon': '⭐', 'threshold': 10},
    'streak_master': {'name': 'Streak Master', 'icon': '🔥', 'threshold': 7},
    'legend': {'name': 'Legend', 'icon': '👑', 'threshold': 50}
}

# -----------------------------------------------------------
# DATABASE INITIALIZATION
# -----------------------------------------------------------

def init_db():
    """Initialize database with enhanced schema"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table with enhanced fields
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            pin_hash TEXT NOT NULL,
            points INTEGER DEFAULT 0,
            total_points INTEGER DEFAULT 0,
            last_claim_date TEXT,
            streak_days INTEGER DEFAULT 0,
            badges TEXT DEFAULT '[]',
            referral_code TEXT UNIQUE,
            referred_by TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_active TEXT
        )
    """)
    
    # Create daily codes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            date TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

# Run database initialization
init_db()

# -----------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------

def generate_referral_code(username):
    """Generate unique referral code"""
    return f"{username[:3]}{''.join(random.choices(string.ascii_uppercase + string.digits, k=5))}".upper()

def get_user_by_username(username):
    """Fetch user by username"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# -----------------------------------------------------------
# ROUTES
# -----------------------------------------------------------

@app.route("/")
def index():
    """Homepage"""
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration"""
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        pin = request.form["pin"]
        
        # Validate PIN (must be 4 digits)
        if not (pin.isdigit() and len(pin) == 4):
            return render_template("error.html", message="PIN must be 4 digits.")
        
        # Hash the PIN
        pin_hash = generate_password_hash(pin)
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            # Generate unique referral code
            referral_code = generate_referral_code(username)
            
            cursor.execute(
                "INSERT INTO users (username, pin_hash, referral_code) VALUES (?, ?, ?)",
                (username, pin_hash, referral_code)
            )
            conn.commit()
            
            # Auto-login after registration
            user = get_user_by_username(username)
            session['user_id'] = user['id']
            session['username'] = user['username']
            session.permanent = True
            
            return redirect(url_for("profile", username=username))
            
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("error.html", message="Username already taken.")
        
        conn.close()
    
    return render_template("register.html")

@app.route("/claim", methods=["GET", "POST"])
def claim():
    """Handle daily point claims"""
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        pin = request.form["pin"]
        code = request.form["code"]
        
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get user with all fields
        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['pin_hash'], pin):
            conn.close()
            return render_template("error.html", message="Invalid credentials")
        
        # Check daily code
        cursor.execute("SELECT code FROM daily_codes WHERE date=?", 
                      (datetime.now().strftime("%Y-%m-%d"),))
        valid_code = cursor.fetchone()
        
        # If no code set for today, use default or generate one
        if not valid_code:
            # Auto-generate a code for today if none exists
            default_code = "1234"
            cursor.execute(
                "INSERT INTO daily_codes (code, date) VALUES (?, ?)",
                (default_code, datetime.now().strftime("%Y-%m-%d"))
            )
            conn.commit()
            valid_code = {'code': default_code}
        
        if valid_code['code'] != code:
            conn.close()
            return render_template("error.html", message="Invalid daily code")
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        if user['last_claim_date'] == today:
            conn.close()
            return render_template("error.html", message="Already claimed today")
        
        # Calculate streak
        streak_days = user['streak_days'] or 0
        if user['last_claim_date']:
            last_date = datetime.strptime(user['last_claim_date'], '%Y-%m-%d').date()
            yesterday = datetime.now().date() - timedelta(days=1)
            
            if last_date == yesterday:
                streak_days += 1
            elif last_date < yesterday:
                streak_days = 1  # Restart streak
        else:
            streak_days = 1  # First claim
        
        # Calculate points earned
        points_earned = 1
        streak_message = None
        if streak_days >= 7:
            points_earned += STREAK_BONUS
            streak_message = f"🔥 {STREAK_BONUS} bonus points for {streak_days}-day streak!"
        
        # Update points
        new_points = user['points'] + points_earned
        total_points = user['total_points'] + points_earned
        
        # Check for new badges
        badges = json.loads(user['badges']) if user['badges'] else []
        new_badges = []
        
        for badge_key, badge_info in BADGES.items():
            if badge_key not in badges and total_points >= badge_info['threshold']:
                badges.append(badge_key)
                new_badges.append(badge_info)
        
        # Check reward condition (10 points = free fries)
        reward = False
        if new_points >= 10:
            reward = True
            new_points = 0
        
        percent = int((new_points / 10) * 100)
        remaining = 10 - new_points
        
        # Update user record
        cursor.execute("""
            UPDATE users 
            SET points=?, total_points=?, last_claim_date=?, 
                streak_days=?, badges=?, last_active=?
            WHERE username=?
        """, (new_points, total_points, today, streak_days, 
              json.dumps(badges), datetime.now().isoformat(), username))
        
        conn.commit()
        conn.close()
        
        return render_template(
            "success.html",
            username=username,
            points=new_points,
            percent=percent,
            remaining=remaining,
            reward=reward,
            streak_days=streak_days,
            streak_message=streak_message,
            new_badges=new_badges,
            points_earned=points_earned
        )
    
    return render_template("claim.html")

@app.route("/profile/<username>")
def profile(username):
    """User profile page"""
    # Check if user is logged in (optional - can view public profiles)
    user = get_user_by_username(username)
    
    if not user:
        return render_template("error.html", message="User not found")
    
    # Parse badges
    badges = json.loads(user['badges']) if user['badges'] else []
    badge_details = [BADGES[b] for b in badges if b in BADGES]
    
    # Calculate rank
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) + 1 as rank 
        FROM users 
        WHERE total_points > (SELECT total_points FROM users WHERE username=?)
    """, (username,))
    rank = cursor.fetchone()[0]
    conn.close()
    
    # Check if this is the logged-in user
    is_owner = session.get('username') == username
    
    return render_template(
        "profile.html",
        user=user,
        badges=badge_details,
        rank=rank,
        is_owner=is_owner
    )

@app.route("/leaderboard")
def leaderboard():
    """Display top users"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT username, total_points, streak_days 
        FROM users 
        ORDER BY total_points DESC 
        LIMIT 20
    """)
    leaders = cursor.fetchall()
    
    conn.close()
    return render_template("leaderboard.html", leaders=leaders)

@app.route("/admin")
def admin():
    """Simple admin view"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, points, total_points, streak_days FROM users")
    users = cursor.fetchall()
    
    conn.close()
    
    return render_template("admin.html", users=users)

@app.route("/admin/generate-code", methods=["POST"])
def generate_code():
    """Generate daily code (admin only - add authentication later)"""
    # Simple admin check - you can enhance this
    if not session.get('user_id'):
        return {"error": "Not authorized"}, 403
    
    new_code = str(random.randint(1000, 9999))
    today = datetime.now().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT OR REPLACE INTO daily_codes (code, date) VALUES (?, ?)",
        (new_code, today)
    )
    
    conn.commit()
    conn.close()
    
    return {"code": new_code, "date": today}

@app.route("/login", methods=["POST"])
def login():
    """Simple login endpoint for existing users"""
    username = request.form.get("username", "").strip().lower()
    pin = request.form.get("pin", "")
    
    user = get_user_by_username(username)
    
    if user and check_password_hash(user['pin_hash'], pin):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session.permanent = True
        return redirect(url_for("profile", username=username))
    
    return render_template("error.html", message="Invalid login credentials")

@app.route("/logout")
def logout():
    """Log out user"""
    session.clear()
    return redirect(url_for("index"))

# -----------------------------------------------------------
# RUN APPLICATION
# -----------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)