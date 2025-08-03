from flask import request, jsonify
from datetime import datetime
from werkzeug.exceptions import BadRequest
from models import db, Todo

def validate_todo_data(data):
    """Helper function สำหรับตรวจสอบข้อมูล"""
    if not data:
        raise BadRequest("ไม่มีข้อมูลที่ส่งมา")
    
    if 'title' not in data or not data['title'].strip():
        raise BadRequest("ต้องระบุชื่องาน")
    
    return True

def register_api_routes(app):
    """ลงทะเบียน API Routes ทั้งหมด"""
    
    @app.route('/api', methods=['GET'])
    def api_home():
        """หน้าแรกแสดงข้อมูล API"""
        return jsonify({
            'message': 'Todo List API',
            'version': '1.0.0',
            'web_interface': request.url_root,
            'api_docs': request.url_root + 'api-docs',
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