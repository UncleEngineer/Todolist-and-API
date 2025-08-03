import requests

# เพิ่ม Todo ใหม่
def create_data():
    new_todo = {
        "title": "เรียน Python",
        "description": "เรียนการสร้าง API",
        "is_completed": False
    }

    response = requests.post("http://localhost:5000/api/todos", json=new_todo)
    print(response.json())

def read_data():
    # ดึงรายการทั้งหมด
    response = requests.get("http://localhost:5000/api/todos")
    todos = response.json()
    print(todos)


# read_data()
def update_data(todo_id = 1754209231111):
    # แก้ไข Todo
    
    updated_data = {
        "title": "เรียน Python (อัปเดต)",
        "description": "เรียน API และ Database",
        "is_completed": True
    }

    response = requests.put(f"http://localhost:5000/api/todos/{todo_id}", json=updated_data)

    # เปลี่ยนสถานะ (เสร็จ/ไม่เสร็จ)
    # response = requests.patch(f"http://localhost:5000/api/todos/{todo_id}/toggle")

def delete_data(todo_id):
    response = requests.delete(f"http://localhost:5000/api/todos/{todo_id}")

delete_data(2)

# update_data()
read_data()

