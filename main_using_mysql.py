import sys
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QTableWidget, QTableWidgetItem, QDialog, \
    QVBoxLayout, QLineEdit, QComboBox, QPushButton, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtCore import Qt
import mysql.connector



# Refactoring Code
class DatabaseConnection:
    def __init__(self, host="localhost", user="forPython", password="pythonCourse", database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database


    def connect(self):
        connection = mysql.connector.connect(host=self.host,
                                             user=self.user,
                                             password=self.password,
                                             database=self.database)
        return connection



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        # Top Menu
        file_menu_item = self.menuBar().addMenu("&File")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        # Sub Menu
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Phone Number"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Toolbar and it's elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Status Bar and it's Elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)


    def load_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        connection.close()


    def insert(self):
        insert_dialog = InsertDialog()
        insert_dialog.exec()


    def search(self):
        search_dialog = FindDataDialog()
        search_dialog.exec()


    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Clean previously added button
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)


    def edit(self):
        dialog = EditDialog()
        dialog.exec()


    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()


    def about(self):
        dialog = AboutDialog()
        dialog.exec()



class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(400)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name...")
        layout.addWidget(self.student_name)

        # Add a dropdown list widget
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add phone number widget
        self.phone_number = QLineEdit()
        self.phone_number.setPlaceholderText("Phone Number...")
        layout.addWidget(self.phone_number)

        # Add a submit button
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)


    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.phone_number.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()    # For only inserting data
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()  # Instantly loading the data after a data is inserted (i.e. refreshing)



class FindDataDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add a student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("ID...")
        layout.addWidget(self.student_name)

        # Search button widget
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        layout.addWidget(search_button)

        self.setLayout(layout)


    def search(self):
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        result = cursor.fetchall()
        rows = list(result)
        print(rows)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()



# Class for Status Bar Elements
class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(400)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get student name from selected row
        index = main_window.table.currentRow()  # Returns an integer
        student_name = main_window.table.item(index, 1).text() # Here, 'index' refers to row and '1' refers to column (i.e. "name" column)

        # Get id from selected row
        self.student_id = main_window.table.item(index, 0).text()

        # Shows value of selected row
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name...")
        layout.addWidget(self.student_name)

        course_name = main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        phone_number = main_window.table.item(index, 3).text()
        self.phone_number = QLineEdit(phone_number)
        self.phone_number.setPlaceholderText("Phone Number...")
        layout.addWidget(self.phone_number)

        # Add a submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)


    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.phone_number.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()



class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")
        self.setFixedWidth(350)

        layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)


    def delete_student(self):
        # Get row number and id from selected row
        index = main_window.table.currentRow()  # Returns an integer
        student_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        # Close the prompt window
        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("Record was deleted successfully!")
        confirmation_widget.exec()



class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        Student Management System allows us to create, read, update and delete operations on student records.
        """
        self.setText(content)



app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())

# ====================================================================================================================
# Difference between MYSQL and sqlite3

#     MYSQL
# - Better Concurrency
# - Better for large data
# - In-built Authentication
# - Support many data types
# - Can handle multiple user at same time

# ------------------------------------------------------------------

#     sqlite3
# - Easy to use
# - Portable
# - For development and testing
# - File Based System


