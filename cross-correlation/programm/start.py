import sys
from PyQt5.QtWidgets import QApplication
from main_widget import MainWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_widget = MainWidget()
    main_widget.setWindowTitle('Программа')
    main_widget.resize(800, 600)
    main_widget.show()
    sys.exit(app.exec_())
