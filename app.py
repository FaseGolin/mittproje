from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response #type: ignore
import sqlite3
import os
import pg8000 #type: ignore
import json
from werkzeug.security import generate_password_hash, check_password_hash #type: ignore
from datetime import datetime
from dotenv import load_dotenv #type: ignore
app = Flask(__name__)
app.secret_key = b'qwerty' 
DATABASE = 'database.db'

load_dotenv()

# Database connection parameters from environment
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")




def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# def get_db_connection():
#     connection = pg8000.connect(
#         user=DB_USER,
#         password=DB_PASSWORD,
#         database=DB_NAME,
#         host=DB_HOST,
#         port=DB_PORT
#     )
#     return connection


def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            courses TEXT
    );
''')


    conn.commit()
    cursor.close()
    conn.close()

create_table()
        
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        selected_courses = request.form.get('selectedCourses', '')

        session["selected_courses"] = selected_courses.split(",") if selected_courses else []

        if not selected_courses.strip():
            flash('No courses selected. Please try again.', 'warning')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (username, password, courses)
                VALUES (?, ?, ?)
            ''', (username, hashed_password, selected_courses))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            flash('Username is already registered. Please choose another.', 'warning')
            return redirect(url_for('register'))

        conn.close()
        flash('Your account has been created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['selected_courses'] = user['courses'].split(",") if user['courses'] else []
            print(f"DEBUG: Loaded courses from DB: {session['selected_courses']}")  # Debugging print

            flash('You are now logged in!', 'success')
            return redirect(url_for('success'))

        flash('Incorrect username or password.', 'danger')

    return render_template('login.html')


@app.route('/')
def index():
    if 'username' in session:
        return render_template('home.html', username=session["username"])
    return render_template('home.html')

@app.route('/home/')
def home():
    return render_template('home.html')

@app.route('/video/<video_name>')
def video_page(video_name):
    # Dictionary of video data
    videos = {
        "copywriting": {
            "title": "COPYWRITING",
            "filename": "Copywriting.mp4",
            "description": "Learn the secrets of persuasive writing to increase conversions."
        },
        "client-acquisition": {
            "title": "CLIENT ACQUISITION STRATEGIES",
            "filename": "Freelancing.mp4",
            "description": "Discover how to attract and retain high-value clients."
        },
        "ecommerce": {
            "title": "ECOMMERCE SUCCESS",
            "filename": "E-commerce.mp4",
            "description": "Master the art of online selling and brand-building."
        },
        "business": {
            "title": "BUSINESS MASTERY",
            "filename": "Business.mp4",
            "description": "Develop essential business strategies for long-term success."
        },
        "content-creation": {
            "title": "CONTENT CREATION GUIDE",
            "filename": "Content-Creation.mp4",
            "description": "Learn how to create engaging content that drives traffic and sales."
        },
        "defi": {
            "title": "CRYPTO & DEFI STRATEGIES",
            "filename": "Crypto.mp4",
            "description": "Understand cryptocurrency and decentralized finance to grow your wealth."
        },
        "health": {
            "title": "HEALTH & FITNESS",
            "filename": "Health.mp4",
            "description": "Optimize your physical and mental well-being with expert guidance."
        },
        "markets": {
            "title": "STOCK & MARKET ANALYSIS",
            "filename": "Markets.mp4",
            "description": "Gain insights into stock markets and financial trends for smart investing."
        },
        "artifical-intelligence": {
            "title": "ARTIFICAL-INTELLIGENCENE",
            "filename": "Artificial-Intelligence.mp4",
            "description": "Explore how AI is transforming industries and how you can leverage it."
        },
        "mindset": {
            "title": "ENTREPRUNEURIAL MINDSET",
            "filename": "Mindset.mp4",
            "description": "Cultivate the right mindset for success in business and life."
        }
    }

    
    if video_name in videos:
        video = videos[video_name]
    else:
        flash("Video not found.", "danger")
        return redirect(url_for('home'))  

    
    video_url = f"https://huizjjyrhmxufwgkfwiu.supabase.co/storage/v1/object/public/sida/videos/{video['filename']}"

   
    return render_template('video.html', video_url=video_url, video=video)





@app.route('/logout/')
def logout():
    session.pop('username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/courses', methods=['GET', 'POST'])
def success():
    if 'username' not in session:
        flash('You need to log in first!', 'warning')
        return redirect(url_for('login'))  
    
    selected_courses = session.get('selected_courses', [])

    

    


    return render_template('success.html', selected_courses=selected_courses)


@app.route('/course-videos')
def course_videos():
    if 'username' not in session:
        flash('You need to log in first!', 'warning')
        return redirect(url_for('login'))
    
    course = request.args.get('course')
    
    videos = {
        "copywriting": [
            {
                "title": "Introduction to Copywriting",
                "filename": "Copywriting1.mp4",
                "description": "Learn the basics of copywriting and how to craft persuasive messages."
            },
            {
                "title": "Advanced Copywriting Techniques",
                "filename": "Copywriting2.mp4",
                "description": "Discover advanced techniques to increase conversion rates with your writing."
            },
            {
                "title": "Copywriting for Social Media",
                "filename": "Copywriting3.mp4",
                "description": "Master copywriting specifically for social media platforms and ads."
            }
        ],
        "client-acquisition": [
            {
                "title": "Finding Your Ideal Client",
                "filename": "Freelancing1.mp4",
                "description": "Learn how to identify and attract your perfect client."
            },
            {
                "title": "Building Long-Term Client Relationships",
                "filename": "Freelancing2.mp4",
                "description": "Understand how to build trust and lasting relationships with clients."
            },
            {
                "title": "Client Retention Strategies",
                "filename": "Freelancing3.mp4",
                "description": "Implement strategies to retain high-value clients and keep them coming back."
            }
        ],
        "ecommerce": [
            {
                "title": "Setting Up Your Online Store",
                "filename": "E-commerce1.mp4",
                "description": "Learn how to set up a successful e-commerce website."
            },
            {
                "title": "Marketing Your E-commerce Business",
                "filename": "E-commerce2.mp4",
                "description": "Discover marketing strategies to drive traffic to your e-commerce site."
            },
            {
                "title": "Optimizing Your E-commerce for Sales",
                "filename": "E-commerce3.mp4",
                "description": "Find out how to optimize your site to increase conversions and sales."
            }
        ],
        "business": [
            {
                "title": "Building a Business Foundation",
                "filename": "Business1.mp4",
                "description": "Understand the essential principles of building a solid business foundation."
            },
            {
                "title": "Scaling Your Business",
                "filename": "Business2.mp4",
                "description": "Learn how to scale your business successfully and sustainably."
            },
            {
                "title": "Business Management Tips",
                "filename": "Business3.mp4",
                "description": "Master key business management strategies for long-term growth."
            }
        ],
        "content-creation": [
            {
                "title": "Planning Your Content Strategy",
                "filename": "Content-Creation1.mp4",
                "description": "Learn how to plan a content strategy that aligns with your goals."
            },
            {
                "title": "Creating Engaging Content",
                "filename": "Content-Creation2.mp4",
                "description": "Discover how to create content that resonates with your audience."
            },
            {
                "title": "Optimizing Content for SEO",
                "filename": "Content-Creation3.mp4",
                "description": "Learn how to optimize your content for search engines to increase visibility."
            }
        ],
        "crypto": [
            {
                "title": "Understanding Cryptocurrency",
                "filename": "Crypto1.mp4",
                "description": "A beginner's guide to understanding cryptocurrency and blockchain technology."
            },
            {
                "title": "Decentralized Finance Explained",
                "filename": "Crypto2.mp4",
                "description": "Learn how decentralized finance (DeFi) is reshaping the financial industry."
            },
            {
                "title": "Investing in DeFi",
                "filename": "Crypto3.mp4",
                "description": "Discover how to invest in DeFi platforms and grow your digital assets."
            }
        ],
        "health": [
            {
                "title": "Introduction to Health & Fitness",
                "filename": "Health1.mp4",
                "description": "Get started on your journey to physical and mental wellness."
            },
            {
                "title": "Exercise for a Healthy Lifestyle",
                "filename": "Health2.mp4",
                "description": "Learn about the best exercises for improving your health and fitness."
            },
            {
                "title": "Mental Health Tips",
                "filename": "Health3.mp4",
                "description": "Discover tips for maintaining mental health and overall well-being."
            }
        ],
        "market": [
            {
                "title": "Stock Market Fundamentals",
                "filename": "Markets1.mp4",
                "description": "Understand the basics of the stock market and how to get started with investing."
            },
            {
                "title": "Advanced Market Analysis",
                "filename": "Markets2.mp4",
                "description": "Learn how to analyze stocks and other markets for better investment decisions."
            },
            {
                "title": "Creating a Diversified Portfolio",
                "filename": "Markets3.mp4",
                "description": "Discover strategies for building a diversified investment portfolio."
            }
        ],
        "artificial-intelligence": [
            {
                "title": "AI Basics for Beginners",
                "filename": "Artificial-Intelligence1.mp4",
                "description": "An introduction to artificial intelligence and its applications in various industries."
            },
            {
                "title": "How AI is Changing Industries",
                "filename": "Artificial-Intelligence2.mp4",
                "description": "Learn how AI is transforming fields like healthcare, finance, and retail."
            },
            {
                "title": "Leveraging AI for Business Growth",
                "filename": "Artificial-Intelligence3.mp4",
                "description": "Understand how businesses are using AI to drive innovation and growth."
            }
        ],
        "mindset": [
            {
                "title": "Developing the Entrepreneurial Mindset",
                "filename": "Mindset1.mp4",
                "description": "Learn how to think like an entrepreneur and embrace the mindset for success."
            },
            {
                "title": "Building Resilience in Business",
                "filename": "Mindset2.mp4",
                "description": "Discover strategies for overcoming setbacks and staying motivated in business."
            },
            {
                "title": "Achieving Success with the Right Mindset",
                "filename": "Mindset3.mp4",
                "description": "Understand how having the right mindset can lead to long-term success."
            }
        ]
    }


    if not course or course not in videos:
        flash('Invalid course selected.', 'danger')
        return redirect(url_for('success'))
    
    

    return render_template('videos.html', course=course, videos=videos[course])


@app.route('/test')
def allUsers():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users')  
    allUsers = [{'id': row[0], 'username': row[1], 'password': row[2], 'courses': row[3]} for row in cursor.fetchall()]   
    connection.close()

    base_url = "https://huizjjyrhmxufwgkfwiu.supabase.co/storage/v1/object/public/sida/images/"
    
    return render_template('html.html', allUsers=allUsers, base_url=base_url)
# @app.route('/success')
# def success():
#     if 'username' in session:
#         selected_courses = session.get('selected_courses', [])
#         return render_template('success.html', username=session["username"], courses=selected_courses)


@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run()



