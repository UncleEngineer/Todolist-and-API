from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from werkzeug.exceptions import BadRequest

# สร้าง Flask app
app = Flask(__name__)

# กำหนดค่า CORS เพื่อให้ Flutter เชื่อมต่อได้
CORS(app)

# กำหนดค่าฐานข้อมูล SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "todos.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# เริ่มต้น SQLAlchemy
db = SQLAlchemy(app)

# โมเดล Todo
class Todo(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# สร้างตารางในฐานข้อมูล
with app.app_context():
    db.create_all()

# Helper function สำหรับตรวจสอบข้อมูล
def validate_todo_data(data):
    if not data:
        raise BadRequest("ไม่มีข้อมูลที่ส่งมา")
    
    if 'title' not in data or not data['title'].strip():
        raise BadRequest("ต้องระบุชื่องาน")
    
    return True

# Route: ดึงข้อมูล Todo ทั้งหมด
@app.route('/api/todos', methods=['GET'])
def get_todos():
    """ดึงรายการ Todo ทั้งหมด"""
    try:
        todos = Todo.query.order_by(Todo.created_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [todo.to_dict() for todo in todos],
            'message': 'ดึงข้อมูลสำเร็จ'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500

# Route: ดึงข้อมูล Todo ตาม ID
@app.route('/api/todos/<string:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """ดึงข้อมูล Todo ตาม ID"""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({
                'success': False,
                'message': 'ไม่พบงานที่ระบุ'
            }), 404
        
        return jsonify({
            'success': True,
            'data': todo.to_dict(),
            'message': 'ดึงข้อมูลสำเร็จ'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500

# Route: เพิ่ม Todo ใหม่
@app.route('/api/todos', methods=['POST'])
def create_todo():
    """เพิ่ม Todo ใหม่"""
    try:
        data = request.get_json()
        validate_todo_data(data)
        
        # ตรวจสอบว่า ID ซ้ำหรือไม่
        if 'id' in data and Todo.query.get(data['id']):
            return jsonify({
                'success': False,
                'message': 'ID นี้มีอยู่แล้ว'
            }), 400
        
        # สร้าง Todo ใหม่
        todo = Todo(
            id=data.get('id', str(int(datetime.now().timestamp() * 1000))),
            title=data['title'].strip(),
            description=data.get('description', '').strip(),
            is_completed=data.get('is_completed', False)
        )
        
        db.session.add(todo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': todo.to_dict(),
            'message': 'เพิ่มงานสำเร็จ'
        }), 201
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500

# Route: แก้ไข Todo
@app.route('/api/todos/<string:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """แก้ไข Todo"""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({
                'success': False,
                'message': 'ไม่พบงานที่ระบุ'
            }), 404
        
        data = request.get_json()
        validate_todo_data(data)
        
        # อัปเดตข้อมูล
        todo.title = data['title'].strip()
        todo.description = data.get('description', '').strip()
        todo.is_completed = data.get('is_completed', todo.is_completed)
        todo.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': todo.to_dict(),
            'message': 'แก้ไขงานสำเร็จ'
        }), 200
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500

# Route: อัปเดตสถานะ Todo (เสร็จ/ไม่เสร็จ)
@app.route('/api/todos/<string:todo_id>/toggle', methods=['PATCH'])
def toggle_todo(todo_id):
    """เปลี่ยนสถานะงาน (เสร็จ/ไม่เสร็จ)"""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({
                'success': False,
                'message': 'ไม่พบงานที่ระบุ'
            }), 404
        
        # เปลี่ยนสถานะ
        todo.is_completed = not todo.is_completed
        todo.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        status_text = 'เสร็จแล้ว' if todo.is_completed else 'ยังไม่เสร็จ'
        
        return jsonify({
            'success': True,
            'data': todo.to_dict(),
            'message': f'เปลี่ยนสถานะเป็น "{status_text}" สำเร็จ'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500

# Route: ลบ Todo
@app.route('/api/todos/<string:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """ลบ Todo"""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({
                'success': False,
                'message': 'ไม่พบงานที่ระบุ'
            }), 404
        
        db.session.delete(todo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'ลบงานสำเร็จ'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500

# Route: ดึงสถิติ Todo
@app.route('/api/todos/stats', methods=['GET'])
def get_stats():
    """ดึงสถิติ Todo"""
    try:
        total = Todo.query.count()
        completed = Todo.query.filter_by(is_completed=True).count()
        pending = total - completed
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'completed': completed,
                'pending': pending,
                'completion_rate': round((completed / total * 100) if total > 0 else 0, 2)
            },
            'message': 'ดึงสถิติสำเร็จ'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500

# Route: ลบงานที่เสร็จแล้วทั้งหมด
@app.route('/api/todos/completed', methods=['DELETE'])
def delete_completed_todos():
    """ลบงานที่เสร็จแล้วทั้งหมด"""
    try:
        completed_todos = Todo.query.filter_by(is_completed=True).all()
        count = len(completed_todos)
        
        if count == 0:
            return jsonify({
                'success': True,
                'message': 'ไม่มีงานที่เสร็จแล้วให้ลบ'
            }), 200
        
        for todo in completed_todos:
            db.session.delete(todo)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'ลบงานที่เสร็จแล้ว {count} รายการ'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500

# Route: หน้าแรก (แสดงข้อมูล API)
@app.route('/', methods=['GET'])
def home():
    """หน้าแรกแสดงข้อมูล API"""
    return jsonify({
        'message': 'Todo List API',
        'version': '1.0.0',
        'endpoints': {
            'GET /api/todos': 'ดึงรายการ Todo ทั้งหมด',
            'GET /api/todos/<id>': 'ดึง Todo ตาม ID',
            'POST /api/todos': 'เพิ่ม Todo ใหม่',
            'PUT /api/todos/<id>': 'แก้ไข Todo',
            'PATCH /api/todos/<id>/toggle': 'เปลี่ยนสถานะ Todo',
            'DELETE /api/todos/<id>': 'ลบ Todo',
            'GET /api/todos/stats': 'ดึงสถิติ Todo',
            'DELETE /api/todos/completed': 'ลบงานที่เสร็จแล้วทั้งหมด'
        }
    })

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
    # เพิ่มข้อมูลตัวอย่างถ้ายังไม่มี
    with app.app_context():
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
                )
            ]
            
            for todo in sample_todos:
                db.session.add(todo)
            
            db.session.commit()
            print("✅ เพิ่มข้อมูลตัวอย่างแล้ว")
    
    print("🚀 เริ่มต้น Todo API Server...")
    print("📋 API Documentation: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)