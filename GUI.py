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
                    
                    # Przekazanie danych do dialogu wysyłającego
                    self.dialog3 = Dialog3(json_data=json_data)
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
    def __init__(self, json_data=None):
        super().__init__()
        self.setupUi(self)
        self.initialize_com_ports()
        self.serial_port = None
        self.json_data = json_data if json_data is not None else []
        self.current_index = 0
        self.baud_rate_warning_shown = False
        self.response_buffer = ''
        self.processing_complete = False  # Flaga oznaczająca zakończenie przetwarzania

        if self.json_data:
            self.textEdit.setText(f"Loaded {len(self.json_data)} records.")
            self.textEdit.append("Starting data sending.")

        self.SendButton.clicked.connect(self.start_sending)
        self.CancelButton.clicked.connect(self.close)

        self.read_timer = QTimer(self)
        self.read_timer.timeout.connect(self.read_data_from_serial)
        self.read_timer.start(100)

        self.send_timer = QTimer(self)

    def initialize_com_ports(self):
        com_ports = [port.device for port in serial.tools.list_ports.comports()]
        existing_ports = set(self.COMbox.itemText(i) for i in range(self.COMbox.count()))
        for port in com_ports:
            if port not in existing_ports:
                self.COMbox.addItem(port)

    def start_sending(self):
        if not self.json_data:
            QtWidgets.QMessageBox.critical(self, 'Error', 'No data to send.')
            return

        self.send_timer.timeout.connect(self.send_data)
        self.send_timer.start(2000)

    def send_data(self):
        if self.processing_complete:
            return

        if self.current_index >= len(self.json_data):
            self.processing_complete = True
            QtWidgets.QMessageBox.information(self, 'Info', 'All data has been sent.')
            self.send_timer.stop()
            return

        current_record = self.json_data[self.current_index]

        address = current_record.get('column_1')
        expected_interval = current_record.get('column_2')
        expected_state = current_record.get('column_3')

        port_name = self.COMbox.currentText()

        try:
            baud_rate = int(self.baudBox.currentText())
        except ValueError:
            if not self.baud_rate_warning_shown:
                self.log_error('Please select a valid baud rate.')
                self.baud_rate_warning_shown = True
            return

        if address:
            tshow_message = f"chat private {address} tshow \n"
        else:
            self.log_error('Invalid address in JSON file.')
            return

        self.textEdit.append(f"Sending: {tshow_message}")

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

            self.serial_port.write(tshow_message.encode('ascii'))
            self.textEdit.append(f"tshow command sent successfully (record {self.current_index + 1}/{len(self.json_data)}).")

            QTimer.singleShot(2000, self.check_response)

        except Exception as e:
            self.log_error(f'Failed to send data: {e}')

    def check_response(self):
        if self.processing_complete:
            return

        response_clean = self.response_buffer
        self.response_buffer = ''

        if response_clean.strip():
            self.textEdit.append(f"Debug - Full Response: {response_clean}")

            ansi_escape = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])')
            response_clean = ansi_escape.sub('', response_clean)

            self.textEdit.append(f"Debug - Cleaned Response: {response_clean}")

            current_record = self.json_data[self.current_index]
            address = current_record.get('column_1')

            # Sprawdzanie odpowiedzi na podstawie oczekiwanego adresu
            pattern = rf'<{address}>: \*you\* sconf: (\d+):(\d)'
            match = re.search(pattern, response_clean)
            if match:
                received_interval = match.group(1)
                received_state = match.group(2)

                received_state = 'y' if received_state == '1' else 'n'

                expected_interval = current_record.get('column_2')
                expected_state = current_record.get('column_3')

                if received_interval == expected_interval and received_state == expected_state:
                    self.textEdit.append(f"Data matches for address {address}. Sending OK message.")
                    self.send_ok_message()
                else:
                    self.textEdit.append(f"Data does not match for address {address}. Sending configuration.")
                    self.send_configuration(expected_interval, expected_state)
            else:
                self.textEdit.append(f"Failed to parse response. Response: {response_clean}")
                self.textEdit.append(f"No valid response received. Resending tshow command.")
        else:
            self.textEdit.append(f"No valid response received. Resending tshow command.")
            self.textEdit.append(f"Otrzymano: {response_clean}")

        # Sprawdzanie, czy zakończyć operację, jeśli wszystkie rekordy zostały przetworzone
        if self.current_index >= len(self.json_data):
            if not self.processing_complete:
                self.textEdit.append(f"All records processed successfully.")
                self.processing_complete = True
        else:
            self.textEdit.append(f"Sending: chat private {address} tshow")

    def send_configuration(self, interval, state):
        current_record = self.json_data[self.current_index]
        address = current_record.get('column_1')

        state_value = '1' if state == 'y' else '0'

        config_message = f"chat private {address} tconf:{interval}:{state_value} \n"

        try:
            self.serial_port.write(config_message.encode('ascii'))
            self.textEdit.append(f"Configuration sent successfully for address {address}.")
            
            self.current_index += 1

        except Exception as e:
            self.log_error(f'Failed to send configuration: {e}')

    def send_ok_message(self):
        current_record = self.json_data[self.current_index]
        address = current_record.get('column_1')

        ok_message = f"chat private {address} OK \n"

        try:
            self.serial_port.write(ok_message.encode('ascii'))
            self.textEdit.append(f"OK message sent successfully for address {address}.")
            
            self.current_index += 1

            # Sprawdzenie, czy zakończyć operację, jeśli wszystkie rekordy zostały przetworzone
            if self.current_index >= len(self.json_data):
                self.textEdit.append(f"All records processed successfully.")
                self.processing_complete = True

        except Exception as e:
            self.log_error(f'Failed to send OK message: {e}')

    def read_data_from_serial(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    response = self.serial_port.read(self.serial_port.in_waiting).decode('ascii')
                    self.response_buffer += response

                    ansi_escape = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])')
                    response_clean = ansi_escape.sub('', self.response_buffer)

                    self.textEdit.append(f"Received: {response_clean}")

                    if self.serial_port.in_waiting == 0:
                        self.check_response()

                # Sprawdzanie, czy zakończyć operację, jeśli wszystkie rekordy zostały przetworzone
                if self.current_index >= len(self.json_data) and not self.processing_complete:
                    self.textEdit.append(f"All records processed successfully.")
                    self.processing_complete = True

            except Exception as e:
                self.log_error(f'Failed to read data: {e}')

    def log_error(self, message):
        self.textEdit.append(f"Error: {message}")
        QtWidgets.QMessageBox.critical(self, 'Error', message)

    def close(self):
        """Override close method to ensure proper cleanup."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.textEdit.append("Serial port closed.")

        self.send_timer.stop()
        self.read_timer.stop()
        self.textEdit.append("Operation canceled and timers stopped.")

        super().close()  # Call the base class close method

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())