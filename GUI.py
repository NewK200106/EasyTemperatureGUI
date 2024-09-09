import sys
import json
from PyQt5 import QtWidgets, uic

# Load UI files
window_class, window_base = uic.loadUiType("EasyTGUI.ui")
dialog1_class, dialog1_base = uic.loadUiType("EasyT_new_file_creator.ui")
dialog2_class, dialog2_base = uic.loadUiType("EasyT_file_table.ui")  # Dialog z tabelą

class MainWindow(window_base, window_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Connect the "New" menu option to the function that opens Dialog1
        self.actionNew.triggered.connect(self.open_new_file_creator)
        self.actionLoad.triggered.connect(self.load_from_json)  # Podłącz do funkcji wczytywania danych

    def open_new_file_creator(self):
        # Utwórz instancję Dialog1 i pokaż ją
        self.dialog1 = Dialog1()
        self.dialog1.show()

    def load_from_json(self):
        # Otwórz okno dialogowe do wyboru pliku
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Wczytaj dane z pliku JSON", "", "JSON Files (*.json)")
        if file_name:
            try:
                # Wczytaj dane z pliku JSON
                with open(file_name, 'r') as json_file:
                    data = json.load(json_file)

                # Stwórz nową instancję Dialog2 i załaduj dane
                self.dialog2 = Dialog2()
                self.dialog2.load_data(data)
                self.dialog2.show()

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Błąd', f'Nie udało się wczytać pliku: {e}')

class Dialog1(dialog1_base, dialog1_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Podłącz przycisk "OK" do funkcji otwierającej Dialog2
        self.OK_Button.clicked.connect(self.open_table_dialog)

    def open_table_dialog(self):
        # Pobierz liczbę wierszy z QLineEdit w Dialog1
        try:
            row_count = int(self.lineEdit.text())  # Zakładam, że pole QLineEdit nazywa się 'lineEdit'
        except ValueError:
            QtWidgets.QMessageBox.warning(self, 'Błąd', 'Proszę wpisać poprawną liczbę')
            return

        # Utwórz instancję Dialog2 (z tabelą) i przekaż liczbę wierszy
        self.dialog2 = Dialog2(row_count)
        self.dialog2.show()

class Dialog2(dialog2_base, dialog2_class):
    def __init__(self, row_count=None):
        super().__init__()
        self.setupUi(self)

        # Ustawienie liczby wierszy w QTableWidget, jeśli row_count jest podany
        if row_count is not None:
            self.tableWidget.setRowCount(row_count)

        # Podłącz przyciski z paska narzędzi do funkcji
        self.actionSave.triggered.connect(self.save_to_json)
        self.actionSave_as.triggered.connect(self.save_as_to_json)  # Dodaj funkcję "Save As"
        self.actionLoad.triggered.connect(self.load_from_json)  # Dodaj funkcję "Load"

    def save_to_json(self):
        # Pobieranie danych z tabeli
        data = []
        for row in range(self.tableWidget.rowCount()):
            row_data = {}
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item:  # Sprawdzamy, czy w komórce jest wartość
                    row_data[f"column_{column}"] = item.text()
                else:
                    row_data[f"column_{column}"] = None  # Jeśli pusta komórka, ustawiamy None
            data.append(row_data)

        # Zapis do pliku JSON
        with open('table_data.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        # Pokaż komunikat po zapisaniu
        QtWidgets.QMessageBox.information(self, 'Sukces', 'Dane zostały zapisane do pliku JSON.')

    def save_as_to_json(self):
        # Otwórz okno dialogowe do wyboru ścieżki pliku
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Zapisz dane do pliku JSON", "", "JSON Files (*.json)")
        if file_name:
            try:
                # Pobieranie danych z tabeli
                data = []
                for row in range(self.tableWidget.rowCount()):
                    row_data = {}
                    for column in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, column)
                        if item:  # Sprawdzamy, czy w komórce jest wartość
                            row_data[f"column_{column}"] = item.text()
                        else:
                            row_data[f"column_{column}"] = None  # Jeśli pusta komórka, ustawiamy None
                    data.append(row_data)

                # Zapis do pliku JSON
                with open(file_name, 'w') as json_file:
                    json.dump(data, json_file, indent=4)

                # Pokaż komunikat po zapisaniu
                QtWidgets.QMessageBox.information(self, 'Sukces', 'Dane zostały zapisane do pliku JSON.')

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Błąd', f'Nie udało się zapisać pliku: {e}')

    def load_from_json(self):
        # Otwórz okno dialogowe do wyboru pliku
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Wczytaj dane z pliku JSON", "", "JSON Files (*.json)")
        if file_name:
            try:
                # Wczytaj dane z pliku JSON
                with open(file_name, 'r') as json_file:
                    data = json.load(json_file)

                # Załaduj dane do tabeli
                self.load_data(data)

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Błąd', f'Nie udało się wczytać pliku: {e}')

    def load_data(self, data):
        if not data:
            return

        # Ustawienie liczby wierszy i kolumn w QTableWidget
        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(len(data[0]))

        # Wypełnienie tabeli danymi
        for row_index, row_data in enumerate(data):
            for column_index, (column_name, value) in enumerate(row_data.items()):
                item = QtWidgets.QTableWidgetItem(value if value is not None else "")
                self.tableWidget.setItem(row_index, column_index, item)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Create instance of the main window
    window = MainWindow()

    # Show the main window
    window.show()

    # Start the application event loop
    sys.exit(app.exec_())
