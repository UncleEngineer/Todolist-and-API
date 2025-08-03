from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from werkzeug.exceptions import BadRequest

# Import routes
from web_routes import register_web_routes
from api_routes import register_api_routes
from models import db, Todo

# สร้าง Flask app
app = Flask(__name__)

# กำหนดค่า Secret Key สำหรับ Flash Messages
app.secret_key = 'your-secret-key-here-change-in-production'

# กำหนดค่า CORS เพื่อให้ Flutter เชื่อมต่อได้
CORS(app)

# กำหนดค่าฐานข้อมูล SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "todos.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# เริ่มต้น SQLAlchemy
db.init_app(app)

# ลงทะเบียน routes
register_web_routes(app)
register_api_routes(app)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'ไม่พบ endpoint ที่ระบุ'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'success': False,
        'message': 'เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์'
    }), 500

if __name__ == '__main__':
    # สร้างตารางในฐานข้อมูล
    with app.app_context():
        db.create_all()
        
        # เพิ่มข้อมูลตัวอย่างถ้ายังไม่มี
        if Todo.query.count() == 0:
            sample_todos = [
                Todo(
                    id='1',
                    title='ซื้อของใช้ในบ้าน',
                    description='ซื้อข้าว น้ำมัน และผักผลไม้',
                    is_completed=False
                ),
                Todo(
                    id='2',
                    title='ทำงานบ้าน',
                    description='เก็บห้องนอนและล้างจาน',
                    is_completed=True
                ),
                Todo(
                    id='3',
                    title='ออกกำลังกาย',
                    description='วิ่งเก็บสเต็ป 30 นาที',
                    is_completed=False
                ),
                Todo(
                    id='4',
                    title='อ่านหนังสือ',
                    description='อ่านหนังสือเกี่ยวกับการพัฒนาตนเอง',
                    is_completed=True
                ),
                Todo(
                    id='5',
                    title='เรียนออนไลน์',
                    description='เรียน Flutter และ Python API Development',
                    is_completed=False
                )
            ]
            
            for todo in sample_todos:
                db.session.add(todo)
            
            db.session.commit()
            print("✅ เพิ่มข้อมูลตัวอย่างแล้ว")
    
    print("🚀 เริ่มต้น Todo Management Server...")
    print("🌐 Web Interface: http://localhost:5000")
    print("📋 API Documentation: http://localhost:5000/api-docs")
    print("🔗 API Endpoint: http://localhost:5000/api")
    app.run(debug=True, host='0.0.0.0', port=5000)