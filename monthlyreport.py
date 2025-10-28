# ========================= monthlyreport.py =========================
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import calendar

def open_monthly_report():
    # -------- Helper: fetch aggregated monthly data for all students --------
    def fetch_monthly_data(month, year):
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        mm = f"{month:02d}"
        yyyy = str(year)
        cur.execute("""
            SELECT s.roll_no, s.name,
                   SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as presents,
                   SUM(CASE WHEN a.status='Absent' THEN 1 ELSE 0 END) as absents,
                   SUM(CASE WHEN a.status='Leave' THEN 1 ELSE 0 END) as leaves,
                   COUNT(a.status) as total_days
            FROM students s
            LEFT JOIN attendance a
              ON s.roll_no = a.roll_no
              AND strftime('%m', a.date)=? AND strftime('%Y', a.date)=?
            GROUP BY s.roll_no, s.name
            ORDER BY s.roll_no
        """, (mm, yyyy))
        rows = cur.fetchall()
        conn.close()
        return rows

    # -------- Helper: fetch per-student day-wise records for that month --------
    def fetch_student_records(roll_no, month, year):
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        mm = f"{month:02d}"
        yyyy = str(year)
        cur.execute("""
            SELECT date, status
            FROM attendance
            WHERE roll_no = ? AND strftime('%m', date)=? AND strftime('%Y', date)=?
            ORDER BY date
        """, (roll_no, mm, yyyy))
        rows = cur.fetchall()
        conn.close()
        return rows

    # -------- Export full-month aggregated PDF (No Leave Column + Fixed Layout) --------
    def export_month_pdf(month, year, data):
        if not data:
            messagebox.showwarning("No Data", "No data to export for the selected month.")
            return

        if not os.path.exists("Monthly PDF Folder"):
            os.makedirs("Monthly PDF Folder")
        month_name = calendar.month_name[month]
        filename = f"Monthly PDF Folder/Monthly_Report_{month_name}_{year}.pdf"

        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        def draw_header(y_start):
            """Draw table header on each new page"""
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, y_start, "Roll No")
            c.drawString(110, y_start, "Name")
            c.drawString(310, y_start, "Present")
            c.drawString(380, y_start, "Absent")
            c.drawString(460, y_start, "Total")
            c.drawString(530, y_start, "Percent")

        # Title
        c.setFont("Helvetica-Bold", 18)
        c.drawString(150, height - 50, "Monthly Attendance Report")

        # Month name
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Month: {month_name} {year}")

        # First header
        y = height - 110
        draw_header(y)
        y -= 16
        c.setFont("Helvetica", 10)

        for roll, name, presents, absents, leaves, total in data:
            percent = ((presents + leaves) / total * 100) if total else 0
            c.drawString(40, y, str(roll))
            c.drawString(110, y, str(name)[:28])
            c.drawString(310, y, str(presents))
            c.drawString(380, y, str(absents))
            c.drawString(460, y, str(total))
            c.drawString(530, y, f"{percent:.1f}%")

            y -= 15  # spacing optimized

            # --- Page break condition ---
            if y < 60:
                c.showPage()
                c.setFont("Helvetica-Bold", 18)
                c.drawString(150, height - 50, "Monthly Attendance Report ")
                c.setFont("Helvetica", 12)
                c.drawString(50, height - 80, f"Month: {month_name} {year}")
                y = height - 110
                draw_header(y)
                y -= 16
                c.setFont("Helvetica", 10)

        c.save()
        messagebox.showinfo("Success", f"✅ Monthly PDF saved successfully:\n{filename}")


    # -------- Export individual student's month PDF (detailed by date) --------
    def export_student_pdf(roll_no, name, month, year, records):
        if not records:
            messagebox.showwarning("No Data", f"No attendance records found for {name} in {calendar.month_name[month]} {year}.")
            return

        if not os.path.exists("Monthly PDF Folder"):
            os.makedirs("Monthly PDF Folder")
        month_name = calendar.month_name[month]
        filename = f"Monthly PDF Folder/Student_{roll_no}_{month_name}_{year}.pdf"

        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Title and details
        c.setFont("Helvetica-Bold", 16)
        c.drawString(140, height - 50, f"Monthly Attendance - {name} ({roll_no})")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Month: {month_name} {year}")

        # Table header
        y = height - 120
        c.setFont("Helvetica-Bold", 11)
        c.drawString(80, y, "Date")
        c.drawString(200, y, "Status")
        y -= 18
        c.setFont("Helvetica", 11)

        for date, status in records:
            c.drawString(80, y, str(date))
            c.drawString(200, y, str(status))
            y -= 16
            if y < 80:
                c.showPage()
                y = height - 80
                c.setFont("Helvetica", 11)

        c.save()
        messagebox.showinfo("Success", f"✅ Student PDF saved:\n{filename}")

    # -------- Build Window --------
    win = tk.Toplevel()
    win.title("Monthly Attendance Report")
    win.geometry("980x720")
    win.configure(bg="#f3efff")

    # Header
    header = tk.Frame(win, bg="#6D28D9", height=90)
    header.pack(fill="x")
    tk.Label(header, text="🗓️ Monthly Attendance Report", font=("Segoe UI", 20, "bold"),
             bg="#6D28D9", fg="white").pack(pady=12)
    tk.Label(header, text=f"Generate aggregated or per-student monthly reports", font=("Segoe UI", 10),
             bg="#6D28D9", fg="#EDE9FE").pack()

    # Selection frame (month, year & search)
    control = tk.Frame(win, bg="#f3efff")
    control.pack(fill="x", pady=12, padx=18)

    tk.Label(control, text="Month:", bg="#f3efff", font=("Segoe UI", 11)).grid(row=0, column=0, padx=6, sticky="w")
    month_var = tk.IntVar(value=datetime.date.today().month)
    month_combo = ttk.Combobox(control, textvariable=month_var, values=list(range(1,13)), width=6, state="readonly")
    month_combo.grid(row=0, column=1, padx=6)

    tk.Label(control, text="Year:", bg="#f3efff", font=("Segoe UI", 11)).grid(row=0, column=2, padx=6, sticky="w")
    year_var = tk.IntVar(value=datetime.date.today().year)
    year_range = list(range(datetime.date.today().year - 3, datetime.date.today().year + 3))
    year_combo = ttk.Combobox(control, textvariable=year_var, values=year_range, width=8, state="readonly")
    year_combo.grid(row=0, column=3, padx=6)

    # Search bar for individual student
    tk.Label(control, text="Search (Roll or Name):", bg="#f3efff", font=("Segoe UI", 11)).grid(row=0, column=4, padx=(18,6), sticky="w")
    search_entry = tk.Entry(control, font=("Segoe UI", 11), width=25)
    search_entry.grid(row=0, column=5, padx=6)

    # Buttons for actions
    btn_frame = tk.Frame(win, bg="#f3efff")
    btn_frame.pack(fill="x", padx=18, pady=(0,10))

    show_btn = tk.Button(btn_frame, text="🔍 Show Report", bg="#3B82F6", fg="white",
                         font=("Segoe UI", 11, "bold"), width=14, relief=tk.FLAT)
    show_btn.grid(row=0, column=0, padx=8)

    export_all_btn = tk.Button(btn_frame, text="📄 Export Full Month PDF", bg="#10B981", fg="white",
                               font=("Segoe UI", 11, "bold"), width=18, relief=tk.FLAT)
    export_all_btn.grid(row=0, column=1, padx=8)

    export_person_btn = tk.Button(btn_frame, text="📄 Export Student PDF", bg="#8B5CF6", fg="white",
                                  font=("Segoe UI", 11, "bold"), width=18, relief=tk.FLAT)
    export_person_btn.grid(row=0, column=2, padx=8)

    refresh_btn = tk.Button(btn_frame, text="🔄 Refresh", bg="#F59E0B", fg="white",
                            font=("Segoe UI", 11, "bold"), width=12, relief=tk.FLAT,
                            command=lambda: load_data())
    refresh_btn.grid(row=0, column=3, padx=8)

    # Treeview style and table
    style = ttk.Style()
    style.configure("Treeview", rowheight=28, font=("Segoe UI", 11))
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

    columns = ("Roll No", "Name", "Present", "Absent", "Leave", "Total", "Percent")
    tree_frame = tk.Frame(win, bg="#f3efff")
    tree_frame.pack(fill="both", expand=True, padx=18, pady=10)

    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=16)
    for col in columns:
        tree.heading(col, text=col)
        if col == "Name":
            tree.column(col, width=300, anchor="center")
        elif col == "Percent":
            tree.column(col, width=90, anchor="center")
        else:
            tree.column(col, width=110, anchor="center")
    tree.pack(fill="both", expand=True, side="left")

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # -------- Load / Show data into table --------
    def load_data():
        try:
            month = int(month_var.get())
            year = int(year_var.get())
        except Exception:
            messagebox.showerror("Invalid Month/Year", "Please select a valid month and year.")
            return

        rows = fetch_monthly_data(month, year)
        tree.delete(*tree.get_children())
        for roll, name, presents, absents, leaves, total in rows:
            percent = ((presents + leaves) / total * 100) if total else 0.0
            tree.insert("", tk.END, values=(roll, name, presents, absents, leaves, total, f"{percent:.1f}%"))
        return rows

    # -------- Search student and export individual's monthly PDF --------
    def handle_export_individual():
        query = search_entry.get().strip()
        if not query:
            messagebox.showwarning("Input Required", "Please enter Roll No or Name to search.")
            return
        try:
            month = int(month_var.get())
            year = int(year_var.get())
        except Exception:
            messagebox.showerror("Invalid Month/Year", "Please select a valid month and year.")
            return

        # Determine if numeric (roll) or name
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        if query.isdigit():
            cur.execute("SELECT roll_no, name FROM students WHERE roll_no = ?", (int(query),))
        else:
            # partial match for name (case-insensitive)
            cur.execute("SELECT roll_no, name FROM students WHERE LOWER(name) LIKE ?", (f"%{query.lower()}%",))
        matches = cur.fetchall()
        conn.close()

        if not matches:
            messagebox.showinfo("Not Found", f"No student found for '{query}'.")
            return
        if len(matches) > 1:
            # show simple list of matches and ask to use roll number instead
            list_names = "\n".join([f"{r} - {n}" for r, n in matches])
            messagebox.showinfo("Multiple Matches", f"Multiple students found:\n\n{list_names}\n\nPlease enter the exact Roll No to export a single student's PDF.")
            return

        roll_no, name = matches[0]
        records = fetch_student_records(roll_no, month, year)
        export_student_pdf(roll_no, name, month, year, records)

    # -------- Export aggregated month (button handler) --------
    def handle_export_all():
        try:
            month = int(month_var.get())
            year = int(year_var.get())
        except Exception:
            messagebox.showerror("Invalid Month/Year", "Please select a valid month and year.")
            return
        data = fetch_monthly_data(month, year)
        export_month_pdf(month, year, data)

    # wire buttons
    show_btn.config(command=load_data)
    export_all_btn.config(command=handle_export_all)
    export_person_btn.config(command=handle_export_individual)

    # initial load
    load_data()

    # footer
    tk.Label(win, text="© Huzaifa Shoaib | Attendance System", bg="#f3efff", fg="#6B7280",
             font=("Segoe UI", 10, "italic")).pack(side="bottom", pady=6)

# Note: This module expects student.db to exist in same folder and tables to follow earlier structure.
# Use from main.py -> open_monthly_report() to open this window.
