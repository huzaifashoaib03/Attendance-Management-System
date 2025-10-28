# ================= Main Attendance Management System =================
# main.py

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import os

# Import report modules (make sure these modules exist)
from dailyreport import open_daily_report
from monthlyreport import open_monthly_report

# ----------- Database Setup -----------
def setup_database():
    """
    Create tables if not exist and ensure a unique index on (roll_no, date).
    Safely removes existing duplicate attendance rows (keeps the earliest id).
    """
    conn = sqlite3.connect("student.db", timeout=10)
    cur = conn.cursor()

    # Create students table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            roll_no INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    # Create attendance table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no INTEGER,
            status TEXT,
            date TEXT,
            FOREIGN KEY(roll_no) REFERENCES students(roll_no)
        )
    """)

    conn.commit()

    # Remove duplicates (keep the smallest id for each roll_no+date)
    cur.execute("""
        DELETE FROM attendance
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM attendance
            GROUP BY roll_no, date
        )
    """)
    conn.commit()

    # Create unique index to prevent future duplicates
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_attendance_unique
        ON attendance (roll_no, date)
    """)
    conn.commit()

    conn.close()


# ----------- Main Class -----------
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Student Attendance Management System")
        self.root.geometry("1000x680")
        self.root.configure(bg="#E5E7EB")

        # Heading
        tk.Label(
            root,
            text="📚 Student Attendance Management System",
            font=("Arial", 22, "bold"),
            bg="#1E40AF",
            fg="white",
            pady=15
        ).pack(fill=tk.X)

        # Main Frame
        main_frame = tk.Frame(root, bg="#E5E7EB")
        main_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # --- Student Management Frame ---
        student_frame = tk.LabelFrame(main_frame, text="👩‍🎓 Manage Students", font=("Arial", 14, "bold"),
                                      bg="#E5E7EB", fg="#1E3A8A", padx=15, pady=10)
        student_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(student_frame, text="Roll No:", font=("Arial", 12), bg="#E5E7EB").grid(row=0, column=0, padx=5, pady=5)
        self.roll_entry = tk.Entry(student_frame, font=("Arial", 12), width=10)
        self.roll_entry.grid(row=0, column=1, padx=5)

        tk.Label(student_frame, text="Name:", font=("Arial", 12), bg="#E5E7EB").grid(row=0, column=2, padx=5, pady=5)
        self.name_entry = tk.Entry(student_frame, font=("Arial", 12), width=25)
        self.name_entry.grid(row=0, column=3, padx=5)

        # Date field (auto-filled with today's date)
        tk.Label(student_frame, text="Date:", font=("Arial", 12), bg="#E5E7EB").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = tk.Entry(student_frame, font=("Arial", 12), width=12)
        self.date_entry.grid(row=0, column=5, padx=5)
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today_str)

        tk.Button(student_frame, text="Add Student", bg="#10B981", fg="white", font=("Arial", 11, "bold"),
                  command=self.add_student, width=14).grid(row=1, column=0, padx=10, pady=8)
        tk.Button(student_frame, text="Edit Student", bg="#F59E0B", fg="white", font=("Arial", 11, "bold"),
                  command=self.edit_student, width=14).grid(row=1, column=1, padx=10, pady=8)
        tk.Button(student_frame, text="Delete Student", bg="#EF4444", fg="white", font=("Arial", 11, "bold"),
                  command=self.delete_student, width=14).grid(row=1, column=2, padx=10, pady=8)

        # --- Attendance Table ---
        table_frame = tk.LabelFrame(main_frame, text="📅 Mark Attendance", font=("Arial", 14, "bold"),
                                    bg="#E5E7EB", fg="#1E3A8A", padx=15, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("Roll No", "Name", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # --- Status Buttons ---
        status_frame = tk.Frame(main_frame, bg="#E5E7EB")
        status_frame.pack(pady=10)
        tk.Button(status_frame, text="✅ Present", command=lambda: self.mark_attendance("Present"),
                  bg="#10B981", fg="white", font=("Arial", 11, "bold"), width=12).grid(row=0, column=0, padx=10)
        tk.Button(status_frame, text="❌ Absent", command=lambda: self.mark_attendance("Absent"),
                  bg="#EF4444", fg="white", font=("Arial", 11, "bold"), width=12).grid(row=0, column=1, padx=10)
        tk.Button(status_frame, text="🕒 Leave", command=lambda: self.mark_attendance("Leave"),
                  bg="#F59E0B", fg="white", font=("Arial", 11, "bold"), width=12).grid(row=0, column=2, padx=10)
        tk.Button(status_frame, text="✅ Mark All Present", command=self.mark_all_present,
                  bg="#059669", fg="white", font=("Arial", 11, "bold"), width=16).grid(row=0, column=3, padx=10)
        tk.Button(status_frame, text="🔄 Refresh", command=self.load_students,
                  bg="#3B82F6", fg="white", font=("Arial", 11, "bold"), width=12).grid(row=0, column=4, padx=10)

        # --- Report Buttons ---
        report_frame = tk.Frame(main_frame, bg="#E5E7EB")
        report_frame.pack(pady=20)

        def make_btn(text, command, color):
            return tk.Button(
                report_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Arial", 12, "bold"),
                activebackground="#1E293B",
                activeforeground="white",
                relief="raised",
                bd=3,
                width=20,
                height=2,
                cursor="hand2"
            )

        make_btn("📅 Open Daily Report", open_daily_report, "#3B82F6").pack(pady=8)
        make_btn("📆 Open Monthly Report", open_monthly_report, "#10B981").pack(pady=8)

        # Load students and today's status
        self.load_students()

    # -------- Add Student --------
    def add_student(self):
        roll = self.roll_entry.get().strip()
        name = self.name_entry.get().strip()

        if not roll or not name:
            messagebox.showerror("Error", "Please enter both Roll No and Name!")
            return

        conn = sqlite3.connect("student.db", timeout=5)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO students (roll_no, name) VALUES (?, ?)", (int(roll), name))
            conn.commit()
            messagebox.showinfo("Success", "Student added successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Roll No already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()
        self.load_students()

    # -------- Edit Student --------
    def edit_student(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Student", "Please select a student to edit.")
            return

        old_roll, old_name, _ = self.tree.item(selected, "values")

        new_roll = self.roll_entry.get().strip()
        new_name = self.name_entry.get().strip()

        if not new_roll or not new_name:
            messagebox.showerror("Error", "Please enter new Roll No and Name!")
            return

        conn = sqlite3.connect("student.db", timeout=5)
        cur = conn.cursor()
        try:
            cur.execute("UPDATE students SET roll_no=?, name=? WHERE roll_no=?", (int(new_roll), new_name, int(old_roll)))
            conn.commit()
            messagebox.showinfo("Updated", "Student record updated successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Roll No already exists, please choose another.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()
        self.load_students()

    # -------- Delete Student --------
    def delete_student(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Student", "Please select a student to delete.")
            return
        values = self.tree.item(selected, "values")
        roll_no = values[0]

        conn = sqlite3.connect("student.db", timeout=5)
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM students WHERE roll_no=?", (int(roll_no),))
            conn.commit()
            messagebox.showinfo("Deleted", f"Student Roll No {roll_no} deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()
        self.load_students()

    # -------- Load Students from Database (shows status for selected date) --------
    def load_students(self):
        # Determine date from date_entry (fallback to today)
        try:
            date = self.date_entry.get().strip()
            # validate basic format YYYY-MM-DD, otherwise fallback
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except Exception:
            date = datetime.date.today().strftime("%Y-%m-%d")
            # keep entry updated
            try:
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, date)
            except Exception:
                pass

        self.tree.delete(*self.tree.get_children())
        conn = sqlite3.connect("student.db", timeout=5)
        cur = conn.cursor()
        try:
            # left join to get today's attendance if any
            cur.execute("""
                SELECT s.roll_no, s.name, IFNULL(a.status, '') as status
                FROM students s
                LEFT JOIN attendance a
                  ON s.roll_no = a.roll_no AND a.date = ?
                ORDER BY s.roll_no
            """, (date,))
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=(row[0], row[1], row[2]))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load students: {e}")
        finally:
            conn.close()

    # -------- Mark Individual Attendance (insert or update) --------
    def mark_attendance(self, status):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Student", "Please select a student to mark attendance.")
            return
        roll_no, name, _ = self.tree.item(selected, "values")

        # Use selected date from UI (or today's date)
        try:
            date = self.date_entry.get().strip()
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except Exception:
            date = datetime.date.today().strftime("%Y-%m-%d")
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, date)

        conn = sqlite3.connect("student.db", timeout=5)
        cur = conn.cursor()
        try:
            # Check if attendance exists for this roll & date
            cur.execute("SELECT id, status FROM attendance WHERE roll_no = ? AND date = ?", (int(roll_no), date))
            existing = cur.fetchone()
            if existing:
                # Update the existing record
                cur.execute("UPDATE attendance SET status = ? WHERE id = ?", (status, existing[0]))
                conn.commit()
                messagebox.showinfo("Updated", f"Attendance updated to '{status}' for {name}.")
            else:
                # Insert new attendance record
                try:
                    cur.execute("INSERT INTO attendance (roll_no, status, date) VALUES (?, ?, ?)", (int(roll_no), status, date))
                    conn.commit()
                    messagebox.showinfo("Success", f"Attendance marked as {status} for {name}.")
                except sqlite3.IntegrityError:
                    # If unique constraint triggered for some reason, update instead
                    cur.execute("UPDATE attendance SET status = ? WHERE roll_no = ? AND date = ?", (status, int(roll_no), date))
                    conn.commit()
                    messagebox.showinfo("Updated", f"Attendance updated to '{status}' for {name}.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while marking attendance:\n{e}")
        finally:
            conn.close()

        # update UI
        self.load_students()

    # -------- Mark All Students Present (insert or update) --------
    def mark_all_present(self):
        # Use selected date from UI (or today's date)
        try:
            date = self.date_entry.get().strip()
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except Exception:
            date = datetime.date.today().strftime("%Y-%m-%d")
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, date)

        # Optional confirmation
        if not messagebox.askyesno("Confirm", f"Mark ALL students as Present for {date}?"):
            return

        conn = sqlite3.connect("student.db", timeout=10)
        cur = conn.cursor()
        try:
            cur.execute("SELECT roll_no FROM students")
            students = cur.fetchall()

            count_inserted = 0
            count_updated = 0

            for (roll_no,) in students:
                # Check if attendance exists for this student & date
                cur.execute("SELECT id, status FROM attendance WHERE roll_no = ? AND date = ?", (int(roll_no), date))
                existing = cur.fetchone()

                if existing:
                    if existing[1] != "Present":
                        cur.execute("UPDATE attendance SET status = ? WHERE id = ?", ("Present", existing[0]))
                        count_updated += 1
                else:
                    try:
                        cur.execute("INSERT INTO attendance (roll_no, status, date) VALUES (?, ?, ?)", (int(roll_no), "Present", date))
                        count_inserted += 1
                    except sqlite3.IntegrityError:
                        # If race condition or other, update instead
                        cur.execute("UPDATE attendance SET status = ? WHERE roll_no = ? AND date = ?", ("Present", int(roll_no), date))
                        count_updated += 1

            conn.commit()
            messagebox.showinfo("Success", f"Marked {count_inserted} new and updated {count_updated} students as Present for {date}!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while marking all present:\n{e}")
        finally:
            conn.close()

        # Refresh UI
        self.load_students()


# ----------- Run Application -----------
if __name__ == "__main__":
    # Ensure DB and indexes are set up
    setup_database()

    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
