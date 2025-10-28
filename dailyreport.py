# ========================= dailyreport.py =========================
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from tkcalendar import DateEntry   # ✅ For calendar date picker


def open_daily_report():
    selected_date = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))

    # -------- Fetch Attendance Data for Specific Date --------
    def fetch_daily_data(for_date):
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT s.roll_no, s.name, 
                   COALESCE((
                       SELECT a.status 
                       FROM attendance a 
                       WHERE a.roll_no = s.roll_no AND a.date = ?
                       ORDER BY a.id DESC LIMIT 1
                   ), 'Not Marked') AS status
            FROM students s
            ORDER BY s.roll_no
        """, (for_date,))
        rows = cur.fetchall()
        conn.close()
        return rows

    # -------- Export Daily Report to PDF (With Summary + Dynamic Header) --------
    def export_to_pdf(data):
        if not os.path.exists("Daily PDF Folder"):
            os.makedirs("Daily PDF Folder")

        filename = f"Daily PDF Folder/Daily_Report_{selected_date.get()}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # --- Calculate Summary Data ---
        total_students = len(data)
        total_present = sum(1 for _, _, s in data if s.lower() == "present")
        total_absent = sum(1 for _, _, s in data if s.lower() == "absent")
        total_leave = sum(1 for _, _, s in data if s.lower() == "leave")

        def draw_header(y_pos):
            """Draw table header on each new page"""
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_pos, "Roll No")
            c.drawString(150, y_pos, "Name")
            c.drawString(350, y_pos, "Status")

        # --- Title Section ---
        c.setFont("Helvetica-Bold", 18)
        c.drawString(180, height - 50, "Daily Attendance Report Of CS S3")

        # --- Date & Summary Section ---
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Date: {selected_date.get()}")
        c.drawString(50, height - 100, f"Total Students: {total_students}")
        c.drawString(250, height - 100, f"Present: {total_present}")
        c.drawString(400, height - 100, f"Absent: {total_absent}")
        c.drawString(520, height - 100, f"Leave: {total_leave}")

        # --- Table Header ---
        y = height - 130
        draw_header(y)
        y -= 20
        c.setFont("Helvetica", 11)

        # --- Table Rows ---
        for roll, name, status in data:
            c.drawString(50, y, str(roll))
            c.drawString(150, y, str(name))
            c.drawString(350, y, str(status))
            y -= 15

            # --- Page Break ---
            if y < 60:
                c.showPage()
                c.setFont("Helvetica-Bold", 18)
                c.drawString(180, height - 50, "Daily Attendance Report ")
                c.setFont("Helvetica", 12)
                c.drawString(50, height - 80, f"Date: {selected_date.get()}")
                y = height - 110
                draw_header(y)
                y -= 20
                c.setFont("Helvetica", 11)

        # --- Absent Section ---
        y -= 30
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "🚫 Absent Students:")
        y -= 20
        c.setFont("Helvetica", 11)
        absent_list = [(r, n) for (r, n, s) in data if s.lower() == "absent"]
        if absent_list:
            for roll, name in absent_list:
                c.drawString(70, y, f"{roll}  -  {name}")
                y -= 15
                if y < 60:
                    c.showPage()
                    c.setFont("Helvetica-Bold", 18)
                    c.drawString(180, height - 50, "Daily Attendance Report ")
                    y = height - 100
                    c.setFont("Helvetica", 11)
        else:
            c.drawString(70, y, "None")
            y -= 20

        # --- Leave Section ---
        y -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "🕒 On Leave:")
        y -= 20
        c.setFont("Helvetica", 11)
        leave_list = [(r, n) for (r, n, s) in data if s.lower() == "leave"]
        if leave_list:
            for roll, name in leave_list:
                c.drawString(70, y, f"{roll}  -  {name}")
                y -= 15
                if y < 60:
                    c.showPage()
                    c.setFont("Helvetica-Bold", 18)
                    c.drawString(180, height - 50, "Daily Attendance Report ")
                    y = height - 100
                    c.setFont("Helvetica", 11)
        else:
            c.drawString(70, y, "None")

        c.save()
        messagebox.showinfo("Success", f"✅ PDF saved successfully:\n{filename}")

    # -------- Main Window --------
    win = tk.Toplevel()
    win.title("Daily Attendance Report")
    win.geometry("950x750")
    win.configure(bg="#eaf4fc")

    # -------- Heading Section --------
    header_frame = tk.Frame(win, bg="#2563EB", height=80)
    header_frame.pack(fill=tk.X)

    heading_label = tk.Label(
        header_frame,
        text="📅 Daily Attendance Report",
        font=("Arial Rounded MT Bold", 22),
        bg="#2563EB",
        fg="white"
    )
    heading_label.pack(pady=10, side=tk.LEFT, padx=20)

    # -------- Summary Section (Below Heading) --------
    summary_frame = tk.Frame(win, bg="#DBEAFE", height=100)
    summary_frame.pack(fill=tk.X, padx=20, pady=10)

    total_students_lbl = tk.Label(summary_frame, text="Total Students: 0", font=("Arial", 12, "bold"), bg="#DBEAFE", fg="#1E3A8A")
    total_present_lbl = tk.Label(summary_frame, text="Present: 0", font=("Arial", 12, "bold"), bg="#DBEAFE", fg="#047857")
    total_absent_lbl = tk.Label(summary_frame, text="Absent: 0", font=("Arial", 12, "bold"), bg="#DBEAFE", fg="#B91C1C")
    total_leave_lbl = tk.Label(summary_frame, text="Leave: 0", font=("Arial", 12, "bold"), bg="#DBEAFE", fg="#92400E")

    total_students_lbl.grid(row=0, column=0, padx=40, pady=10)
    total_present_lbl.grid(row=0, column=1, padx=40, pady=10)
    total_absent_lbl.grid(row=0, column=2, padx=40, pady=10)
    total_leave_lbl.grid(row=0, column=3, padx=40, pady=10)

    # -------- Absent & Leave Lists Section --------
    lists_frame = tk.Frame(win, bg="#eaf4fc")
    lists_frame.pack(fill=tk.X, padx=25, pady=5)

    absent_frame = tk.LabelFrame(lists_frame, text="🚫 Absent Students", bg="#FEE2E2", fg="#B91C1C",
                                 font=("Arial", 12, "bold"), padx=10, pady=5, width=400, height=120)
    absent_frame.pack(side=tk.LEFT, padx=15, pady=5, fill=tk.BOTH, expand=True)

    absent_box = tk.Text(absent_frame, width=40, height=5, font=("Arial", 10), bg="#FEF2F2", fg="black")
    absent_box.pack(fill=tk.BOTH, expand=True)

    leave_frame = tk.LabelFrame(lists_frame, text="🕒 On Leave", bg="#FEF3C7", fg="#92400E",
                                font=("Arial", 12, "bold"), padx=10, pady=5, width=400, height=120)
    leave_frame.pack(side=tk.RIGHT, padx=15, pady=5, fill=tk.BOTH, expand=True)

    leave_box = tk.Text(leave_frame, width=40, height=5, font=("Arial", 10), bg="#FFFBEB", fg="black")
    leave_box.pack(fill=tk.BOTH, expand=True)

    # 🟢 Add Date Picker on right side of heading
    date_picker = DateEntry(
        header_frame,
        width=12,
        background="#2563EB",
        foreground="white",
        borderwidth=2,
        date_pattern='yyyy-mm-dd',
        font=("Arial", 11)
    )
    date_picker.place(x=700, y=25)

    select_date_btn = tk.Button(
        header_frame,
        text="🔍 Show Date",
        bg="#10B981",
        fg="white",
        font=("Arial", 10, "bold"),
        relief=tk.FLAT,
        cursor="hand2",
        command=lambda: load_data(date_picker.get_date().strftime("%Y-%m-%d"))
    )
    select_date_btn.place(x=820, y=25)

    # -------- Treeview Styling --------
    style = ttk.Style()
    style.configure("Treeview",
                    background="#ffffff",
                    foreground="black",
                    rowheight=30,
                    fieldbackground="#ffffff",
                    font=("Arial", 11))
    style.configure("Treeview.Heading",
                    font=("Arial", 12, "bold"),
                    background="#2563EB",
                    foreground="black")
    style.map('Treeview', background=[('selected', '#93C5FD')])

    # -------- Table Section --------
    columns = ("Roll No", "Name", "Status")
    tree = ttk.Treeview(win, columns=columns, show="headings", height=11)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=200 if col != "Name" else 350)
    tree.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)

    # -------- Load Data Function --------
    def load_data(for_date=None):
        if not for_date:
            for_date = selected_date.get()
        data = fetch_daily_data(for_date)
        tree.delete(*tree.get_children())
        for row in data:
            tree.insert("", tk.END, values=row)
        selected_date.set(for_date)

        # --- Update Summary Counts ---
        total_students = len(data)
        total_present = sum(1 for _, _, s in data if s.lower() == "present")
        total_absent = sum(1 for _, _, s in data if s.lower() == "absent")
        total_leave = sum(1 for _, _, s in data if s.lower() == "leave")

        total_students_lbl.config(text=f"Total Students: {total_students}")
        total_present_lbl.config(text=f"Present: {total_present}")
        total_absent_lbl.config(text=f"Absent: {total_absent}")
        total_leave_lbl.config(text=f"Leave: {total_leave}")

        # --- Update Absent & Leave Lists ---
        absent_box.delete("1.0", tk.END)
        leave_box.delete("1.0", tk.END)

        for roll, name, status in data:
            if status.lower() == "absent":
                absent_box.insert(tk.END, f"{roll}  -  {name}\n")
            elif status.lower() == "leave":
                leave_box.insert(tk.END, f"{roll}  -  {name}\n")

        if total_absent == 0:
            absent_box.insert(tk.END, "None\n")
        if total_leave == 0:
            leave_box.insert(tk.END, "None\n")

        return data

    # -------- Buttons Section --------
    btn_frame = tk.Frame(win, bg="#eaf4fc")
    btn_frame.pack(pady=15)

    tk.Button(
        btn_frame, text="📄 Export to PDF",
        command=lambda: export_to_pdf(load_data()),
        bg="#10B981", fg="white",
        font=('Arial', 11, 'bold'),
        width=18, relief=tk.FLAT, cursor="hand2"
    ).grid(row=0, column=0, padx=15)

    tk.Button(
        btn_frame, text="🔄 Refresh",
        command=lambda: load_data(selected_date.get()),
        bg="#F59E0B", fg="white",
        font=('Arial', 11, 'bold'),
        width=12, relief=tk.FLAT, cursor="hand2"
    ).grid(row=0, column=1, padx=10)

    # Load today's data by default
    load_data(selected_date.get())
