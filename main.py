from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QWidget
from PyQt5 import uic
from PyQt5 import QtCore
import sys
import sqlite3

DB_NAME = "coffee.sqlite"


def do_with_db(db_name, clause_string, *additives, returning=False):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    if returning:
        data = cursor.execute(clause_string, additives).fetchall()
    else:
        cursor.execute(clause_string, additives)
        connection.commit()
    connection.close()
    if returning:
        return data


class CoffeeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        uic.loadUi("main.ui", self)
        self.refresh_table()

        self.addEditAction.triggered.connect(self.add_edit)

    def refresh_table(self):
        data = do_with_db(DB_NAME, "SELECT * FROM coffee", returning=True)
        titles = ["ID", "Название", "Степень обжарки", "Тип", "Вкус", "Цена, рублей", "Объём упаковки, граммов"]

        self.tableWidget.clear()
        self.tableWidget.setColumnCount(len(titles))
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setHorizontalHeaderLabels(titles)

        for row in range(len(data)):
            for col in range(len(titles)):
                item = QTableWidgetItem(str(data[row][col]))
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(row, col, item)

    def add_edit(self):
        self.add_edit_form = AddEditCoffee(self)
        self.add_edit_form.show()


class AddEditCoffee(QWidget):
    HEADER_TEXT = ("ID", "Название", "Степень обжарки", "Тип", "Вкус", "Цена, рублей", "Объем упаковки, граммов")
    DB_HAS_RECORD_CLAUSE = """
    SELECT count(*)
    FROM coffee
    WHERE id == ?
    """
    DB_INSERT_VALUES = """
    INSERT INTO coffee
    VALUES(?, ?, ?, ?, ?, ?, ?);
    """
    DB_DELETE_RECORD = """
    DELETE from coffee
    where id = ?
    """

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        uic.loadUi("addEditCoffeeForm.ui", self)
        self.init_ui()

    def init_ui(self):
        self.tableWidget.setRowCount(len(self.HEADER_TEXT))
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderLabels([""])
        self.tableWidget.setVerticalHeaderLabels(self.HEADER_TEXT)

        self.addEditButton.clicked.connect(self.commit)

    def commit(self):
        fields = []
        for i in range(len(self.HEADER_TEXT)):
            if self.tableWidget.item(i, 0):
                fields.append(self.tableWidget.item(i, 0).text())
        try:
            id = int(fields[0])
            name = fields[1]
            cook_grade = fields[2]
            type = fields[3]
            taste = fields[4]
            cost = int(fields[5])
            mass = int(fields[6])

            rec_exists = do_with_db(DB_NAME, self.DB_HAS_RECORD_CLAUSE, id, returning=True)
            if rec_exists:
                do_with_db(DB_NAME, self.DB_DELETE_RECORD, id)
            do_with_db(DB_NAME, self.DB_INSERT_VALUES,
                       id, name, cook_grade,
                       type, taste, cost, mass)
            if self.parent:
                self.parent.refresh_table()
            self.close()

        except(ValueError, IndexError):
            self.statusLabel.setText("Введены некорректные значения.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeWindow()
    window.show()
    sys.exit(app.exec())
