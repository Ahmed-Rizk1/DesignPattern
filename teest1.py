import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
import pandas as pd
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import calendar
from datetime import datetime
import random
from tkinter.simpledialog import askstring

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.connection = sqlite3.connect("students.db")
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                grade TEXT,
                comments TEXT
            )
        """)
        self.connection.commit()

    def get_connection(self):
        return self.connection

class StudentProxy:
    def __init__(self):
        self._real_student = None

    def _initialize(self):
        self._real_student = Student()

    def save(self, name, age, grade, comments=None):
        if self._real_student is None:
            self._initialize()
        self._real_student.save(name, age, grade, comments)

    def get_all(self):
        if self._real_student is None:
            self._initialize()
        return self._real_student.get_all()

    def delete(self, student_id):
        if self._real_student is None:
            self._initialize()
        self._real_student.delete(student_id)

    def update(self, student_id, name, age, grade, comments):
        if self._real_student is None:
            self._initialize()
        self._real_student.update(student_id, name, age, grade, comments)

    def search_by_name(self, name):
        if self._real_student is None:
            self._initialize()
        return self._real_student.search_by_name(name)

    def search_by_age(self, age):
        if self._real_student is None:
            self._initialize()
        return self._real_student.search_by_age(age)

class Student:
    def __init__(self, name=None, age=None, grade=None, comments=None):
        self.name = name
        self.age = age
        self.grade = grade
        self.comments = comments

    def save(self, name, age, grade, comments=None):
        db = Database().get_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO students (name, age, grade, comments) VALUES (?, ?, ?, ?)", 
                       (name, age, grade, comments))
        db.commit()

    def get_all(self):
        db = Database().get_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM students")
        return cursor.fetchall()

    def delete(self, student_id):
        db = Database().get_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        db.commit()

    def update(self, student_id, name, age, grade, comments):
        db = Database().get_connection()
        cursor = db.cursor()
        cursor.execute("UPDATE students SET name = ?, age = ?, grade = ?, comments = ? WHERE id = ?", 
                       (name, age, grade, comments, student_id))
        db.commit()

    def search_by_name(self, name):
        db = Database().get_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM students WHERE name LIKE ?", ('%' + name + '%',))
        return cursor.fetchall()

    def search_by_age(self, age):
        db = Database().get_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM students WHERE age = ?", (age,))
        return cursor.fetchall()

    @staticmethod
    def get_average_age():
        db = Database().get_connection()
        cursor = db.cursor()
        cursor.execute("SELECT AVG(age) FROM students")
        return cursor.fetchone()[0]

class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("800x600")

        self.name_label = ttk.Label(root, text="Name:")
        self.name_label.grid(row=0, column=0, padx=10, pady=5)
        self.name_entry = ttk.Entry(root)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        self.age_label = ttk.Label(root, text="Age:")
        self.age_label.grid(row=1, column=0, padx=10, pady=5)
        self.age_entry = ttk.Entry(root)
        self.age_entry.grid(row=1, column=1, padx=10, pady=5)

        self.grade_label = ttk.Label(root, text="Grade:")
        self.grade_label.grid(row=2, column=0, padx=10, pady=5)
        self.grade_entry = ttk.Entry(root)
        self.grade_entry.grid(row=2, column=1, padx=10, pady=5)

        self.comments_label = ttk.Label(root, text="Comments:")
        self.comments_label.grid(row=3, column=0, padx=10, pady=5)
        self.comments_entry = ttk.Entry(root)
        self.comments_entry.grid(row=3, column=1, padx=10, pady=5)

        self.add_button = ttk.Button(root, text="Add Student", command=self.add_student)
        self.add_button.grid(row=4, column=0, padx=10, pady=10)

        self.update_button = ttk.Button(root, text="Update Student", command=self.update_student)
        self.update_button.grid(row=4, column=1, padx=10, pady=10)

        self.search_label = ttk.Label(root, text="Search by Name:")
        self.search_label.grid(row=5, column=0, padx=10, pady=5)
        self.search_entry = ttk.Entry(root)
        self.search_entry.grid(row=5, column=1, padx=10, pady=5)
        self.search_button = ttk.Button(root, text="Search", command=self.search_student)
        self.search_button.grid(row=5, column=2, padx=10, pady=5)

        self.search_age_label = ttk.Label(root, text="Search by Age:")
        self.search_age_label.grid(row=6, column=0, padx=10, pady=5)
        self.search_age_entry = ttk.Entry(root)
        self.search_age_entry.grid(row=6, column=1, padx=10, pady=5)
        self.search_age_button = ttk.Button(root, text="Search by Age", command=self.search_student_by_age)
        self.search_age_button.grid(row=6, column=2, padx=10, pady=5)

        self.export_button = ttk.Button(root, text="Export to CSV", command=self.export_to_csv)
        self.export_button.grid(row=7, column=0, padx=10, pady=10)

        self.stats_button = ttk.Button(root, text="Show Stats", command=self.show_stats)
        self.stats_button.grid(row=7, column=1, padx=10, pady=10)

        self.calendar_button = ttk.Button(root, text="Task Calendar", command=self.show_calendar)
        self.calendar_button.grid(row=7, column=2, padx=10, pady=10)

        self.performance_button = ttk.Button(root, text="Performance Report", command=self.show_performance_report)
        self.performance_button.grid(row=7, column=3, padx=10, pady=10)

        self.recommendations_button = ttk.Button(root, text="AI Recommendations", command=self.show_ai_recommendations)
        self.recommendations_button.grid(row=7, column=4, padx=10, pady=10)

        self.customize_button = ttk.Button(root, text="Customize UI", command=self.customize_ui)
        self.customize_button.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

        self.students_list = ttk.Treeview(root, columns=("ID", "Name", "Age", "Grade", "Comments"), show='headings')
        self.students_list.grid(row=8, column=0, columnspan=3, padx=10, pady=10)
        self.students_list.heading("ID", text="ID")
        self.students_list.heading("Name", text="Name")
        self.students_list.heading("Age", text="Age")
        self.students_list.heading("Grade", text="Grade")
        self.students_list.heading("Comments", text="Comments")

        self.delete_button = ttk.Button(root, text="Delete Student", command=self.delete_student)
        self.delete_button.grid(row=9, column=0, columnspan=3, pady=10)

        self.load_students()

    def add_student(self):
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        grade = self.grade_entry.get().strip()
        comments = self.comments_entry.get().strip()

        if not name or not age or not grade:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            age = int(age)
        except ValueError:
            messagebox.showerror("Error", "Age must be an integer.")
            return

        student_proxy = StudentProxy()
        student_proxy.save(name, age, grade, comments)
        self.clear_fields()
        self.load_students()

    def load_students(self):
        for row in self.students_list.get_children():
            self.students_list.delete(row)
        
        student_proxy = StudentProxy()
        students = student_proxy.get_all()
        for student in students:
            self.students_list.insert("", "end", values=student)

    def delete_student(self):
        selected_student = self.students_list.selection()
        if not selected_student:
            messagebox.showerror("Error", "Please select a student to delete.")
            return

        student_id = self.students_list.item(selected_student)["values"][0]
        student_proxy = StudentProxy()
        student_proxy.delete(student_id)
        self.load_students()

    def update_student(self):
        selected_student = self.students_list.selection()
        if not selected_student:
            messagebox.showerror("Error", "Please select a student to update.")
            return

        student_id = self.students_list.item(selected_student)["values"][0]
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        grade = self.grade_entry.get().strip()
        comments = self.comments_entry.get().strip()

        if not name or not age or not grade:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            age = int(age)
        except ValueError:
            messagebox.showerror("Error", "Age must be an integer.")
            return

        student_proxy = StudentProxy()
        student_proxy.update(student_id, name, age, grade, comments)
        self.clear_fields()
        self.load_students()

    def search_student(self):
        name = self.search_entry.get().strip()
        student_proxy = StudentProxy()
        students = student_proxy.search_by_name(name)
        self.update_students_list(students)

    def search_student_by_age(self):
        age = self.search_age_entry.get().strip()
        try:
            age = int(age)
        except ValueError:
            messagebox.showerror("Error", "Age must be an integer.")
            return

        student_proxy = StudentProxy()
        students = student_proxy.search_by_age(age)
        self.update_students_list(students)

    def update_students_list(self, students):
        for row in self.students_list.get_children():
            self.students_list.delete(row)
        
        for student in students:
            self.students_list.insert("", "end", values=student)

    def clear_fields(self):
        self.name_entry.delete(0, END)
        self.age_entry.delete(0, END)
        self.grade_entry.delete(0, END)
        self.comments_entry.delete(0, END)

    def export_to_csv(self):
        students = self.students_list.get_children()
        with open('students.csv', 'w', newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Age", "Grade", "Comments"])
            for student in students:
                student_values = self.students_list.item(student)["values"]
                writer.writerow(student_values)

    def show_stats(self):
        average_age = Student.get_average_age()
        messagebox.showinfo("Stats", f"Average Age: {average_age}")

    def show_calendar(self):
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        month_calendar = calendar.month(current_year, current_month)
        messagebox.showinfo("Calendar", month_calendar)

    def show_performance_report(self):
        messagebox.showinfo("Performance Report", "This will be an AI-driven performance report.")

    def show_ai_recommendations(self):
        messagebox.showinfo("AI Recommendations", "This feature will offer AI-driven student recommendations.")

    def customize_ui(self):
        bg_color = askstring("Customize UI", "Enter a background color:")
        self.root.configure(bg=bg_color)

if __name__ == "__main__":
    root = Tk()
    app = StudentApp(root)
    root.mainloop()
