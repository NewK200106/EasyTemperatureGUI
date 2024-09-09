import sys
import json
import serial.tools.list_ports  # Import modułu do obsługi portów COM
from PyQt5 import QtWidgets, uic

# Load UI files
window_class, window_base = uic.loadUiType("EasyTGUI.ui")
dialog1_class, dialog1_base = uic.loadUiType("EasyT_new_file_creator.ui")
dialog2_class, dialog2_base = uic.loadUiType("EasyT_file_table.ui")
dialog3_class, dialog3_base = uic.loadUiType("EasyT_send.ui")  # Dialog z informacjami

class MainWindow(window_base, window_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Connect actions to functions
        self.actionNew.triggered.connect(self.open_new_file_creator)
        self.actionLoad.triggered.connect(self.load_from_json)
        self.actionSend_config.triggered.connect(self.send_config)  # Poprawiono na .triggered

    def open_new_file_creator(self):
        self.dialog1 = Dialog1()
        self.dialog1.show()

    def load_from_json(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Wczytaj dane z pliku JSON", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, 'r') as json_file:
                    data = json.load(json_file)
                self.dialog2 = Dialog2()
                self.dialog2.load_data(data)
                self.dialog2.show()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Błąd', f'Nie udało się wczytać pliku: {e}')

    def send_config(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Wczytaj dane z pliku JSON", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, 'r') as json_file:
                    json_data = json.load(json_file)  # Możesz przechować dane w jakiejś zmiennej, jeśli chcesz
                
                self.dialog3 = Dialog3()
                self.dialog3.fileinfo.setText(file_name)
                self.dialog3.initialize_com_ports()  # Inicjalizowanie portów COM
                self.dialog3.show()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Błąd', f'Nie udało się wczytać pliku: {e}')

class Dialog1(dialog1_base, dialog1_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.OK_Button.clicked.connect(self.open_table_dialog)

    def open_table_dialog(self):
        try:
            row_count = int(self.lineEdit.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, 'Błąd', 'Proszę wpisać poprawną liczbę')
            return

        self.dialog2 = Dialog2(row_count)
        self.dialog2.show()

class Dialog2(dialog2_base, dialog2_class):
    def __init__(self, row_count=None):
        super().__init__()
        self.setupUi(self)

        if row_count is not None:
            self.tableWidget.setRowCount(row_count)

        self.actionSave.triggered.connect(self.save_to_json)
        self.actionSave_as.triggered.connect(self.save_as_to_json)
        self.actionLoad.triggered.connect(self.load_from_json)

    def save_to_json(self):
        data = []
        for row in range(self.tableWidget.rowCount()):
            row_data = {}
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                row_data[f"column_{column}"] = item.text() if item else None
            data.append(row_data)

        with open('table_data.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        QtWidgets.QMessageBox.information(self, 'Sukces', 'Dane zostały zapisane do pliku JSON.')

    def save_as_to_json(self):
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Zapisz dane do pliku JSON", "", "JSON Files (*.json)")
        if file_name:
            try:
                data = []
                for row in range(self.tableWidget.rowCount()):
                    row_data = {}
                    for column in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, column)
                        row_data[f"column_{column}"] = item.text() if item else None
                    data.append(row_data)

                with open(file_name, 'w') as json_file:
                    json.dump(data, json_file, indent=4)

                QtWidgets.QMessageBox.information(self, 'Sukces', 'Dane zostały zapisane do pliku JSON.')
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Błąd', f'Nie udało się zapisać pliku: {e}')

    def load_from_json(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Wczytaj dane z pliku JSON", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, 'r') as json_file:
                    data = json.load(json_file)
                self.load_data(data)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Błąd', f'Nie udało się wczytać pliku: {e}')

    def load_data(self, data):
        if not data:
            return

        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(len(data[0]))

        for row_index, row_data in enumerate(data):
            for column_index, (column_name, value) in enumerate(row_data.items()):
                item = QtWidgets.QTableWidgetItem(value if value is not None else "")
                self.tableWidget.setItem(row_index, column_index, item)

class Dialog3(dialog3_base, dialog3_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def initialize_com_ports(self):
        # Pobierz dostępne porty COM i dodaj je do COMbox
        com_ports = [port.device for port in serial.tools.list_ports.comports()]
        self.COMbox.addItems(com_ports)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
