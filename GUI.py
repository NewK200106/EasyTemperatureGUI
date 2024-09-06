import sys
from PyQt5 import QtWidgets, uic

# Load UI files (assuming your files are named EasyTGUI.ui, EasyT_new_file_creator.ui, and EasyT_file_table.ui)
window_class, window_base = uic.loadUiType("EasyTGUI.ui")
dialog1_class, dialog1_base = uic.loadUiType("EasyT_new_file_creator.ui")
dialog2_class, dialog2_base = uic.loadUiType("EasyT_file_table.ui")

class MainWindow(window_base, window_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Connect the "New" menu option to the function that opens Dialog1
        self.actionNew.triggered.connect(self.open_new_file_creator)

    def open_new_file_creator(self):
        # Create an instance of Dialog1 and show it
        self.dialog1 = Dialog1()
        self.dialog1.show()

class Dialog1(dialog1_base, dialog1_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class Dialog2(dialog2_base, dialog2_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Create instance of the main window
    window = MainWindow()
    
    # Show the main window
    window.show()

    # Start the application event loop
    sys.exit(app.exec_())
