from flask import render_template_string, request, redirect, url_for, flash
from datetime import datetime
from models import db, Todo
from templates import HOME_TEMPLATE, API_INFO_TEMPLATE

def register_web_routes(app):
    """ลงทะเบียน Web Routes ทั้งหมด"""
    
    @app.route('/')
    def web_home():
        """หน้าหลักแสดงรายการ Todo ในรูปแบบตาราง"""
        try:
            todos = Todo.query.order_by(Todo.is_completed.asc(), Todo.created_at.desc()).all()
            
            # คำนวณสถิติ
            total = len(todos)
            completed = sum(1 for todo in todos if todo.is_completed)
            pending = total - completed
            completion_rate = (completed / total * 100) if total > 0 else 0
            
            stats = {
                'total': total,
                'completed': completed,
                'pending': pending,
                'completion_rate': completion_rate
            }
            
            return render_template_string(HOME_TEMPLATE, todos=todos, stats=stats)
        except Exception as e:
            flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
            return render_template_string(HOME_TEMPLATE, todos=[], stats={'total': 0, 'completed': 0, 'pending': 0, 'completion_rate': 0})

    @app.route('/web/add', methods=['POST'])
    def web_add_todo():
        """เพิ่ม Todo ใหม่ผ่าน Web Form"""
        try:
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            
            if not title:
                flash('กรุณากรอกชื่องาน', 'error')
                return redirect(url_for('web_home'))
            
            new_todo = Todo(
                id=str(int(datetime.now().timestamp() * 1000)),
                title=title,
                description=description,
                is_completed=False
            )
            
            db.session.add(new_todo)
            db.session.commit()
            
            flash(f'เพิ่มงาน "{title}" สำเร็จ', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาดในการเพิ่มงาน: {str(e)}', 'error')
        
        return redirect(url_for('web_home'))

    @app.route('/web/edit/<string:todo_id>', methods=['POST'])
    def web_edit_todo(todo_id):
        """แก้ไข Todo ผ่าน Web Form"""
        try:
            todo = Todo.query.get(todo_id)
            if not todo:
                flash('ไม่พบงานที่ระบุ', 'error')
                return redirect(url_for('web_home'))
            
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            
            if not title:
                flash('กรุณากรอกชื่องาน', 'error')
                return redirect(url_for('web_home'))
            
            todo.title = title
            todo.description = description
            todo.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'แก้ไขงาน "{title}" สำเร็จ', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาดในการแก้ไขงาน: {str(e)}', 'error')
        
        return redirect(url_for('web_home'))

    @app.route('/web/toggle/<string:todo_id>', methods=['POST'])
    def web_toggle_todo(todo_id):
        """เปลี่ยนสถานะ Todo ผ่าน Web"""
        try:
            todo = Todo.query.get(todo_id)
            if not todo:
                flash('ไม่พบงานที่ระบุ', 'error')
                return redirect(url_for('web_home'))
            
            todo.is_completed = not todo.is_completed
            todo.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            status_text = 'เสร็จแล้ว' if todo.is_completed else 'ยังไม่เสร็จ'
            flash(f'เปลี่ยนสถานะงาน "{todo.title}" เป็น "{status_text}"', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาดในการเปลี่ยนสถานะ: {str(e)}', 'error')
        
        return redirect(url_for('web_home'))

    @app.route('/web/delete/<string:todo_id>', methods=['POST'])
    def web_delete_todo(todo_id):
        """ลบ Todo ผ่าน Web"""
        try:
            todo = Todo.query.get(todo_id)
            if not todo:
                flash('ไม่พบงานที่ระบุ', 'error')
                return redirect(url_for('web_home'))
            
            title = todo.title
            db.session.delete(todo)
            db.session.commit()
            
            flash(f'ลบงาน "{title}" สำเร็จ', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาดในการลบงาน: {str(e)}', 'error')
        
        return redirect(url_for('web_home'))

    @app.route('/web/delete-completed', methods=['POST'])
    def web_delete_completed():
        """ลบงานที่เสร็จแล้วทั้งหมดผ่าน Web"""
        try:
            completed_todos = Todo.query.filter_by(is_completed=True).all()
            count = len(completed_todos)
            
            if count == 0:
                flash('ไม่มีงานที่เสร็จแล้วให้ลบ', 'error')
                return redirect(url_for('web_home'))
            
            for todo in completed_todos:
                db.session.delete(todo)
            
            db.session.commit()
            
            flash(f'ลบงานที่เสร็จแล้ว {count} รายการสำเร็จ', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาดในการลบงาน: {str(e)}', 'error')
        
        return redirect(url_for('web_home'))

    @app.route('/api-docs')
    def api_info():
        """หน้าข้อมูล API Documentation"""
        return render_template_string(API_INFO_TEMPLATE)