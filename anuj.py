# =========================================================
# FULL SCHOOL ERP SYSTEM
# =========================================================

import sys
import sqlite3
import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("school_erp.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    student_code TEXT,
    date TEXT,
    status TEXT
)
""")

conn.commit()

# DEFAULT ADMIN
cursor.execute(
    "SELECT * FROM users WHERE username='admin'"
)

if not cursor.fetchone():

    cursor.execute(
        "INSERT INTO users VALUES(?,?,?)",
        ("admin", "admin123", "admin")
    )

    conn.commit()


# =========================================================
# MEMORY
# =========================================================

students = []
student_counter = 0


# =========================================================
# STYLE
# =========================================================

GLASS_STYLE = """
QWidget {
    background-color: #0b0b0f;
    color: white;
    font-family: Segoe UI;
}

QPushButton {
    background-color: rgba(0,229,255,0.85);
    color: black;
    border-radius: 12px;
    padding: 10px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton:hover {
    background-color: rgba(0,229,255,1);
}

QLineEdit, QTextEdit, QListWidget, QComboBox {
    background-color: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 8px;
    color: white;
    border: 1px solid rgba(255,255,255,0.1);
}
"""


# =========================================================
# LOGIN SCREEN
# =========================================================

class LoginScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("LOGIN")
        self.resize(400, 320)
        self.setStyleSheet(GLASS_STYLE)

        layout = QVBoxLayout()

        title = QLabel("SCHOOL ERP LOGIN")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size:28px;
            color:#00e5ff;
            font-weight:bold;
        """)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.role = QComboBox()
        self.role.addItems([
            "admin",
            "teacher",
            "student"
        ])

        btn = QPushButton("LOGIN")
        btn.clicked.connect(self.login)

        layout.addWidget(title)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.role)
        layout.addWidget(btn)

        self.setLayout(layout)

    def login(self):

        u = self.username.text()
        p = self.password.text()
        r = self.role.currentText()

        cursor.execute("""
        SELECT * FROM users
        WHERE username=? AND password=? AND role=?
        """, (u, p, r))

        user = cursor.fetchone()

        if user:

            self.home = HomeScreen()
            self.home.show()
            self.close()

        else:
            QMessageBox.warning(
                self,
                "Error",
                "Invalid Login"
            )


# =========================================================
# HOME SCREEN
# =========================================================

class HomeScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SCHOOL ERP")
        self.resize(700, 450)
        self.setStyleSheet(GLASS_STYLE)

        layout = QVBoxLayout()

        title = QLabel("SCHOOL ERP SYSTEM")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size:30px;
            color:#00e5ff;
            font-weight:bold;
        """)

        student_btn = QPushButton(
            "👨‍🎓 STUDENT MODULE"
        )

        admin_btn = QPushButton(
            "👨‍💼 ADMIN MODULE"
        )

        student_btn.clicked.connect(
            self.open_student
        )

        admin_btn.clicked.connect(
            self.open_admin
        )

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addWidget(student_btn)
        layout.addWidget(admin_btn)
        layout.addStretch()

        self.setLayout(layout)

    def open_student(self):

        self.win = StudentScreen()
        self.win.show()

    def open_admin(self):

        self.win = AdminScreen()
        self.win.show()


# =========================================================
# ADD STUDENT
# =========================================================

class AddStudentDialog(QDialog):

    def __init__(self, refresh_callback):
        super().__init__()

        self.refresh_callback = refresh_callback
        self.image_path = ""

        self.setWindowTitle("ADD STUDENT")
        self.resize(450, 650)
        self.setStyleSheet(GLASS_STYLE)

        layout = QFormLayout()

        self.name = QLineEdit()
        self.cls = QLineEdit()
        self.section = QLineEdit()

        self.address = QTextEdit()

        self.father = QLineEdit()
        self.mother = QLineEdit()

        img_btn = QPushButton(
            "Choose Image"
        )

        img_btn.clicked.connect(
            self.choose_image
        )

        save_btn = QPushButton(
            "SAVE STUDENT"
        )

        save_btn.clicked.connect(
            self.save_student
        )

        layout.addRow("Name", self.name)
        layout.addRow("Class", self.cls)
        layout.addRow("Section", self.section)
        layout.addRow("Address", self.address)
        layout.addRow("Father", self.father)
        layout.addRow("Mother", self.mother)

        layout.addRow(img_btn)
        layout.addRow(save_btn)

        self.setLayout(layout)

    def choose_image(self):

        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if file:
            self.image_path = file

    def save_student(self):

        global student_counter

        student_counter += 1

        code = f"{student_counter:04d}"

        students.append({

            "code": code,
            "name": self.name.text(),
            "class": self.cls.text(),
            "section": self.section.text(),

            "address":
            self.address.toPlainText(),

            "father": self.father.text(),
            "mother": self.mother.text(),

            "image": self.image_path,

            "marks": {
                "math": 0,
                "science": 0,
                "english": 0,
                "computer": 0
            },

            "fees": {
                "total": 0,
                "paid": 0
            }

        })

        self.refresh_callback()

        QMessageBox.information(
            self,
            "Saved",
            "Student Added Successfully"
        )

        self.close()


# =========================================================
# ADMIN SCREEN
# =========================================================

class AdminScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ADMIN PANEL")
        self.resize(900, 700)
        self.setStyleSheet(GLASS_STYLE)

        layout = QVBoxLayout()

        title = QLabel("ADMIN DASHBOARD")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size:26px;
            color:#00e5ff;
            font-weight:bold;
        """)

        # SEARCH
        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Search by name or roll no..."
        )

        self.search.textChanged.connect(
            self.refresh
        )

        # LIST
        self.list = QListWidget()

        self.list.itemClicked.connect(
            self.open_options
        )

        layout.addWidget(title)
        layout.addWidget(self.search)
        layout.addWidget(self.list)

        self.setLayout(layout)

        self.refresh()

    def refresh(self):

        self.list.clear()

        text = self.search.text().lower()

        if not students:

            self.list.addItem(
                "No students added yet"
            )

            return

        for s in students:

            if text:

                if (
                    text not in s["name"].lower()
                    and
                    text not in s["code"]
                ):
                    continue

            due = (
                s["fees"]["total"]
                -
                s["fees"]["paid"]
            )

            self.list.addItem(
                f"""
ROLL NO : {s['code']}
NAME    : {s['name']}
CLASS   : {s['class']}
SECTION : {s['section']}
FEES DUE: ₹{due}
                """
            )

    def open_options(self, item):

        row = self.list.row(item)

        filtered_students = []

        text = self.search.text().lower()

        for s in students:

            if text:

                if (
                    text not in s["name"].lower()
                    and
                    text not in s["code"]
                ):
                    continue

            filtered_students.append(s)

        if row >= len(filtered_students):
            return

        student = filtered_students[row]

        self.option_window = QWidget()

        self.option_window.resize(420, 380)

        self.option_window.setStyleSheet(
            GLASS_STYLE
        )

        layout = QVBoxLayout()

        title = QLabel(student["name"])
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size:22px;
            color:#00e5ff;
            font-weight:bold;
        """)

        marks_btn = QPushButton(
            "🧾 EDIT MARKS"
        )

        fees_btn = QPushButton(
            "💰 EDIT FEES"
        )

        att_btn = QPushButton(
            "📅 ATTENDANCE"
        )

        marks_btn.clicked.connect(
            lambda:
            self.edit_marks(student)
        )

        fees_btn.clicked.connect(
            lambda:
            self.edit_fees(student)
        )

        att_btn.clicked.connect(
            lambda:
            self.attendance_window(student)
        )

        layout.addWidget(title)
        layout.addWidget(marks_btn)
        layout.addWidget(fees_btn)
        layout.addWidget(att_btn)

        self.option_window.setLayout(layout)

        self.option_window.show()

    def edit_marks(self, student):

        self.marks_window = QWidget()

        self.marks_window.resize(350, 320)

        self.marks_window.setStyleSheet(
            GLASS_STYLE
        )

        layout = QFormLayout()

        math = QLineEdit(
            str(student["marks"]["math"])
        )

        science = QLineEdit(
            str(student["marks"]["science"])
        )

        english = QLineEdit(
            str(student["marks"]["english"])
        )

        computer = QLineEdit(
            str(student["marks"]["computer"])
        )

        def save():

            student["marks"]["math"] = int(
                math.text() or 0
            )

            student["marks"]["science"] = int(
                science.text() or 0
            )

            student["marks"]["english"] = int(
                english.text() or 0
            )

            student["marks"]["computer"] = int(
                computer.text() or 0
            )

            QMessageBox.information(
                self,
                "Saved",
                "Marks Updated"
            )

            self.marks_window.close()

        btn = QPushButton("SAVE MARKS")

        btn.clicked.connect(save)

        layout.addRow("Math", math)
        layout.addRow("Science", science)
        layout.addRow("English", english)
        layout.addRow("Computer", computer)

        layout.addRow(btn)

        self.marks_window.setLayout(layout)

        self.marks_window.show()

    def edit_fees(self, student):

        self.fees_window = QWidget()

        self.fees_window.resize(350, 250)

        self.fees_window.setStyleSheet(
            GLASS_STYLE
        )

        layout = QFormLayout()

        total = QLineEdit(
            str(student["fees"]["total"])
        )

        paid = QLineEdit(
            str(student["fees"]["paid"])
        )

        def save():

            student["fees"]["total"] = int(
                total.text() or 0
            )

            student["fees"]["paid"] = int(
                paid.text() or 0
            )

            self.refresh()

            QMessageBox.information(
                self,
                "Saved",
                "Fees Updated"
            )

            self.fees_window.close()

        btn = QPushButton("SAVE FEES")

        btn.clicked.connect(save)

        layout.addRow("Total Fees", total)
        layout.addRow("Paid Fees", paid)

        layout.addRow(btn)

        self.fees_window.setLayout(layout)

        self.fees_window.show()

    def mark_today_attendance(
        self,
        student,
        status
    ):

        today = str(datetime.date.today())

        cursor.execute("""
        INSERT INTO attendance
        VALUES(?,?,?)
        """, (
            student["code"],
            today,
            status
        ))

        conn.commit()

        QMessageBox.information(
            self,
            "Saved",
            f"{status} marked for {today}"
        )

    def attendance_window(self, student):

        self.att_window = QWidget()

        self.att_window.resize(350, 250)

        self.att_window.setStyleSheet(
            GLASS_STYLE
        )

        layout = QVBoxLayout()

        title = QLabel(
            f"Attendance - {student['name']}"
        )

        title.setAlignment(Qt.AlignCenter)

        present = QPushButton(
            "✅ PRESENT"
        )

        absent = QPushButton(
            "❌ ABSENT"
        )

        leave = QPushButton(
            "🟡 LEAVE"
        )

        present.clicked.connect(
            lambda:
            self.mark_today_attendance(
                student,
                "Present"
            )
        )

        absent.clicked.connect(
            lambda:
            self.mark_today_attendance(
                student,
                "Absent"
            )
        )

        leave.clicked.connect(
            lambda:
            self.mark_today_attendance(
                student,
                "Leave"
            )
        )

        layout.addWidget(title)
        layout.addWidget(present)
        layout.addWidget(absent)
        layout.addWidget(leave)

        self.att_window.setLayout(layout)

        self.att_window.show()


# =========================================================
# STUDENT SCREEN
# =========================================================

class StudentScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("STUDENT SYSTEM")
        self.resize(950, 700)

        self.setStyleSheet(GLASS_STYLE)

        layout = QVBoxLayout()

        title = QLabel("STUDENT LIST")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size:22px;
            color:#00e5ff;
            font-weight:bold;
        """)

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Search student..."
        )

        self.search.textChanged.connect(
            self.refresh_list
        )

        self.list = QListWidget()

        self.list.itemClicked.connect(
            self.open_student
        )

        btn = QPushButton("ADD STUDENT")

        btn.clicked.connect(
            self.add_student
        )

        layout.addWidget(title)
        layout.addWidget(self.search)
        layout.addWidget(self.list)
        layout.addWidget(btn)

        self.setLayout(layout)

        self.refresh_list()

    def refresh_list(self):

        self.list.clear()

        text = self.search.text().lower()

        for s in students:

            if text:

                if (
                    text not in s["name"].lower()
                    and
                    text not in s["code"]
                ):
                    continue

            self.list.addItem(
                f"{s['code']} | {s['name']}"
            )

    def calculate_attendance(self, code):

        cursor.execute("""
        SELECT status FROM attendance
        WHERE student_code=?
        """, (code,))

        data = cursor.fetchall()

        if not data:
            return 0

        total = len(data)

        present = 0

        for d in data:

            if d[0] == "Present":
                present += 1

        return round(
            (present / total) * 100,
            2
        )

    def generate_marksheet_pdf(self, student):

        file = f"{student['code']}_marksheet.pdf"

        c = canvas.Canvas(file, pagesize=A4)

        c.setFont(
            "Helvetica-Bold",
            18
        )

        c.drawString(
            200,
            800,
            "STUDENT MARKSHEET"
        )

        m = student["marks"]

        c.setFont("Helvetica", 12)

        c.drawString(
            50,
            760,
            f"Name: {student['name']}"
        )

        c.drawString(
            50,
            740,
            f"Roll No: {student['code']}"
        )

        c.drawString(
            50,
            680,
            f"Math: {m['math']}"
        )

        c.drawString(
            50,
            660,
            f"Science: {m['science']}"
        )

        c.drawString(
            50,
            640,
            f"English: {m['english']}"
        )

        c.drawString(
            50,
            620,
            f"Computer: {m['computer']}"
        )

        c.save()

        QMessageBox.information(
            self,
            "Saved",
            file
        )

    def generate_fees_pdf(self, student):

        file = f"{student['code']}_fees.pdf"

        c = canvas.Canvas(file, pagesize=A4)

        c.setFont(
            "Helvetica-Bold",
            18
        )

        c.drawString(
            220,
            800,
            "FEES RECEIPT"
        )

        f = student["fees"]

        c.setFont("Helvetica", 12)

        c.drawString(
            50,
            760,
            f"Name: {student['name']}"
        )

        c.drawString(
            50,
            740,
            f"Roll No: {student['code']}"
        )

        c.drawString(
            50,
            680,
            f"Total Fees: {f['total']}"
        )

        c.drawString(
            50,
            660,
            f"Paid Fees: {f['paid']}"
        )

        c.drawString(
            50,
            640,
            f"Due Fees: {f['total'] - f['paid']}"
        )

        c.save()

        QMessageBox.information(
            self,
            "Saved",
            file
        )

    def attendance_pdf(self, student):

        file = f"{student['code']}_attendance.pdf"

        c = canvas.Canvas(file, pagesize=A4)

        c.setFont(
            "Helvetica-Bold",
            18
        )

        c.drawString(
            180,
            800,
            "ATTENDANCE REPORT"
        )

        cursor.execute("""
        SELECT * FROM attendance
        WHERE student_code=?
        """, (student["code"],))

        records = cursor.fetchall()

        y = 740

        for r in records:

            c.drawString(
                50,
                y,
                f"Date: {r[1]}   Status: {r[2]}"
            )

            y -= 20

        percent = self.calculate_attendance(
            student["code"]
        )

        c.drawString(
            50,
            y - 20,
            f"Attendance Percentage: {percent}%"
        )

        c.save()

        QMessageBox.information(
            self,
            "Saved",
            file
        )

    # =====================================================
    # OPEN STUDENT
    # =====================================================

    def open_student(self, item):

        student = students[
            self.list.row(item)
        ]

        self.win = QWidget()

        self.win.resize(650, 750)

        self.win.setWindowTitle(
            student["name"]
        )

        self.win.setStyleSheet(
            GLASS_STYLE
        )

        layout = QVBoxLayout()

        name = QLabel(student["name"])

        name.setAlignment(Qt.AlignCenter)

        name.setStyleSheet("""
            font-size:24px;
            color:#00e5ff;
            font-weight:bold;
        """)

        image_label = QLabel()

        image_label.setAlignment(
            Qt.AlignCenter
        )

        image_label.setFixedSize(
            200,
            200
        )

        if student.get("image"):

            pixmap = QPixmap(
                student["image"]
            )

            if not pixmap.isNull():

                pixmap = pixmap.scaled(
                    200,
                    200,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                image_label.setPixmap(
                    pixmap
                )

            else:

                image_label.setText(
                    "Image not found"
                )

        else:

            image_label.setText(
                "No Image"
            )

        details = QLabel(f"""

ROLL NO : {student['code']}

CLASS   : {student['class']}

SECTION : {student['section']}

FATHER  : {student['father']}

MOTHER  : {student['mother']}

ADDRESS :

{student['address']}

""")

        details.setStyleSheet("""
            font-size:16px;
            padding:15px;
            background: rgba(255,255,255,0.04);
            border-radius:12px;
        """)

        attendance = QLabel(
            f"Attendance Percentage : {self.calculate_attendance(student['code'])}%"
        )

        attendance.setStyleSheet("""
            font-size:16px;
            color:#00e5ff;
            font-weight:bold;
            padding:10px;
        """)

        marks_btn = QPushButton(
            "📄 MARKSHEET PDF"
        )

        fees_btn = QPushButton(
            "💰 FEES PDF"
        )

        att_btn = QPushButton(
            "📅 ATTENDANCE PDF"
        )

        marks_btn.clicked.connect(
            lambda:
            self.generate_marksheet_pdf(
                student
            )
        )

        fees_btn.clicked.connect(
            lambda:
            self.generate_fees_pdf(
                student
            )
        )

        att_btn.clicked.connect(
            lambda:
            self.attendance_pdf(
                student
            )
        )

        layout.addWidget(name)

        layout.addWidget(image_label)

        layout.addWidget(details)

        layout.addWidget(attendance)

        layout.addWidget(marks_btn)

        layout.addWidget(fees_btn)

        layout.addWidget(att_btn)

        self.win.setLayout(layout)

        self.win.show()

    def add_student(self):

        AddStudentDialog(
            self.refresh_list
        ).exec_()


# =========================================================
# RUN
# =========================================================

app = QApplication(sys.argv)

login = LoginScreen()
login.show()

sys.exit(app.exec_())