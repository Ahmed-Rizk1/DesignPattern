import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
import pandas as pd
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Singleton Pattern: Database
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
                rating INTEGER,
                comments TEXT
            )
        """)
        self.connection.commit()

    def get_connection(self):
        return self.connection


# Model
class Student:
    def __init__(self, name, age, grade, rating=None, comments=None):
        self.name = name
        self.age = age
        self.grade = grade
        self.rating = rating
        self.comments = comments

    def save(self):
        db = Database().get_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO students (name, age, grade, rating, comments) VALUES (?, ?, ?, ?, ?)", 
                       (self.name, self.age, self.grade, self.rating, self.comments))
        db.commit()

    @staticmethod
    def get_all():
        db = Database().get_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM students")
        return cursor.fetchall()

    @staticmethod
    def delete(student_id):
        db = Database().get_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        db.commit()

    @staticmethod
    def update(student_id, name, age, grade, rating, comments):
        db = Database().get_connection()
        cursor = db.cursor()
        cursor.execute("UPDATE students SET name = ?, age = ?, grade = ?, rating = ?, comments = ? WHERE id = ?", 
                       (name, age, grade, rating, comments, student_id))
        db.commit()

    @staticmethod
    def search_by_name(name):
        db = Database().get_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM students WHERE name LIKE ?", ('%' + name + '%',))
        return cursor.fetchall()

    @staticmethod
    def get_average_age():
        db = Database().get_connection()
        cursor = db.cursor()
        cursor.execute("SELECT AVG(age) FROM students")
        return cursor.fetchone()[0]


# View & Controller
class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("800x600")
        
        # UI Elements
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

        self.rating_label = ttk.Label(root, text="Rating (1-5):")
        self.rating_label.grid(row=3, column=0, padx=10, pady=5)
        self.rating_entry = ttk.Entry(root)
        self.rating_entry.grid(row=3, column=1, padx=10, pady=5)

        self.comments_label = ttk.Label(root, text="Comments:")
        self.comments_label.grid(row=4, column=0, padx=10, pady=5)
        self.comments_entry = ttk.Entry(root)
        self.comments_entry.grid(row=4, column=1, padx=10, pady=5)

        self.add_button = ttk.Button(root, text="Add Student", command=self.add_student)
        self.add_button.grid(row=5, column=0, padx=10, pady=10)

        self.update_button = ttk.Button(root, text="Update Student", command=self.update_student)
        self.update_button.grid(row=5, column=1, padx=10, pady=10)

        self.search_label = ttk.Label(root, text="Search by Name:")
        self.search_label.grid(row=6, column=0, padx=10, pady=5)
        self.search_entry = ttk.Entry(root)
        self.search_entry.grid(row=6, column=1, padx=10, pady=5)
        self.search_button = ttk.Button(root, text="Search", command=self.search_student)
        self.search_button.grid(row=6, column=2, padx=10, pady=5)

        self.export_button = ttk.Button(root, text="Export to CSV", command=self.export_to_csv)
        self.export_button.grid(row=7, column=0, padx=10, pady=10)

        self.stats_button = ttk.Button(root, text="Show Stats", command=self.show_stats)
        self.stats_button.grid(row=7, column=1, padx=10, pady=10)

        self.students_list = ttk.Treeview(root, columns=("ID", "Name", "Age", "Grade", "Rating", "Comments"), show='headings')
        self.students_list.grid(row=8, column=0, columnspan=3, padx=10, pady=10)
        self.students_list.heading("ID", text="ID")
        self.students_list.heading("Name", text="Name")
        self.students_list.heading("Age", text="Age")
        self.students_list.heading("Grade", text="Grade")
        self.students_list.heading("Rating", text="Rating")
        self.students_list.heading("Comments", text="Comments")

        self.delete_button = ttk.Button(root, text="Delete Student", command=self.delete_student)
        self.delete_button.grid(row=9, column=0, columnspan=3, pady=10)

        self.load_students()

    def add_student(self):
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        grade = self.grade_entry.get().strip()
        rating = self.rating_entry.get().strip()
        comments = self.comments_entry.get().strip()

        if not name or not age or not grade or not rating:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            age = int(age)
            rating = int(rating)
            if rating < 1 or rating > 5:
                messagebox.showerror("Error", "Rating must be between 1 and 5!")
                return
        except ValueError:
            messagebox.showerror("Error", "Age and Rating must be numbers!")
            return

        student = Student(name, age, grade, rating, comments)
        student.save()
        messagebox.showinfo("Success", "Student added successfully!")
        self.clear_entries()
        self.load_students()

    def update_student(self):
        selected_item = self.students_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a student to update!")
            return

        student_id = self.students_list.item(selected_item[0])["values"][0]
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        grade = self.grade_entry.get().strip()
        rating = self.rating_entry.get().strip()
        comments = self.comments_entry.get().strip()

        if not name or not age or not grade or not rating:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            age = int(age)
            rating = int(rating)
            if rating < 1 or rating > 5:
                messagebox.showerror("Error", "Rating must be between 1 and 5!")
                return
        except ValueError:
            messagebox.showerror("Error", "Age and Rating must be numbers!")
            return

        Student.update(student_id, name, age, grade, rating, comments)
        messagebox.showinfo("Success", "Student updated successfully!")
        self.clear_entries()
        self.load_students()

    def delete_student(self):
        selected_item = self.students_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a student to delete!")
            return

        student_id = self.students_list.item(selected_item[0])["values"][0]
        Student.delete(student_id)
        messagebox.showinfo("Success", "Student deleted successfully!")
        self.load_students()

    def search_student(self):
        name = self.search_entry.get().strip()
        results = Student.search_by_name(name)
        self.populate_students(results)

    def export_to_csv(self):
        students = Student.get_all()
        with open("students.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Age", "Grade", "Rating", "Comments"])
            writer.writerows(students)
        messagebox.showinfo("Success", "Data exported to CSV successfully!")

    def show_stats(self):
        avg_age = Student.get_average_age()
        messagebox.showinfo("Statistics", f"Average Age of Students: {avg_age:.2f}")

        # Plot statistics (example: Rating distribution)
        ratings = [student[4] for student in Student.get_all()]
        plt.hist(ratings, bins=5, range=(1, 6), edgecolor='black')
        plt.xlabel('Rating')
        plt.ylabel('Frequency')
        plt.title('Rating Distribution')
        plt.show()

    def load_students(self):
        students = Student.get_all()
        self.populate_students(students)

    def populate_students(self, students):
        for row in self.students_list.get_children():
            self.students_list.delete(row)
        for student in students:
            self.students_list.insert("", "end", values=student)

    def clear_entries(self):
        self.name_entry.delete(0, END)
        self.age_entry.delete(0, END)
        self.grade_entry.delete(0, END)
        self.rating_entry.delete(0, END)
        self.comments_entry.delete(0, END)


if __name__ == "__main__":
    root = Tk()
    app = StudentApp(root)
    root.mainloop()
