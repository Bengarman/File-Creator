

from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
from ODXF_Creator import Ui_Dialog as odxfScript
from IVS_Creator import Ui_Dialog as ivsScript


class Ui_Dialog(object):
    def odxfButtonPushed(self, Previous):
        # Hides the previous UI Screen
        Previous.hide()
        # Creates a new Dialog
        self.dialog = QtWidgets.QDialog()
        # Assigns the ui element to the new Dialog
        self.dialog.ui = odxfScript()

        self.dialog.ui.setupUi(self.dialog)
        # Shows the UI Dialog
        self.dialog.show()


    def ivsButtonPushed(self, Previous):
        # Hides the previous UI Screen
        Previous.hide()
        # Creates a new Dialog
        self.dialog = QtWidgets.QDialog()
        # Assigns the ui element to the new Dialog
        self.dialog.ui = ivsScript()

        self.dialog.ui.setupUi(self.dialog)
        # Shows the UI Dialog
        self.dialog.show()

    def setupUi(self, Dialog):
        #Code to create the UI Design
        Dialog.setObjectName("Dialog")
        Dialog.resize(522, 198)
        self.odxfButton = QtWidgets.QPushButton(Dialog)
        self.odxfButton.setGeometry(QtCore.QRect(30, 70, 221, 101))
        self.odxfButton.setObjectName("odxfButton")
        self.odxfButton.clicked.connect(partial(self.odxfButtonPushed, Dialog))
        self.ivsButton = QtWidgets.QPushButton(Dialog)
        self.ivsButton.setGeometry(QtCore.QRect(270, 70, 221, 101))
        self.ivsButton.setObjectName("ivsButton")
        self.ivsButton.clicked.connect(partial(self.ivsButtonPushed, Dialog))
        self.titleLabel = QtWidgets.QLabel(Dialog)
        self.titleLabel.setGeometry(QtCore.QRect(30, 20, 461, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "File Creator"))
        self.odxfButton.setText(_translate("Dialog", "ODXF"))
        self.ivsButton.setText(_translate("Dialog", "IVS"))
        self.titleLabel.setText(_translate("Dialog", "File Creator"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    app.setWindowIcon(QtGui.QIcon('icon.ico'))
    Dialog.setWindowIcon(QtGui.QIcon('icon.ico'))
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
