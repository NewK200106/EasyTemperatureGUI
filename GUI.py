import sys
import json
import serial.tools.list_ports  # Import modułu do obsługi portów COM
import serial
import re
import colorama  
from datetime import datetime
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
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
                    json_data = json.load(json_file)
                
                # Zakładamy, że interesuje Cię pierwszy wpis w pliku JSON
                first_entry = json_data[0]  # Pierwszy wpis w JSON

                # Pobierz wartości address, interval, state
                address = first_entry["column_1"]
                interval = int(first_entry["column_2"])
                state = first_entry["column_3"]

                # Przekazanie danych do dialogu wysyłającego
                self.dialog3 = Dialog3(address, interval, state)
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
    def __init__(self, address=None, interval=None, state=None):
        super().__init__()
        self.setupUi(self)
        self.initialize_com_ports()  # Inicjalizowanie portów COM

        # Zapisz przekazane dane do zmiennych
        self.serial_port = None
        self.address = address
        self.interval = interval
        self.state = state

        # Wyświetl dane w polu textEdit (opcjonalnie)
        self.textEdit.setText(f"Address: {self.address}, Interval: {self.interval}, State: {self.state}")

        # Połącz przyciski z funkcjami
        self.SendButton.clicked.connect(self.send_data)
        self.CancelButton.clicked.connect(self.close)

        # Timer do okresowego sprawdzania danych przychodzących
        self.read_timer = QTimer(self)
        self.read_timer.timeout.connect(self.read_data_from_serial)
        self.read_timer.start(100)  # Sprawdzaj dane co 100 ms

    def initialize_com_ports(self):
        # Pobierz dostępne porty COM i dodaj je do COMbox
        com_ports = [port.device for port in serial.tools.list_ports.comports()]
        self.COMbox.addItems(com_ports)

    def send_data(self):
        port_name = self.COMbox.currentText()

        try:
            baud_rate = int(self.baudBox.currentText())
        except ValueError:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Please select a valid baud rate.')
            return

        # Generowanie wiadomości na podstawie zmiennych
        if self.address and self.interval and self.state:
            data_to_send = f"chat private {self.address} tconf:{self.interval}:{self.state}"
        else:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Niepoprawne dane (address, interval, state).')
            return

        # Wyświetl wygenerowaną wiadomość w textEdit (opcjonalnie)
        self.textEdit.append(f"Sending: {data_to_send}")

        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

        try:
            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                rtscts=False,
                dsrdtr=False
            )
            self.serial_port.write(data_to_send.encode('utf-8'))
            QtWidgets.QMessageBox.information(self, 'Success', 'Data sent successfully.')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Error', f'Failed to send data: {e}')

    def read_data_from_serial(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    # Odbierz dane z portu szeregowego
                    response = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8')

                    # Obsługa kodów ucieczki ANSI za pomocą wyrażeń regularnych
                    ansi_escape = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])')
                    response_clean = ansi_escape.sub('', response)  # Usuń kody ucieczki z danych

                    # Wyświetl przetworzone dane w textEdit
                    self.textEdit.append(response_clean)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Error', f'Failed to read data: {e}')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())