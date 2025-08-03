# HTML Templates สำหรับ Web Interface

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo List Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            background-color: #f8f9fa; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        }
        .navbar { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        }
        .card { 
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
            border: none; 
            border-radius: 10px; 
        }
        .stats-card { 
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
            color: white; 
        }
        .btn-custom { 
            border-radius: 25px; 
        }
        .table-container { 
            background: white; 
            border-radius: 10px; 
            padding: 20px; 
        }
        .completed-row { 
            background-color: #f8f9fa; 
            opacity: 0.8; 
        }
        .completed-text { 
            text-decoration: line-through; 
            color: #6c757d; 
        }
        .status-badge { 
            font-size: 0.8em; 
        }
        .action-buttons .btn { 
            margin: 0 2px; 
        }
        .fade-in { 
            animation: fadeIn 0.5s ease-in; 
        }
        @keyframes fadeIn { 
            from { opacity: 0; transform: translateY(20px); } 
            to { opacity: 1; transform: translateY(0); } 
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-tasks me-2"></i>Todo Management
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/api-docs">
                    <i class="fas fa-code me-1"></i>API Docs
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }} alert-dismissible fade show" role="alert">
                    <i class="fas fa-{{ 'check-circle' if category == 'success' else 'exclamation-triangle' }} me-2"></i>
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Statistics Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card stats-card fade-in">
                    <div class="card-body text-center">
                        <i class="fas fa-list fa-2x mb-2"></i>
                        <h3>{{ stats.total }}</h3>
                        <p class="mb-0">งานทั้งหมด</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white fade-in">
                    <div class="card-body text-center">
                        <i class="fas fa-check-circle fa-2x mb-2"></i>
                        <h3>{{ stats.completed }}</h3>
                        <p class="mb-0">เสร็จแล้ว</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-warning text-white fade-in">
                    <div class="card-body text-center">
                        <i class="fas fa-clock fa-2x mb-2"></i>
                        <h3>{{ stats.pending }}</h3>
                        <p class="mb-0">รอดำเนินการ</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-info text-white fade-in">
                    <div class="card-body text-center">
                        <i class="fas fa-percentage fa-2x mb-2"></i>
                        <h3>{{ "%.1f"|format(stats.completion_rate) }}%</h3>
                        <p class="mb-0">ความสำเร็จ</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add New Todo Button -->
        <div class="row mb-3">
            <div class="col-12">
                <button type="button" class="btn btn-primary btn-custom" data-bs-toggle="modal" data-bs-target="#addTodoModal">
                    <i class="fas fa-plus me-2"></i>เพิ่มงานใหม่
                </button>
                <a href="/" class="btn btn-outline-secondary btn-custom ms-2">
                    <i class="fas fa-sync-alt me-2"></i>รีเฟรช
                </a>
                {% if stats.completed > 0 %}
                <button type="button" class="btn btn-outline-danger btn-custom ms-2" onclick="deleteCompleted()">
                    <i class="fas fa-trash me-2"></i>ลบงานที่เสร็จแล้ว
                </button>
                {% endif %}
            </div>
        </div>

        <!-- Todo Table -->
        <div class="table-container fade-in">
            <h4 class="mb-3">
                <i class="fas fa-table me-2"></i>รายการงาน
                {% if todos %}({{ todos|length }} รายการ){% endif %}
            </h4>
            
            {% if todos %}
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th width="5%">#</th>
                            <th width="25%">ชื่องาน</th>
                            <th width="30%">รายละเอียด</th>
                            <th width="10%">สถานะ</th>
                            <th width="15%">วันที่สร้าง</th>
                            <th width="15%">การจัดการ</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for todo in todos %}
                        <tr class="{{ 'completed-row' if todo.is_completed else '' }}">
                            <td>{{ loop.index }}</td>
                            <td class="{{ 'completed-text' if todo.is_completed else '' }}">
                                <strong>{{ todo.title }}</strong>
                            </td>
                            <td class="{{ 'completed-text' if todo.is_completed else '' }}">
                                {{ todo.description if todo.description else '-' }}
                            </td>
                            <td>
                                {% if todo.is_completed %}
                                    <span class="badge bg-success status-badge">
                                        <i class="fas fa-check me-1"></i>เสร็จแล้ว
                                    </span>
                                {% else %}
                                    <span class="badge bg-warning status-badge">
                                        <i class="fas fa-clock me-1"></i>รอดำเนินการ
                                    </span>
                                {% endif %}
                            </td>
                            <td>
                                <small>{{ todo.created_at.strftime('%d/%m/%Y %H:%M') if todo.created_at else '-' }}</small>
                            </td>
                            <td>
                                <div class="action-buttons">
                                    <button class="btn btn-sm btn-outline-{{ 'secondary' if todo.is_completed else 'success' }}" 
                                            onclick="toggleTodo('{{ todo.id }}')" title="เปลี่ยนสถานะ">
                                        <i class="fas fa-{{ 'undo' if todo.is_completed else 'check' }}"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-primary" 
                                            onclick="editTodo('{{ todo.id }}', '{{ todo.title|replace("'", "\\'") }}', '{{ todo.description|replace("'", "\\'") }}')" 
                                            title="แก้ไข">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" 
                                            onclick="deleteTodo('{{ todo.id }}', '{{ todo.title|replace("'", "\\'") }}')" title="ลบ">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <div class="text-center py-5">
                <i class="fas fa-inbox fa-4x text-muted mb-3"></i>
                <h5 class="text-muted">ยังไม่มีงานในรายการ</h5>
                <p class="text-muted">เริ่มต้นโดยการเพิ่มงานใหม่</p>
            </div>
            {% endif %}
        </div>
    </div>

    <!-- Add Todo Modal -->
    <div class="modal fade" id="addTodoModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <form method="POST" action="/web/add">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-plus me-2"></i>เพิ่มงานใหม่
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="title" class="form-label">ชื่องาน *</label>
                            <input type="text" class="form-control" id="title" name="title" required>
                        </div>
                        <div class="mb-3">
                            <label for="description" class="form-label">รายละเอียด</label>
                            <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save me-2"></i>บันทึก
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Edit Todo Modal -->
    <div class="modal fade" id="editTodoModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <form method="POST" id="editTodoForm">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-edit me-2"></i>แก้ไขงาน
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="edit_title" class="form-label">ชื่องาน *</label>
                            <input type="text" class="form-control" id="edit_title" name="title" required>
                        </div>
                        <div class="mb-3">
                            <label for="edit_description" class="form-label">รายละเอียด</label>
                            <textarea class="form-control" id="edit_description" name="description" rows="3"></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save me-2"></i>บันทึกการแก้ไข
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function toggleTodo(todoId) {
            if (confirm('คุณต้องการเปลี่ยนสถานะของงานนี้หรือไม่?')) {
                fetch(`/web/toggle/${todoId}`, { method: 'POST' })
                    .then(response => {
                        if (response.ok) {
                            location.reload();
                        } else {
                            alert('เกิดข้อผิดพลาดในการเปลี่ยนสถานะ');
                        }
                    })
                    .catch(error => {
                        alert('เกิดข้อผิดพลาด: ' + error.message);
                    });
            }
        }

        function editTodo(todoId, title, description) {
            document.getElementById('edit_title').value = title;
            document.getElementById('edit_description').value = description;
            document.getElementById('editTodoForm').action = `/web/edit/${todoId}`;
            
            const editModal = new bootstrap.Modal(document.getElementById('editTodoModal'));
            editModal.show();
        }

        function deleteTodo(todoId, title) {
            if (confirm(`คุณต้องการลบงาน "${title}" หรือไม่?`)) {
                fetch(`/web/delete/${todoId}`, { method: 'POST' })
                    .then(response => {
                        if (response.ok) {
                            location.reload();
                        } else {
                            alert('เกิดข้อผิดพลาดในการลบ');
                        }
                    })
                    .catch(error => {
                        alert('เกิดข้อผิดพลาด: ' + error.message);
                    });
            }
        }

        function deleteCompleted() {
            if (confirm('คุณต้องการลบงานที่เสร็จแล้วทั้งหมดหรือไม่?')) {
                fetch('/web/delete-completed', { method: 'POST' })
                    .then(response => {
                        if (response.ok) {
                            location.reload();
                        } else {
                            alert('เกิดข้อผิดพลาดในการลบ');
                        }
                    })
                    .catch(error => {
                        alert('เกิดข้อผิดพลาด: ' + error.message);
                    });
            }
        }

        // Auto hide alerts after 5 seconds
        setTimeout(function() {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            });
        }, 5000);
    </script>
</body>
</html>
"""

API_INFO_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo API Documentation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border: none; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        .endpoint { background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .method-get { color: #28a745; }
        .method-post { color: #007bff; }
        .method-put { color: #ffc107; }
        .method-patch { color: #6f42c1; }
        .method-delete { color: #dc3545; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-tasks me-2"></i>Todo Management
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">
                    <i class="fas fa-home me-1"></i>หน้าหลัก
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h3><i class="fas fa-code me-2"></i>Todo List API Documentation</h3>
                        <p class="mb-0">REST API สำหรับจัดการรายการงาน (Todo List)</p>
                    </div>
                    <div class="card-body">
                        <div class="mb-4">
                            <h5>Base URL</h5>
                            <code>{{ request.url_root }}api</code>
                        </div>

                        <div class="mb-4">
                            <h5>API Endpoints</h5>
                            
                            <div class="endpoint">
                                <strong class="method-get">GET</strong> <code>/api/todos</code>
                                <p class="mb-1">ดึงรายการ Todo ทั้งหมด</p>
                            </div>

                            <div class="endpoint">
                                <strong class="method-get">GET</strong> <code>/api/todos/{id}</code>
                                <p class="mb-1">ดึง Todo ตาม ID</p>
                            </div>

                            <div class="endpoint">
                                <strong class="method-post">POST</strong> <code>/api/todos</code>
                                <p class="mb-1">เพิ่ม Todo ใหม่</p>
                                <small class="text-muted">Body: {"title": "string", "description": "string", "is_completed": boolean}</small>
                            </div>

                            <div class="endpoint">
                                <strong class="method-put">PUT</strong> <code>/api/todos/{id}</code>
                                <p class="mb-1">แก้ไข Todo</p>
                                <small class="text-muted">Body: {"title": "string", "description": "string", "is_completed": boolean}</small>
                            </div>

                            <div class="endpoint">
                                <strong class="method-patch">PATCH</strong> <code>/api/todos/{id}/toggle</code>
                                <p class="mb-1">เปลี่ยนสถานะ Todo (เสร็จ/ไม่เสร็จ)</p>
                            </div>

                            <div class="endpoint">
                                <strong class="method-delete">DELETE</strong> <code>/api/todos/{id}</code>
                                <p class="mb-1">ลบ Todo</p>
                            </div>

                            <div class="endpoint">
                                <strong class="method-get">GET</strong> <code>/api/todos/stats</code>
                                <p class="mb-1">ดึงสถิติ Todo</p>
                            </div>

                            <div class="endpoint">
                                <strong class="method-delete">DELETE</strong> <code>/api/todos/completed</code>
                                <p class="mb-1">ลบงานที่เสร็จแล้วทั้งหมด</p>
                            </div>
                        </div>

                        <div class="mb-4">
                            <h5>Response Format</h5>
                            <pre class="bg-light p-3"><code>{
  "success": true,
  "data": {...},
  "message": "string"
}</code></pre>
                        </div>

                        <div class="mb-4">
                            <h5>Web Interface</h5>
                            <div class="endpoint">
                                <strong class="method-get">GET</strong> <code>/</code>
                                <p class="mb-1">หน้าหลักจัดการ Todo</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""