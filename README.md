# Attendance-Management-System
“A Python-based attendance management system using Tkinter and SQLite”
============================================================
          ATTENDANCE MANAGEMENT SYSTEM - USER GUIDE
============================================================

👨‍💻 Developer: Huzaifa Shoaib
📦 Project Type: Python (Tkinter + SQLite)
🗓️ Version: 1.0
📁 Works on: Windows 10 / 11

------------------------------------------------------------
📘 ABOUT THE SOFTWARE
------------------------------------------------------------
This software is designed to help teachers or institutes
manage students' attendance records easily.

You can:
✅ Add and manage attendance data in the database
✅ View daily attendance
✅ View monthly attendance summary
✅ Automatically store data using SQLite database

------------------------------------------------------------
📂 FOLDER STRUCTURE
------------------------------------------------------------
Before running the software, make sure your folder looks like this:

Attendance_Management_System/
│
├── main.py
├── dailyreport.py
├── monthlyreport.py
├── student.db
└── README.txt  (this file)

⚠️ Important:
Keep all these files in the same folder, otherwise the
software may not run correctly.

------------------------------------------------------------
⚙️ SYSTEM REQUIREMENTS
------------------------------------------------------------
🔹 Python 3.10 or newer
🔹 Tkinter (comes built-in with Python)
🔹 SQLite (already included with Python)
🔹 Windows OS recommended

------------------------------------------------------------
🚀 HOW TO RUN THE SOFTWARE
------------------------------------------------------------

1️⃣ Install Python (if not already installed)
   👉 Download from: https://www.python.org/downloads/

2️⃣ Open your folder `Attendance_Management_System`.

3️⃣ Double-click on **main.py**  
   OR open Command Prompt and type:
       python main.py

4️⃣ The Attendance Management window will appear.

------------------------------------------------------------
🧭 SOFTWARE INTERFACE GUIDE
------------------------------------------------------------

🏠 **Main Dashboard**
   - When the software opens, you will see two buttons:
        ▶ Daily Report
        ▶ Monthly Report

📅 **Daily Report Section**
   - Shows attendance records for a specific date.
   - Default date = today.
   - You can select another date to view attendance.

📊 **Monthly Report Section**
   - Displays total days recorded and present count for each student.
   - Enter month in format (YYYY-MM), e.g. `2025-10`
   - Click “Load Report” to see the summary.


------------------------------------------------------------
💾 DATABASE INFORMATION
------------------------------------------------------------
All attendance data is saved automatically inside:

   📁 student.db

Do not delete or rename this file unless you want to reset data.

The database contains all records such as:
- Student Roll Number
- Student Name
- Attendance Date
- Attendance Status

------------------------------------------------------------
🧹 DATABASE RESET / CLEANUP OPTIONS
------------------------------------------------------------

You can manage your database depending on what you want to do:

🧾 **OPTION 1: Remove all students and start fresh**
   → Delete the file `student.db` from your folder.
   → Next time you run **main.py** or the software (.exe),
     a new `student.db` file will be created automatically.

   (⚠️ This will remove all students and attendance records.)

🧾 **OPTION 2: Keep student names but clear attendance records**
   → Open `student.db` using “DB Browser for SQLite”.
   → Select the **attendance** table.
   → Clear all rows (delete records but not the table).
   → Save the database.

   (✅ This way, student names and roll numbers remain in the database,
   but all previous attendance entries will be removed.)

------------------------------------------------------------
📊 HOW TO UPDATE ATTENDANCE DATA
------------------------------------------------------------
You can manage records using any SQLite Database Browser tool.

Recommended Tool: "DB Browser for SQLite"  
   Download: https://sqlitebrowser.org/

Steps:
1️⃣ Open `student.db` in DB Browser.
2️⃣ Go to the **Browse Data** tab.
3️⃣ Select the **attendance** table.
4️⃣ You can add, edit, or delete records manually.

------------------------------------------------------------
📦 HOW TO CREATE AN EXECUTABLE FILE (.EXE)
------------------------------------------------------------

If you want to convert this project into a Windows software:

1️⃣ Install PyInstaller
   Command:
      pip install pyinstaller

2️⃣ Open Command Prompt in your project folder:
      cd path\to\Attendance_Management_System

3️⃣ Type the command:
      pyinstaller --onefile --noconsole main.py

4️⃣ After completion, open the **dist** folder.
   You will find:
      📄 main.exe

5️⃣ Double-click main.exe → your software will start without Python.

------------------------------------------------------------
⚠️ TROUBLESHOOTING GUIDE
------------------------------------------------------------

❌ Problem: Software not opening  
✅ Solution: Make sure Python is installed and all files are in one folder.

❌ Problem: Data not showing  
✅ Solution: Check if `student.db` file exists in the same directory.

❌ Problem: Window freezes or buttons not responding  
✅ Solution: Use Python 3.10 or newer version.

❌ Problem: pyinstaller command not found  
✅ Solution: Run Command Prompt as Administrator and reinstall pyinstaller.

------------------------------------------------------------
📚 EXTRA NOTES
------------------------------------------------------------
- Do not rename the database file (student.db).
- Keep all program files together in one folder.
- Backup your database regularly.
- The software is lightweight and works smoothly on any Windows PC.

------------------------------------------------------------
🎯 END OF USER MANUAL
============================================================
