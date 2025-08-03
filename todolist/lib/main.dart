import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Todo List',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: TodoListScreen(),
    );
  }
}

class Todo {
  String id;
  String title;
  String description;
  bool isCompleted;
  DateTime? createdAt;
  DateTime? updatedAt;

  Todo({
    required this.id,
    required this.title,
    this.description = '',
    this.isCompleted = false,
    this.createdAt,
    this.updatedAt,
  });

  factory Todo.fromJson(Map<String, dynamic> json) {
    return Todo(
      id: json['id'].toString(),
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      isCompleted: json['is_completed'] ?? false,
      createdAt: json['created_at'] != null 
          ? DateTime.tryParse(json['created_at']) 
          : null,
      updatedAt: json['updated_at'] != null 
          ? DateTime.tryParse(json['updated_at']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'is_completed': isCompleted,
    };
  }
}

class ApiService {
  // เปลี่ยน URL นี้ตามที่ Flask Server ของคุณรัน
  static const String baseUrl = 'http://192.168.1.35:5000/api';
  
  // สำหรับ Android Emulator ใช้: http://10.0.2.2:5000/api
  // สำหรับ iOS Simulator ใช้: http://localhost:5000/api
  // สำหรับเครื่องจริง ใช้ IP ของเครื่องที่รัน Flask Server

  static const Map<String, String> headers = {
    'Content-Type': 'application/json',
  };

  // ดึงรายการ Todo ทั้งหมด
  static Future<List<Todo>> getTodos() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/todos'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        if (data['success'] == true && data['data'] != null) {
          final List<dynamic> todosJson = data['data'];
          return todosJson.map((json) => Todo.fromJson(json)).toList();
        }
      }
      throw Exception('ไม่สามารถดึงข้อมูลได้');
    } catch (e) {
      print('Error fetching todos: $e');
      throw Exception('เกิดข้อผิดพลาดในการเชื่อมต่อ: $e');
    }
  }

  // เพิ่ม Todo ใหม่
  static Future<Todo> createTodo(Todo todo) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/todos'),
        headers: headers,
        body: json.encode(todo.toJson()),
      );

      if (response.statusCode == 201) {
        final Map<String, dynamic> data = json.decode(response.body);
        if (data['success'] == true && data['data'] != null) {
          return Todo.fromJson(data['data']);
        }
      }
      
      final errorData = json.decode(response.body);
      throw Exception(errorData['message'] ?? 'ไม่สามารถเพิ่มงานได้');
    } catch (e) {
      print('Error creating todo: $e');
      throw Exception('เกิดข้อผิดพลาดในการเพิ่มงาน: $e');
    }
  }

  // แก้ไข Todo
  static Future<Todo> updateTodo(Todo todo) async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/todos/${todo.id}'),
        headers: headers,
        body: json.encode(todo.toJson()),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        if (data['success'] == true && data['data'] != null) {
          return Todo.fromJson(data['data']);
        }
      }
      
      final errorData = json.decode(response.body);
      throw Exception(errorData['message'] ?? 'ไม่สามารถแก้ไขงานได้');
    } catch (e) {
      print('Error updating todo: $e');
      throw Exception('เกิดข้อผิดพลาดในการแก้ไขงาน: $e');
    }
  }

  // เปลี่ยนสถานะ Todo
  static Future<Todo> toggleTodo(String id) async {
    try {
      final response = await http.patch(
        Uri.parse('$baseUrl/todos/$id/toggle'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        if (data['success'] == true && data['data'] != null) {
          return Todo.fromJson(data['data']);
        }
      }
      
      final errorData = json.decode(response.body);
      throw Exception(errorData['message'] ?? 'ไม่สามารถเปลี่ยนสถานะได้');
    } catch (e) {
      print('Error toggling todo: $e');
      throw Exception('เกิดข้อผิดพลาดในการเปลี่ยนสถานะ: $e');
    }
  }

  // ลบ Todo
  static Future<void> deleteTodo(String id) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/todos/$id'),
        headers: headers,
      );

      if (response.statusCode != 200) {
        final errorData = json.decode(response.body);
        throw Exception(errorData['message'] ?? 'ไม่สามารถลบงานได้');
      }
    } catch (e) {
      print('Error deleting todo: $e');
      throw Exception('เกิดข้อผิดพลาดในการลบงาน: $e');
    }
  }

  // ดึงสถิติ
  static Future<Map<String, dynamic>> getStats() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/todos/stats'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        if (data['success'] == true && data['data'] != null) {
          return data['data'];
        }
      }
      throw Exception('ไม่สามารถดึงสถิติได้');
    } catch (e) {
      print('Error fetching stats: $e');
      return {'total': 0, 'completed': 0, 'pending': 0, 'completion_rate': 0.0};
    }
  }
}

class TodoListScreen extends StatefulWidget {
  @override
  _TodoListScreenState createState() => _TodoListScreenState();
}

class _TodoListScreenState extends State<TodoListScreen> {
  List<Todo> todos = [];
  bool isLoading = false;
  bool isOnline = false;
  String? errorMessage;
  Map<String, dynamic> stats = {};
  
  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadTodos();
  }

  // โหลดข้อมูล Todo จาก API
  Future<void> _loadTodos() async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
      final fetchedTodos = await ApiService.getTodos();
      final fetchedStats = await ApiService.getStats();
      
      setState(() {
        todos = fetchedTodos;
        stats = fetchedStats;
        isOnline = true;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        errorMessage = e.toString();
        isOnline = false;
        isLoading = false;
      });
      
      _showErrorSnackBar('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้: $e');
    }
  }

  // แสดง SnackBar แจ้งข้อผิดพลาด
  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        duration: Duration(seconds: 3),
        action: SnackBarAction(
          label: 'ลองใหม่',
          textColor: Colors.white,
          onPressed: _loadTodos,
        ),
      ),
    );
  }

  // แสดง SnackBar แจ้งความสำเร็จ
  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
        duration: Duration(seconds: 2),
      ),
    );
  }

  // เพิ่ม Todo ใหม่
  void _addTodo() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('เพิ่มงานใหม่'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: _titleController,
                decoration: InputDecoration(
                  labelText: 'ชื่องาน *',
                  hintText: 'กรอกชื่องาน',
                  border: OutlineInputBorder(),
                ),
              ),
              SizedBox(height: 16),
              TextField(
                controller: _descriptionController,
                decoration: InputDecoration(
                  labelText: 'รายละเอียด',
                  hintText: 'กรอกรายละเอียดงาน (ไม่บังคับ)',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                _titleController.clear();
                _descriptionController.clear();
                Navigator.of(context).pop();
              },
              child: Text('ยกเลิก'),
            ),
            ElevatedButton(
              onPressed: () => _submitAddTodo(),
              child: Text('เพิ่ม'),
            ),
          ],
        );
      },
    );
  }

  // ส่งข้อมูลเพิ่ม Todo
  Future<void> _submitAddTodo() async {
    if (_titleController.text.trim().isEmpty) {
      _showErrorSnackBar('กรุณากรอกชื่องาน');
      return;
    }

    final newTodo = Todo(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      title: _titleController.text.trim(),
      description: _descriptionController.text.trim(),
    );

    try {
      final createdTodo = await ApiService.createTodo(newTodo);
      
      setState(() {
        todos.add(createdTodo);
      });
      
      _titleController.clear();
      _descriptionController.clear();
      Navigator.of(context).pop();
      
      _showSuccessSnackBar('เพิ่มงานสำเร็จ');
      _loadTodos(); // รีเฟรชข้อมูลเพื่ออัปเดตสถิติ
      
    } catch (e) {
      _showErrorSnackBar('ไม่สามารถเพิ่มงานได้: $e');
    }
  }

  // แก้ไข Todo
  void _editTodo(Todo todo) {
    _titleController.text = todo.title;
    _descriptionController.text = todo.description;

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('แก้ไขงาน'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: _titleController,
                decoration: InputDecoration(
                  labelText: 'ชื่องาน *',
                  hintText: 'กรอกชื่องาน',
                  border: OutlineInputBorder(),
                ),
              ),
              SizedBox(height: 16),
              TextField(
                controller: _descriptionController,
                decoration: InputDecoration(
                  labelText: 'รายละเอียด',
                  hintText: 'กรอกรายละเอียดงาน (ไม่บังคับ)',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                _titleController.clear();
                _descriptionController.clear();
                Navigator.of(context).pop();
              },
              child: Text('ยกเลิก'),
            ),
            ElevatedButton(
              onPressed: () => _submitEditTodo(todo),
              child: Text('บันทึก'),
            ),
          ],
        );
      },
    );
  }

  // ส่งข้อมูลแก้ไข Todo
  Future<void> _submitEditTodo(Todo todo) async {
    if (_titleController.text.trim().isEmpty) {
      _showErrorSnackBar('กรุณากรอกชื่องาน');
      return;
    }

    final updatedTodo = Todo(
      id: todo.id,
      title: _titleController.text.trim(),
      description: _descriptionController.text.trim(),
      isCompleted: todo.isCompleted,
    );

    try {
      final returnedTodo = await ApiService.updateTodo(updatedTodo);
      
      setState(() {
        final index = todos.indexWhere((t) => t.id == todo.id);
        if (index != -1) {
          todos[index] = returnedTodo;
        }
      });
      
      _titleController.clear();
      _descriptionController.clear();
      Navigator.of(context).pop();
      
      _showSuccessSnackBar('แก้ไขงานสำเร็จ');
      
    } catch (e) {
      _showErrorSnackBar('ไม่สามารถแก้ไขงานได้: $e');
    }
  }

  // ลบ Todo
  void _deleteTodo(String id, String title) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('ยืนยันการลบ'),
          content: Text('คุณต้องการลบงาน "$title" หรือไม่?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text('ยกเลิก'),
            ),
            ElevatedButton(
              onPressed: () => _submitDeleteTodo(id),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              child: Text('ลบ', style: TextStyle(color: Colors.white)),
            ),
          ],
        );
      },
    );
  }

  // ส่งคำขอลบ Todo
  Future<void> _submitDeleteTodo(String id) async {
    try {
      await ApiService.deleteTodo(id);
      
      setState(() {
        todos.removeWhere((todo) => todo.id == id);
      });
      
      Navigator.of(context).pop();
      _showSuccessSnackBar('ลบงานสำเร็จ');
      _loadTodos(); // รีเฟรชข้อมูลเพื่ออัปเดตสถิติ
      
    } catch (e) {
      Navigator.of(context).pop();
      _showErrorSnackBar('ไม่สามารถลบงานได้: $e');
    }
  }

  // เปลี่ยนสถานะ Todo
  Future<void> _toggleComplete(String id) async {
    try {
      final updatedTodo = await ApiService.toggleTodo(id);
      
      setState(() {
        final index = todos.indexWhere((todo) => todo.id == id);
        if (index != -1) {
          todos[index] = updatedTodo;
        }
      });
      
      _loadTodos(); // รีเฟรชข้อมูลเพื่ออัปเดตสถิติ
      
    } catch (e) {
      _showErrorSnackBar('ไม่สามารถเปลี่ยนสถานะได้: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    // แยกงานที่ยังไม่เสร็จและเสร็จแล้ว
    List<Todo> incompleteTodos = todos.where((todo) => !todo.isCompleted).toList();
    List<Todo> completedTodos = todos.where((todo) => todo.isCompleted).toList();

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('รายการงาน'),
            if (stats.isNotEmpty)
              Text(
                'ทั้งหมด ${stats['total']} | เสร็จ ${stats['completed']} | เหลือ ${stats['pending']}',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.normal),
              ),
          ],
        ),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        elevation: 2,
        actions: [
          // แสดงสถานะการเชื่อมต่อ
          Container(
            margin: EdgeInsets.only(right: 16),
            child: Center(
              child: Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: isOnline ? Colors.green : Colors.red,
                  shape: BoxShape.circle,
                ),
              ),
            ),
          ),
          // ปุ่มรีเฟรช
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: isLoading ? null : _loadTodos,
          ),
        ],
      ),
      body: isLoading
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('กำลังโหลดข้อมูล...'),
                ],
              ),
            )
          : errorMessage != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.cloud_off,
                        size: 80,
                        color: Colors.grey[400],
                      ),
                      SizedBox(height: 16),
                      Text(
                        'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้',
                        style: TextStyle(
                          fontSize: 18,
                          color: Colors.grey[600],
                        ),
                      ),
                      SizedBox(height: 8),
                      Padding(
                        padding: EdgeInsets.symmetric(horizontal: 32),
                        child: Text(
                          'ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต\nและเซิร์ฟเวอร์ Flask',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[500],
                          ),
                        ),
                      ),
                      SizedBox(height: 24),
                      ElevatedButton.icon(
                        onPressed: _loadTodos,
                        icon: Icon(Icons.refresh),
                        label: Text('ลองใหม่'),
                      ),
                    ],
                  ),
                )
              : todos.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.assignment_outlined,
                            size: 80,
                            color: Colors.grey[400],
                          ),
                          SizedBox(height: 16),
                          Text(
                            'ยังไม่มีงานในรายการ',
                            style: TextStyle(
                              fontSize: 18,
                              color: Colors.grey[600],
                            ),
                          ),
                          SizedBox(height: 8),
                          Text(
                            'กดปุ่ม + เพื่อเพิ่มงานใหม่',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[500],
                            ),
                          ),
                        ],
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: _loadTodos,
                      child: ListView(
                        padding: EdgeInsets.all(16),
                        children: [
                          // งานที่ยังไม่เสร็จ
                          if (incompleteTodos.isNotEmpty) ...[
                            Row(
                              children: [
                                Icon(Icons.pending_actions, color: Colors.blue[700], size: 20),
                                SizedBox(width: 8),
                                Text(
                                  'งานที่ต้องทำ (${incompleteTodos.length})',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.blue[700],
                                  ),
                                ),
                              ],
                            ),
                            SizedBox(height: 8),
                            ...incompleteTodos.map((todo) => _buildTodoItem(todo)).toList(),
                          ],
                          
                          // เว้นระยะระหว่างส่วน
                          if (incompleteTodos.isNotEmpty && completedTodos.isNotEmpty)
                            SizedBox(height: 24),
                          
                          // งานที่เสร็จแล้ว
                          if (completedTodos.isNotEmpty) ...[
                            Row(
                              children: [
                                Icon(Icons.check_circle, color: Colors.green[700], size: 20),
                                SizedBox(width: 8),
                                Text(
                                  'งานที่เสร็จแล้ว (${completedTodos.length})',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.green[700],
                                  ),
                                ),
                              ],
                            ),
                            SizedBox(height: 8),
                            ...completedTodos.map((todo) => _buildTodoItem(todo)).toList(),
                          ],
                        ],
                      ),
                    ),
      floatingActionButton: FloatingActionButton(
        onPressed: isOnline ? _addTodo : null,
        backgroundColor: isOnline ? Colors.blue : Colors.grey,
        foregroundColor: Colors.white,
        child: Icon(Icons.add),
      ),
    );
  }

  Widget _buildTodoItem(Todo todo) {
    return Card(
      margin: EdgeInsets.only(bottom: 8),
      elevation: 2,
      child: ListTile(
        contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Checkbox(
          value: todo.isCompleted,
          onChanged: isOnline ? (_) => _toggleComplete(todo.id) : null,
          activeColor: Colors.green,
        ),
        title: Text(
          todo.title,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w500,
            decoration: todo.isCompleted ? TextDecoration.lineThrough : null,
            color: todo.isCompleted ? Colors.grey[600] : null,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (todo.description.isNotEmpty)
              Padding(
                padding: EdgeInsets.only(top: 4),
                child: Text(
                  todo.description,
                  style: TextStyle(
                    fontSize: 14,
                    color: todo.isCompleted ? Colors.grey[500] : Colors.grey[700],
                  ),
                ),
              ),
            if (todo.createdAt != null)
              Padding(
                padding: EdgeInsets.only(top: 4),
                child: Text(
                  'สร้างเมื่อ: ${_formatDate(todo.createdAt!)}',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[500],
                  ),
                ),
              ),
          ],
        ),
        trailing: isOnline 
            ? PopupMenuButton(
                onSelected: (value) {
                  if (value == 'edit') {
                    _editTodo(todo);
                  } else if (value == 'delete') {
                    _deleteTodo(todo.id, todo.title);
                  }
                },
                itemBuilder: (context) => [
                  PopupMenuItem(
                    value: 'edit',
                    child: Row(
                      children: [
                        Icon(Icons.edit, size: 20, color: Colors.blue),
                        SizedBox(width: 8),
                        Text('แก้ไข'),
                      ],
                    ),
                  ),
                  PopupMenuItem(
                    value: 'delete',
                    child: Row(
                      children: [
                        Icon(Icons.delete, size: 20, color: Colors.red),
                        SizedBox(width: 8),
                        Text('ลบ'),
                      ],
                    ),
                  ),
                ],
              )
            : Icon(Icons.cloud_off, color: Colors.grey),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year} ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }
}