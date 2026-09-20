ExamApp/
├── main.py
├── database.py
├── admin/
│   ├── __init__.py
│   ├── admin_login.py
│   ├── admin_dashboard.py
│   ├── manage_students.py
│   ├── manage_questions.py
│   └── view_results.py
├── student/
│   ├── __init__.py
│   ├── student_login.py
│   ├── exam_window.py
│   └── result_window.py
├── assets/
│   ├── exam.db
│   └── violations/       (webcam snapshots)
└── requirements.txt
  import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'exam.db')

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT UNIQUE,
        name TEXT,
        password TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,
        correct_option TEXT,
        marks INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        duration_minutes INTEGER,
        total_questions INTEGER,
        total_marks INTEGER,
        is_active INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        exam_id INTEGER,
        score INTEGER,
        total INTEGER,
        answers TEXT,
        violations INTEGER DEFAULT 0,
        submitted_at TEXT
    )''')

    # Default admin
    c.execute("INSERT OR IGNORE INTO admin (id, username, password) VALUES (1, 'admin', 'admin123')")

    # Default exam
    c.execute("SELECT COUNT(*) FROM exams")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO exams (title, duration_minutes, total_questions, total_marks) VALUES ('General Test', 60, 50, 50)")

    conn.commit()
    conn.close()
  import sys
from PyQt6.QtWidgets import QApplication
from database import init_db
from admin.admin_login import AdminLogin

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AdminLogin()
    window.show()
    sys.exit(app.exec())
  from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt
from database import get_conn
from admin.admin_dashboard import AdminDashboard
from student.student_login import StudentLogin

class AdminLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exam Software - Login")
        self.setFixedSize(420, 380)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(12)

        title = QLabel("🎓 Exam Software")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        sub = QLabel("Admin Login")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-bottom: 15px;")
        layout.addWidget(sub)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        login_btn = QPushButton("Login as Admin")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        student_btn = QPushButton("Login as Student →")
        student_btn.setStyleSheet("background-color: #27ae60; color: white;")
        student_btn.clicked.connect(self.open_student)
        layout.addWidget(student_btn)

        self.setLayout(layout)
        self.apply_style()

    def apply_style(self):
        self.setStyleSheet("""
            QWidget { background-color: #ecf0f1; font-size: 14px; }
            QLineEdit { padding: 10px; border: 1px solid #bdc3c7; border-radius: 6px; background: white; }
            QPushButton { padding: 10px; background-color: #2980b9; color: white; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #3498db; }
        """)

    def login(self):
        u = self.username.text().strip()
        p = self.password.text().strip()
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (u, p))
        row = c.fetchone()
        conn.close()
        if row:
            self.dash = AdminDashboard()
            self.dash.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials!")

    def open_student(self):
        self.slogin = StudentLogin()
        self.slogin.show()
        self.close()
      from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                             QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt
from admin.manage_students import ManageStudents
from admin.manage_questions import ManageQuestions
from admin.view_results import ViewResults

class AdminDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Dashboard")
        self.setFixedSize(600, 480)

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(15)

        title = QLabel("👨‍💼 Admin Dashboard")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        layout.addSpacing(20)

        for text, handler in [
            ("👥  Manage Students", self.open_students),
            ("📚  Manage Questions (MCQ)", self.open_questions),
            ("📊  View Results & Violations", self.open_results),
            ("🚪  Logout", self.logout)
        ]:
            btn = QPushButton(text)
            btn.setMinimumHeight(45)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget { background: #ecf0f1; }
            QPushButton {
                background: #2980b9; color: white; border-radius: 6px;
                font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: #3498db; }
        """)

    def open_students(self):
        self.w = ManageStudents(); self.w.show()

    def open_questions(self):
        self.w = ManageQuestions(); self.w.show()

    def open_results(self):
        self.w = ViewResults(); self.w.show()

    def logout(self):
        from admin.admin_login import AdminLogin
        self.login = AdminLogin()
        self.login.show()
        self.close()
      from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QLabel)
from database import get_conn

class ManageStudents(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Students")
        self.resize(700, 500)
        layout = QVBoxLayout()

        title = QLabel("👥 Student Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        form = QHBoxLayout()
        self.roll = QLineEdit(); self.roll.setPlaceholderText("Roll No")
        self.name = QLineEdit(); self.name.setPlaceholderText("Name")
        self.pwd  = QLineEdit(); self.pwd.setPlaceholderText("Password")
        add = QPushButton("Add"); add.clicked.connect(self.add_student)
        form.addWidget(self.roll); form.addWidget(self.name)
        form.addWidget(self.pwd); form.addWidget(add)
        layout.addLayout(form)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Roll No", "Name", "Password"])
        layout.addWidget(self.table)

        del_btn = QPushButton("Delete Selected")
        del_btn.setStyleSheet("background:#c0392b; color:white;")
        del_btn.clicked.connect(self.delete_student)
        layout.addWidget(del_btn)

        self.setLayout(layout)
        self.load()

    def load(self):
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT id, roll_no, name, password FROM students")
        rows = c.fetchall(); conn.close()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_student(self):
        r, n, p = self.roll.text().strip(), self.name.text().strip(), self.pwd.text().strip()
        if not (r and n and p):
            QMessageBox.warning(self, "Error", "Fill all fields"); return
        try:
            conn = get_conn(); c = conn.cursor()
            c.execute("INSERT INTO students (roll_no, name, password) VALUES (?,?,?)", (r, n, p))
            conn.commit(); conn.close()
            self.roll.clear(); self.name.clear(); self.pwd.clear()
            self.load()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def delete_student(self):
        row = self.table.currentRow()
        if row < 0: return
        sid = self.table.item(row, 0).text()
        conn = get_conn(); c = conn.cursor()
        c.execute("DELETE FROM students WHERE id=?", (sid,))
        conn.commit(); conn.close()
        self.load()
      from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QLabel, QComboBox, QTextEdit)
from database import get_conn

class ManageQuestions(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Questions")
        self.resize(900, 650)
        layout = QVBoxLayout()

        title = QLabel("📚 Add MCQ Question")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.q = QTextEdit(); self.q.setPlaceholderText("Question"); self.q.setFixedHeight(60)
        layout.addWidget(self.q)

        opts = QHBoxLayout()
        self.a = QLineEdit(); self.a.setPlaceholderText("Option A")
        self.b = QLineEdit(); self.b.setPlaceholderText("Option B")
        self.c = QLineEdit(); self.c.setPlaceholderText("Option C")
        self.d = QLineEdit(); self.d.setPlaceholderText("Option D")
        opts.addWidget(self.a); opts.addWidget(self.b)
        opts.addWidget(self.c); opts.addWidget(self.d)
        layout.addLayout(opts)

        bottom = QHBoxLayout()
        self.correct = QComboBox(); self.correct.addItems(["A", "B", "C", "D"])
        add = QPushButton("Add Question"); add.clicked.connect(self.add_q)
        bottom.addWidget(QLabel("Correct:")); bottom.addWidget(self.correct)
        bottom.addStretch(); bottom.addWidget(add)
        layout.addLayout(bottom)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Question", "A", "B", "C", "D", "Ans"])
        layout.addWidget(self.table)

        del_btn = QPushButton("Delete Selected")
        del_btn.setStyleSheet("background:#c0392b; color:white;")
        del_btn.clicked.connect(self.delete_q)
        layout.addWidget(del_btn)

        self.setLayout(layout)
        self.load()

    def load(self):
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT id, question, option_a, option_b, option_c, option_d, correct_option FROM questions")
        rows = c.fetchall(); conn.close()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_q(self):
        q = self.q.toPlainText().strip()
        a, b, c, d = self.a.text().strip(), self.b.text().strip(), self.c.text().strip(), self.d.text().strip()
        if not (q and a and b and c and d):
            QMessageBox.warning(self, "Error", "Fill all fields"); return
        conn = get_conn(); cur = conn.cursor()
        cur.execute("""INSERT INTO questions 
            (question, option_a, option_b, option_c, option_d, correct_option, marks)
            VALUES (?,?,?,?,?,?,1)""",
            (q, a, b, c, d, self.correct.currentText()))
        conn.commit(); conn.close()
        self.q.clear(); self.a.clear(); self.b.clear(); self.c.clear(); self.d.clear()
        self.load()

    def delete_q(self):
        row = self.table.currentRow()
        if row < 0: return
        qid = self.table.item(row, 0).text()
        conn = get_conn(); c = conn.cursor()
        c.execute("DELETE FROM questions WHERE id=?", (qid,))
        conn.commit(); conn.close()
        self.load()
      from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QLabel, QMessageBox)
from database import get_conn
import pandas as pd
from PyQt6.QtWidgets import QFileDialog

class ViewResults(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Results")
        self.resize(850, 550)

        layout = QVBoxLayout()
        title = QLabel("📊 Student Results")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Roll No", "Name", "Score", "Total", "Violations", "Submitted", "Status"])
        layout.addWidget(self.table)

        export = QPushButton("📥 Export to Excel")
        export.clicked.connect(self.export)
        layout.addWidget(export)

        self.setLayout(layout)
        self.load()

    def load(self):
        conn = get_conn(); c = conn.cursor()
        c.execute("""SELECT s.roll_no, s.name, r.score, r.total, r.violations,
                            r.submitted_at
                     FROM results r JOIN students s ON r.student_id = s.id
                     ORDER BY r.score DESC""")
        rows = c.fetchall(); conn.close()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            status = "PASS" if row[2] >= row[3] * 0.4 else "FAIL"
            if row[4] > 5: status = "FLAGGED"
            data = list(row) + [status]
            for j, val in enumerate(data):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def export(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save", "results.xlsx", "*.xlsx")
        if not path: return
        conn = get_conn()
        df = pd.read_sql_query("""SELECT s.roll_no, s.name, r.score, r.total,
                                          r.violations, r.submitted_at
                                   FROM results r JOIN students s ON r.student_id = s.id""", conn)
        conn.close()
        df.to_excel(path, index=False)
        QMessageBox.information(self, "Done", f"Exported to {path}")
      from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from database import get_conn

class StudentLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Login")
        self.setFixedSize(400, 340)
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(12)

        title = QLabel("🎓 Student Login")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        self.roll = QLineEdit(); self.roll.setPlaceholderText("Roll Number")
        self.pwd  = QLineEdit(); self.pwd.setPlaceholderText("Password")
        self.pwd.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.roll); layout.addWidget(self.pwd)

        btn = QPushButton("Start Exam")
        btn.clicked.connect(self.login)
        layout.addWidget(btn)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget { background:#ecf0f1; }
            QLineEdit { padding:10px; border:1px solid #bdc3c7; border-radius:6px; background:white; }
            QPushButton { padding:10px; background:#27ae60; color:white; border-radius:6px; font-weight:bold; }
        """)

    def login(self):
        r, p = self.roll.text().strip(), self.pwd.text().strip()
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT id, name FROM students WHERE roll_no=? AND password=?", (r, p))
        row = c.fetchone(); conn.close()
        if not row:
            QMessageBox.warning(self, "Error", "Invalid login"); return

        from student.exam_window import ExamWindow
        self.exam = ExamWindow(student_id=row[0], student_name=row[1])
        self.exam.show()
        self.close()
      import cv2, os, time, json
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QRadioButton, QButtonGroup,
                             QMessageBox, QStackedWidget, QTextEdit)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from database import get_conn


class WebcamThread(QThread):
    frame_signal = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.frame_signal.emit(frame)
            time.sleep(0.05)
        cap.release()

    def stop(self):
        self.running = False


class ExamWindow(QWidget):
    def __init__(self, student_id, student_name):
        super().__init__()
        self.student_id = student_id
        self.student_name = student_name
        self.violations = 0
        self.snapshot_count = 0
        self.answers = {}
        self.current_q = 0

        self.setWindowTitle(f"Exam - {student_name}")
        self.showMaximized()

        # Load questions & exam
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT * FROM questions LIMIT 50")
        self.questions = c.fetchall()
        c.execute("SELECT id, title, duration_minutes FROM exams WHERE is_active=1 LIMIT 1")
        exam = c.fetchone()
        conn.close()

        self.exam_id = exam[0]
        self.exam_title = exam[1]
        self.duration = exam[2] * 60  # seconds
        self.remaining = self.duration
        self.total_marks = len(self.questions)

        # Snapshot dir
        self.snap_dir = f"assets/violations/student_{student_id}"
        os.makedirs(self.snap_dir, exist_ok=True)

        self.build_ui()
        self.start_webcam()
        self.start_timer()

        # Show instructions first
        self.show_instructions()

    # ---------- UI ----------
    def build_ui(self):
        main = QHBoxLayout()
        main.setContentsMargins(15, 15, 15, 15)
        main.setSpacing(15)

        # LEFT: Question area
        left = QVBoxLayout()

        self.header = QLabel()
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        left.addWidget(self.header)

        self.q_label = QLabel()
        self.q_label.setWordWrap(True)
        self.q_label.setStyleSheet(
            "font-size: 16px; padding: 15px; background: white; border-radius: 8px; min-height: 60px;")
        left.addWidget(self.q_label)

        self.btn_group = QButtonGroup(self)
        self.radio_widgets = []
        for i in range(4):
            rb = QRadioButton()
            rb.setStyleSheet("font-size: 15px; padding: 10px; background: white; border-radius: 6px;")
            rb.toggled.connect(self.save_answer)
            self.btn_group.addButton(rb, i)
            self.radio_widgets.append(rb)
            left.addWidget(rb)

        left.addStretch()

        nav = QHBoxLayout()
        self.prev_btn = QPushButton("← Previous")
        self.next_btn = QPushButton("Next →")
        self.submit_btn = QPushButton("✅ Submit Exam")
        self.submit_btn.setStyleSheet("background:#e67e22; color:white; font-weight:bold;")
        self.prev_btn.clicked.connect(self.prev_q)
        self.next_btn.clicked.connect(self.next_q)
        self.submit_btn.clicked.connect(self.confirm_submit)
        nav.addWidget(self.prev_btn)
        nav.addWidget(self.next_btn)
        nav.addStretch()
        nav.addWidget(self.submit_btn)
        left.addLayout(nav)

        main.addLayout(left, 3)

        # RIGHT: Webcam + Timer + status
        right = QVBoxLayout()

        self.timer_label = QLabel()
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: white; background:#c0392b; "
            "border-radius: 8px; padding: 12px;")
        right.addWidget(self.timer_label)

        self.cam_label = QLabel("Camera loading...")
        self.cam_label.setFixedSize(320, 240)
        self.cam_label.setStyleSheet("background: black; color: white; border-radius: 8px;")
        self.cam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right.addWidget(self.cam_label)

        self.violation_label = QLabel("⚠️ Violations: 0")
        self.violation_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #c0392b; padding: 8px;")
        right.addWidget(self.violation_label)

        right.addStretch()
        main.addLayout(right, 1)

        self.setLayout(main)
        self.setStyleSheet("QWidget { background:#ecf0f1; font-family: 'Segoe UI'; }")

    def show_instructions(self):
        QMessageBox.information(self, "Exam Instructions",
            f"📋 {self.exam_title}\n\n"
            f"• Total Questions: {self.total_marks}\n"
            f"• Duration: {self.duration//60} minutes\n"
            f"• Each question: 1 mark\n\n"
            "⚠️ ANTI-CHEATING ACTIVE:\n"
            "• Webcam is ON\n"
            "• Do NOT switch windows/tabs\n"
            "• Each violation will be recorded\n\n"
            "Click OK to start.")

    # ---------- Questions ----------
    def load_question(self):
        q = self.questions[self.current_q]
        # q = (id, question, a, b, c, d, correct, marks)
        self.header.setText(f"Question {self.current_q + 1} of {len(self.questions)}")
        self.q_label.setText(q[1])
        opts = [q[2], q[3], q[4], q[5]]
        for i, rb in enumerate(self.radio_widgets):
            rb.setText(f"{chr(65+i)}. {opts[i]}")
            rb.setChecked(self.answers.get(q[0]) == chr(65+i))

    def save_answer(self):
        rb = self.sender()
        if rb and rb.isChecked():
            q = self.questions[self.current_q]
            self.answers[q[0]] = chr(65 + self.btn_group.checkedId())

    def next_q(self):
        if self.current_q < len(self.questions) - 1:
            self.current_q += 1
            self.load_question()

    def prev_q(self):
        if self.current_q > 0:
            self.current_q -= 1
            self.load_question()

    # ---------- Timer ----------
    def start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)
        self.load_question()
        self.update_timer_label()

    def tick(self):
        self.remaining -= 1
        self.update_timer_label()
        if self.remaining <= 0:
            self.timer.stop()
            QMessageBox.warning(self, "Time Up", "Time is over! Exam will be submitted.")
            self.submit_exam()

    def update_timer_label(self):
        m, s = divmod(max(0, self.remaining), 60)
        self.timer_label.setText(f"⏱ {m:02d}:{s:02d}")

    # ---------- Webcam ----------
    def start_webcam(self):
        self.cam_thread = WebcamThread()
        self.cam_thread.frame_signal.connect(self.update_cam)
        self.cam_thread.start()

        # Periodic snapshot every 30 sec
        self.snap_timer = QTimer()
        self.snap_timer.timeout.connect(self.take_snapshot)
        self.snap_timer.start(30000)

    def update_cam(self, frame):
        self.last_frame = frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.cam_label.setPixmap(QPixmap.fromImage(img).scaled(
            320, 240, Qt.AspectRatioMode.KeepAspectRatio))

    def take_snapshot(self):
        if hasattr(self, 'last_frame'):
            self.snapshot_count += 1
            path = os.path.join(self.snap_dir, f"snap_{self.snapshot_count}_{int(time.time())}.jpg")
            cv2.imwrite(path, self.last_frame)

    # ---------- Anti-cheating ----------
    def changeEvent(self, event):
        # Detect window minimize / focus loss
        if event.type() == event.Type.ActivationChange:
            if not self.isActiveWindow() and self.isVisible():
                self.record_violation("Window focus lost")
        super().changeEvent(event)

    def record_violation(self, reason):
        self.violations += 1
        self.violation_label.setText(f"⚠️ Violations: {self.violations}")
        # Snapshot on violation
        if hasattr(self, 'last_frame'):
            path = os.path.join(self.snap_dir, f"violation_{self.violations}_{int(time.time())}.jpg")
            cv2.imwrite(path, self.last_frame)

        if self.violations >= 5:
            QMessageBox.critical(self, "⚠️ Warning",
                f"Too many violations ({self.violations})!\nExam will be auto-submitted.")
            self.submit_exam()

    # ---------- Submit ----------
    def confirm_submit(self):
        ans = QMessageBox.question(self, "Submit",
            f"Are you sure? You attempted {len(self.answers)}/{len(self.questions)} questions.")
        if ans == QMessageBox.StandardButton.Yes:
            self.submit_exam()

    def submit_exam(self):
        self.timer.stop()
        self.snap_timer.stop()
        self.cam_thread.stop()
        self.cam_thread.wait()

        # Auto-evaluate
        score = 0
        for q in self.questions:
            qid = q[0]
            correct = q[6]
            if self.answers.get(qid) == correct:
                score += q[7]

        # Save to DB
        conn = get_conn(); c = conn.cursor()
        c.execute("""INSERT INTO results 
            (student_id, exam_id, score, total, answers, violations, submitted_at)
            VALUES (?,?,?,?,?,?,?)""",
            (self.student_id, self.exam_id, score, self.total_marks,
             json.dumps(self.answers), self.violations,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); conn.close()

        # Show result window
        from student.result_window import ResultWindow
        self.result = ResultWindow(
            name=self.student_name, score=score,
            total=self.total_marks, violations=self.violations,
            attempted=len(self.answers))
        self.result.show()
        self.close()
      from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton)
from PyQt6.QtCore import Qt

class ResultWindow(QWidget):
    def __init__(self, name, score, total, violations, attempted):
        super().__init__()
        self.setWindowTitle("Result")
        self.setFixedSize(500, 480)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        title = QLabel("🎉 Exam Completed")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #27ae60;")
        layout.addWidget(title)

        pct = (score / total * 100) if total else 0
        status = "PASS ✅" if pct >= 40 else "FAIL ❌"
        if violations > 5: status = "FLAGGED ⚠️"

        info = QLabel(f"""
        <div style='text-align:center;'>
        <p style='font-size:18px;'><b>{name}</b></p>
        <p style='font-size:36px; color:#2980b9;'><b>{score} / {total}</b></p>
        <p style='font-size:20px;'>Percentage: <b>{pct:.1f}%</b></p>
        <p style='font-size:16px;'>Attempted: {attempted} / {total}</p>
        <p style='font-size:16px;'>Violations: <b style='color:#c0392b;'>{violations}</b></p>
        <p style='font-size:22px; margin-top:10px;'><b>{status}</b></p>
        </div>
        """)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget { background:#ecf0f1; }
            QPushButton { background:#2980b9; color:white; border-radius:6px; font-weight:bold; }
            QPushButton:hover { background:#3498db; }
        """)cd ExamApp
python main.py
