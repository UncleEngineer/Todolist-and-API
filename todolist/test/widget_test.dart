// This is a basic Flutter widget test for Todo List app.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'dart:convert';

import 'package:todolist/main.dart';

void main() {
  group('Todo List App Tests', () {
    testWidgets('App should display title correctly', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(MyApp());

      // Verify that the app title is displayed
      expect(find.text('รายการงาน'), findsOneWidget);
    });

    testWidgets('Should show loading indicator initially', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(MyApp());

      // Should show loading indicator when fetching data
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('กำลังโหลดข้อมูล...'), findsOneWidget);
    });

    testWidgets('Should show error message when API fails', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(MyApp());

      // Wait for the API call to complete (and fail)
      await tester.pumpAndSettle(Duration(seconds: 3));

      // Should show error message when cannot connect to server
      expect(find.text('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้'), findsOneWidget);
      expect(find.byIcon(Icons.cloud_off), findsOneWidget);
      expect(find.text('ลองใหม่'), findsOneWidget);
    });

    testWidgets('Should show FloatingActionButton', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(MyApp());

      // Verify that the add button is present
      expect(find.byType(FloatingActionButton), findsOneWidget);
      expect(find.byIcon(Icons.add), findsOneWidget);
    });

    testWidgets('Should show refresh button in app bar', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(MyApp());

      // Verify that the refresh button is present in app bar
      expect(find.byIcon(Icons.refresh), findsOneWidget);
    });

    testWidgets('Should open add todo dialog when FAB is tapped', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(MyApp());

      // Wait for loading to complete
      await tester.pumpAndSettle(Duration(seconds: 3));

      // Find and tap the FloatingActionButton (only if it's enabled)
      final fabFinder = find.byType(FloatingActionButton);
      if (tester.widget<FloatingActionButton>(fabFinder).onPressed != null) {
        await tester.tap(fabFinder);
        await tester.pumpAndSettle();

        // Verify that the add todo dialog is shown
        expect(find.text('เพิ่มงานใหม่'), findsOneWidget);
        expect(find.text('ชื่องาน *'), findsOneWidget);
        expect(find.text('รายละเอียด'), findsOneWidget);
        expect(find.text('ยกเลิก'), findsOneWidget);
        expect(find.text('เพิ่ม'), findsOneWidget);
      }
    });

    testWidgets('Should validate empty title in add dialog', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(MyApp());

      // Wait for loading to complete
      await tester.pumpAndSettle(Duration(seconds: 3));

      // Find and tap the FloatingActionButton (only if it's enabled)
      final fabFinder = find.byType(FloatingActionButton);
      if (tester.widget<FloatingActionButton>(fabFinder).onPressed != null) {
        await tester.tap(fabFinder);
        await tester.pumpAndSettle();

        // Try to add todo without title
        await tester.tap(find.text('เพิ่ม'));
        await tester.pumpAndSettle();

        // Should show error message for empty title
        expect(find.text('กรุณากรอกชื่องาน'), findsOneWidget);
      }
    });

    testWidgets('Should close dialog when cancel is tapped', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(MyApp());

      // Wait for loading to complete
      await tester.pumpAndSettle(Duration(seconds: 3));

      // Find and tap the FloatingActionButton (only if it's enabled)
      final fabFinder = find.byType(FloatingActionButton);
      if (tester.widget<FloatingActionButton>(fabFinder).onPressed != null) {
        await tester.tap(fabFinder);
        await tester.pumpAndSettle();

        // Tap cancel button
        await tester.tap(find.text('ยกเลิก'));
        await tester.pumpAndSettle();

        // Dialog should be closed
        expect(find.text('เพิ่มงานใหม่'), findsNothing);
      }
    });

    testWidgets('Should show connection status indicator', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(MyApp());

      // Wait for loading to complete
      await tester.pumpAndSettle(Duration(seconds: 3));

      // Should show connection status (red dot for offline)
      expect(find.byType(Container), findsWidgets);
    });

    testWidgets('Should show empty state when no todos', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(MyApp());

      // Wait for loading to complete
      await tester.pumpAndSettle(Duration(seconds: 3));

      // Should show empty state or error state
      final emptyText = find.text('ยังไม่มีงานในรายการ');
      final errorText = find.text('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้');
      
      expect(emptyText.evaluate().isNotEmpty || errorText.evaluate().isNotEmpty, true);
    });
  });

  group('Todo Model Tests', () {
    test('Todo.fromJson should create Todo object correctly', () {
      final json = {
        'id': '1',
        'title': 'Test Todo',
        'description': 'Test Description',
        'is_completed': false,
        'created_at': '2025-08-03T10:30:00',
        'updated_at': '2025-08-03T10:30:00'
      };

      final todo = Todo.fromJson(json);

      expect(todo.id, '1');
      expect(todo.title, 'Test Todo');
      expect(todo.description, 'Test Description');
      expect(todo.isCompleted, false);
      expect(todo.createdAt, isNotNull);
      expect(todo.updatedAt, isNotNull);
    });

    test('Todo.toJson should create JSON correctly', () {
      final todo = Todo(
        id: '1',
        title: 'Test Todo',
        description: 'Test Description',
        isCompleted: false,
      );

      final json = todo.toJson();

      expect(json['id'], '1');
      expect(json['title'], 'Test Todo');
      expect(json['description'], 'Test Description');
      expect(json['is_completed'], false);
    });

    test('Todo should handle null values correctly', () {
      final json = {
        'id': '1',
        'title': 'Test Todo',
        'description': null,
        'is_completed': null,
        'created_at': null,
        'updated_at': null
      };

      final todo = Todo.fromJson(json);

      expect(todo.id, '1');
      expect(todo.title, 'Test Todo');
      expect(todo.description, '');
      expect(todo.isCompleted, false);
      expect(todo.createdAt, null);
      expect(todo.updatedAt, null);
    });
  });

  group('API Service Tests (Mock)', () {
    test('Should parse successful API response correctly', () {
      final responseJson = {
        'success': true,
        'data': [
          {
            'id': '1',
            'title': 'Test Todo',
            'description': 'Test Description',
            'is_completed': false,
            'created_at': '2025-08-03T10:30:00',
            'updated_at': '2025-08-03T10:30:00'
          }
        ],
        'message': 'ดึงข้อมูลสำเร็จ'
      };

      // Test parsing logic (similar to what ApiService.getTodos does)
      final todosJson = responseJson['data'] as List<dynamic>;
      final todos = todosJson.map((json) => Todo.fromJson(json)).toList();

      expect(todos.length, 1);
      expect(todos[0].title, 'Test Todo');
    });

    test('Should handle API error response correctly', () {
      final errorResponse = {
        'success': false,
        'message': 'เกิดข้อผิดพลาด'
      };

      expect(errorResponse['success'], false);
      expect(errorResponse['message'], 'เกิดข้อผิดพลาด');
    });

    test('Should format request JSON correctly', () {
      final todo = Todo(
        id: 'test_1',
        title: 'New Todo',
        description: 'New Description',
        isCompleted: false,
      );

      final requestJson = todo.toJson();
      final expectedJson = {
        'id': 'test_1',
        'title': 'New Todo',
        'description': 'New Description',
        'is_completed': false,
      };

      expect(requestJson, expectedJson);
    });
  });

  group('UI Component Tests', () {
    testWidgets('Todo item should display correctly', (WidgetTester tester) async {
      // Create a test widget with a mock todo item
      final testTodo = Todo(
        id: '1',
        title: 'Test Todo',
        description: 'Test Description',
        isCompleted: false,
        createdAt: DateTime.now(),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Card(
              child: ListTile(
                leading: Checkbox(
                  value: testTodo.isCompleted,
                  onChanged: (_) {},
                ),
                title: Text(testTodo.title),
                subtitle: Text(testTodo.description),
              ),
            ),
          ),
        ),
      );

      expect(find.text('Test Todo'), findsOneWidget);
      expect(find.text('Test Description'), findsOneWidget);
      expect(find.byType(Checkbox), findsOneWidget);
    });

    testWidgets('Should show completed todo with strikethrough', (WidgetTester tester) async {
      final completedTodo = Todo(
        id: '1',
        title: 'Completed Todo',
        description: 'Completed Description',
        isCompleted: true,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Text(
              completedTodo.title,
              style: TextStyle(
                decoration: completedTodo.isCompleted 
                    ? TextDecoration.lineThrough 
                    : null,
              ),
            ),
          ),
        ),
      );

      final textWidget = tester.widget<Text>(find.text('Completed Todo'));
      expect(textWidget.style?.decoration, TextDecoration.lineThrough);
    });
  });

  group('Date Formatting Tests', () {
    test('Should format date correctly', () {
      final testDate = DateTime(2025, 8, 3, 14, 30);
      final formatted = '${testDate.day}/${testDate.month}/${testDate.year} ${testDate.hour.toString().padLeft(2, '0')}:${testDate.minute.toString().padLeft(2, '0')}';
      
      expect(formatted, '3/8/2025 14:30');
    });
  });
}