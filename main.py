from PyQt5.QtWidgets import QApplication, QMainWindow,  QTableWidgetItem
from PyQt5 import uic
import sys
import sqlite3

DB_NAME = "coffee.sqlite"


class CoffeeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        uic.loadUi("main.ui", self)
        self.refresh_table()

    def refresh_table(self):
        data = do_with_db(DB_NAME, "SELECT * FROM coffee", returning=True)
        titles = ["ID", "Название", "Степень обжарки", "Тип", "Вкус", "Цена, рублей", "Объём упаковки, граммов"]

        self.tableWidget.clear()
        self.tableWidget.setColumnCount(len(titles))
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setHorizontalHeaderLabels(titles)

        for row in range(len(data)):
            for col in range(len(titles)):
                self.tableWidget.setItem(row, col, QTableWidgetItem(str(data[row][col])))


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeWindow()
    window.show()
    sys.exit(app.exec())
