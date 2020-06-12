

from PyQt5 import QtCore, QtGui, QtWidgets
import os, glob
import xml.etree.ElementTree as ET
import datetime
import json
from functools import partial



class Ui_Dialog(object):

    def InitalLoad(self):
        with open(r'config.json') as json_file:
            data = json.load(json_file)
            fileLocation = data["odxfPath"]
        if fileLocation != "":
            self.fileLocationLineEdit.setText(fileLocation)
            global path
            path = fileLocation + "\\"
            self.initaliseVehicleComboBox()

    def fileLocationButtonPushed(self):
        #Used for setting the location of the IVS Files
        with open(r'config.json') as json_file:
            data = json.load(json_file)
            fileLocation = data["odxfPath"]
            
        fileLoc = str(QtWidgets.QFileDialog.getExistingDirectory(None, "Select Directory", fileLocation))
        #Stores it in the filelocationLineEdit
        data["odxfPath"] = fileLoc
        
        with open(r'config.json', 'w') as outfile:
            json.dump(data, outfile)

        self.fileLocationLineEdit.setText(fileLoc)
        global path
        path = fileLoc + "\\"
        
        #Initalise the combobox for vehicles
        self.initaliseVehicleComboBox()

    def initaliseVehicleComboBox(self):
        #List all the vehicle lines that are available
        vehicles = []
        # Walk through the path and get all the main folders
        for x in os.walk(path):
            #Replace the full path with just the vehicle name
            vehicles.append(x[0].replace(path ,""))
        # Add a placeholder 
        vehicles[0] = "-- Select Vehicle --"
        #Clear the combobox and add items
        self.vehicleComboBox.clear()
        self.vehicleComboBox.addItems(vehicles)

    def vehicleComboBoxSelected(self):
        # get the modules available from the vehicle selected
        modules = ["-- Select Module --"]
        # Get the vehicle that was selected
        vehicle = self.vehicleComboBox.currentText()
        # Loop through all vehicles in the path
        for x in os.walk(path + vehicle + "\\"):
            # Get the path and split the vehicle line
            for y in x[2]:
                #Add to the modules list
                modules.append(y.split("-")[1])
        #Remopve dupliactes
        modules.insert(1,"19L310")
        modules.insert(2,"19L320")
        
        modules = list(dict.fromkeys(modules))
        #Clear the combo box and append the modules
        self.moduleComboBox.clear()
        self.moduleComboBox.addItems(modules)

    def moduleComboBoxSelected(self):
        # Get the different hardware models from previous inputs
        hardware = ["-- Select Hardware --"]
        #Get previous inputs
        vehicle = self.vehicleComboBox.currentText()
        module = self.moduleComboBox.currentText()
        #Get all files that have the correct details
        files = glob.glob(path + vehicle + "\\*" + module + "*.xml")
        #Loop through each file and get the area that is needed
        for x in files:
            c = x.split("\\")
            # Append the hardwarre tag
            hardware.append((c[len(c) - 1]).split("-")[0])     
        
        #remove duplicates from list
        hardware = list(dict.fromkeys(hardware))
        #Clear combobox and add new items
        self.hardwareComboBox.clear()
        self.hardwareComboBox.addItems(hardware)
        
    def hardwareComboBoxSelected(self):
        # Getting all the current valueswith the details enetered from previous boxs
        value = ["-- Select Value --"]
        #Getting combobox values 
        vehicle = self.vehicleComboBox.currentText()
        module = self.moduleComboBox.currentText()
        hardware = self.hardwareComboBox.currentText()
        # Gets all the files which have the needed details
        files = glob.glob(path + vehicle + "\\" + hardware +"*" + module + "*.xml")
        #Loop through each of the files and get just the values. Append to Values
        for x in files:
            c = x.split("\\")
            d = ((c[len(c) - 1]).split("-")[2])    
            value.append(d.split('.')[0])
        
        #Remove dupliacte values
        value = list(dict.fromkeys(value))
        # Clear combobox and add values
        self.valueComboBox.clear()
        self.valueComboBox.addItems(value)

    def valueComboBoxSelected(self):
        self.fileLineEdit.setText(self.hardwareComboBox.currentText() + "-" + self.moduleComboBox.currentText() + "-")


    def saveXML(self, XML, path):
        #Used for saving the xml to a specific file path
        XML.write(path, encoding='utf-8', xml_declaration=True)

        #Ensures that the correct encoding is used
        with open(path) as f:
            newText=f.read().replace("<?xml version='1.0' encoding='utf-8'?>", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>""")

        with open(path, "w") as f:
            f.write(newText)

    def createFileButtonPushed(self):
        #Used for creating the files from the combobox choices
        # Get combobox values
        vehicle = self.vehicleComboBox.currentText()
        module = self.moduleComboBox.currentText()
        hardware = self.hardwareComboBox.currentText()
        prevValue = self.valueComboBox.currentText()
        newValue = self.fileLineEdit.text()
        newPath = path + vehicle + "\\"

        # getthe path for the new file and the previous file
        prevFilePath = glob.glob(newPath + hardware +"*" + module + "*" + prevValue + ".xml")[0]
        prevFile = prevFilePath.split("\\")
        prevFile = prevFile[len(prevFile) - 1].split(".xml")[0]
        newFilePath = newPath + newValue + ".xml"
        newFile = newFilePath.split("\\")
        newFile = newFile[len(newFile) - 1].split(".xml")[0]

        # Register the namespace for the ivs files
        ET.register_namespace('xsi','http://www.w3.org/2001/XMLSchema-instance')
        
        #Open the previous file and parse through it
        prevFileXML = ET.parse(prevFilePath)
        prevFileRoot = prevFileXML.getroot()

        # If theres a successor in the file then open the successor
        # and set the predecessor value to be the new file
        successor = ""
        if prevFileRoot[0][2][0][5].text != None:
            successor = prevFileRoot[0][2][0][5].text
            successorFilePath = newPath + successor + ".xml"
            successorFileXML = ET.parse(successorFilePath)
            successorFileRoot = successorFileXML.getroot()
            successorFileRoot[0][2][0][4].text = newFile.split(".")[0]
            self.saveXML(successorFileXML,successorFilePath)
        
        #Set the previousfile successor to be the new one
        prevFileRoot[0][2][0][5].text = newFile
        # Save the previous file
        self.saveXML(prevFileXML,prevFilePath)

        #NOW WE USE THE PREVIOUS FILE FOR THE NEW ONE

        # If their is a successor then add the part number to the file
        if successor != "":
            prevFileRoot[0][2][0][5].text = successor
        else:
            # If not then remove it from the board
            prevFileRoot[0][2][0][5].text = None
        # Set the predecessor value 
        prevFileRoot[0][2][0][4].text = prevFile
        # Set the partnumber created earlier
        prevFileRoot[0][2][0][3].text = newFile
        # Save the file to the new file path
        self.saveXML(prevFileXML,newFilePath)
        QtWidgets.QMessageBox.about(None, "Created", "File Created Succesfully")
        
        # Initalise Type Combobox
        self.initaliseTypeComboBox()

    def initaliseTypeComboBox(self):
        # Getting the text from the comboboxes selected
        vehicle = self.vehicleComboBox.currentText()
        module = self.moduleComboBox.currentText()
        hardware = self.hardwareComboBox.currentText()
        newValue = self.fileLineEdit.text()
        newFilePath = path + vehicle + "\\" + newValue + ".xml"

        newFileXML = ET.parse(newFilePath)
        newFileRoot = newFileXML.getroot()

        #Checks if the file is signed
        if newFileRoot[0][2][0][2].text == "TRUE":
            # Signed
            self.aByteFieldLineEdit.setEnabled(True)
            self.aByteFieldLineEdit.setText("")
            self.hashBinaryTableLineEdit.setEnabled(True)
            self.hashBinaryTableLineEdit.setText("")
            self.hashValueLineEdit.setEnabled(True)
            self.hashValueLineEdit.setText("")
            self.rootHashLineEdit.setEnabled(True)
            self.rootHashLineEdit.setText("")
        else:
            # Not Signed
            self.aByteFieldLineEdit.setText("Not Signed")
            self.aByteFieldLineEdit.setEnabled(False)
            self.hashBinaryTableLineEdit.setText("Not Signed")
            self.hashBinaryTableLineEdit.setEnabled(False)
            self.hashValueLineEdit.setText("Not Signed")
            self.hashValueLineEdit.setEnabled(False)
            self.rootHashLineEdit.setText("Not Signed")
            self.rootHashLineEdit.setEnabled(False)

        #Used to get the different areas which can be updated
        types = []
        #loops through each area accessible
        for x in (newFileRoot[0][3][0][2][1]):
            types.append(str(x.attrib['ID']) +  " - " + str(x.attrib['TYPE']))
        #Adds a placeholder value
        types.insert(0, "-- Select Type --")
        self.typeComboBox.clear()
        self.typeComboBox.addItems(types)

    def typeComboBoxSelected(self):
        # Getting the text from the comboboxes selected
        vehicle = self.vehicleComboBox.currentText()
        module = self.moduleComboBox.currentText()
        hardware = self.hardwareComboBox.currentText()
        newValue = self.fileLineEdit.text()
        newFilePath = path + vehicle + "\\" + newValue + ".xml"

        newFileXML = ET.parse(newFilePath)
        newFileRoot = newFileXML.getroot()

        #Checks if the file is signed
        if newFileRoot[0][2][0][2].text == "FALSE":
            #Gets the id from the combobox
            idName = self.typeComboBox.currentText().split(" - ")[0]
            #Loop through each of the areas that could be updated
            for x in newFileRoot[0][3][0][2][1]:
                    #Checks if it is the correct area
                    if x.attrib["ID"] == idName:
                        #If it is update the placeholder text
                        temp = x[1].text.split("-")
                        self.partNumberLineEdit.setText(temp[0] + "-" + temp[1] + "-")
        else:
            #Get the id from the combobox
            idName = self.typeComboBox.currentText().split(" - ")[0]
            idName = idName.split("_")
            prev = idName[2] + "-" + idName[3] + "-" + idName[4]
            #Set the placeholder to previous value
            temp = prev.split("-")
            self.partNumberLineEdit.setText(temp[0] + "-" + temp[1] + "-")

    def updateFileButtonPushed(self):
        # Getting the text from the comboboxes selected
        vehicle = self.vehicleComboBox.currentText()
        module = self.moduleComboBox.currentText()
        hardware = self.hardwareComboBox.currentText()
        newValue = self.fileLineEdit.text()
        newFilePath = path + vehicle + "\\" + newValue + ".xml"

        newFileXML = ET.parse(newFilePath)
        newFileRoot = newFileXML.getroot()

        #Checks if file is signed or not
        if newFileRoot[0][2][0][2].text == "TRUE":
            # Get the value in the combobox to update 
            idName = self.typeComboBox.currentText().split(" - ")[0]
            # Split the value to be updated by the dashes
            idParts = idName.split("_")
            #Split the new value down so its known where to update
            idParts2 = self.partNumberLineEdit.text().split("-")

            searchCriteria = []
            #Text to find
            searchCriteria.append(idParts[2] + "_" + idParts[3] + "_" + idParts[4])
            searchCriteria.append(idParts[2] + "-" + idParts[3] + "-" + idParts[4])
            #Text to replace
            searchCriteria.append(idParts2[0] + "_" + idParts2[1] + "_" + idParts2[2])
            searchCriteria.append(idParts2[0] + "-" + idParts2[1] + "-" + idParts2[2])
            
            # Loop through each area to be updated
            for x in newFileRoot[0][3][0][2][1]:
                #Checks if the area is the correct one to update
                if x.attrib["ID"] == idName:
                    # If it is then update the signing details in their corresponding locations
                    x[4][0][1].text = self.aByteFieldLineEdit.text()
                    x[5][0][3][5].text = self.hashBinaryTableLineEdit.text()
                    x[5][0][5][5].text = self.hashValueLineEdit.text()
                    x[5][0][6][1].text = self.rootHashLineEdit.text()

            # Now go through and find and replace the different areas 
            for elem in newFileRoot.getiterator():
                try:
                    #Checking in the text values
                    elem.text = elem.text.replace(searchCriteria[0],searchCriteria[2])
                    elem.text = elem.text.replace(searchCriteria[1],searchCriteria[3])
                except AttributeError:
                    pass
                
            for n in newFileXML.findall(".//"):
                for a in n.attrib:
                    #Checking in the attribute values
                    n.attrib[a] = n.attrib[a].replace(searchCriteria[0],searchCriteria[2])
                    n.attrib[a] = n.attrib[a].replace(searchCriteria[1],searchCriteria[3])

            #Save the new file with all updates
            self.saveXML(newFileXML,newFilePath)
            self.aByteFieldLineEdit.setText("")
            self.hashBinaryTableLineEdit.setText("")
            self.hashValueLineEdit.setText("")
            self.rootHashLineEdit.setText("")

        else:
            # If file is not signed
            # Get needed values from comboboxes
            idName = self.typeComboBox.currentText().split(" - ")[0]
            previousPartNumber = ""
            inputtedPartNumber = self.partNumberLineEdit.text().split("-")
            #Loop through each of the files and check if its the correct one.
            for x in newFileRoot[0][3][0][2][1]:
                if x.attrib["ID"] == idName:
                    previousPartNumber = x[1].text
            #Split the previous partnumber down where there is a dash 
            previousPartNumber = previousPartNumber.split("-")

            searchCriteria = []
            #Text to find
            searchCriteria.append(previousPartNumber[0] + "-" + previousPartNumber[1] + "-" + previousPartNumber[2])
            searchCriteria.append(previousPartNumber[0] + "minus" + previousPartNumber[1] + "minus" + previousPartNumber[2])
            searchCriteria.append(previousPartNumber[0] + "-XXXXX-" + previousPartNumber[2])
            #Text to replace
            searchCriteria.append(inputtedPartNumber[0] + "-" + inputtedPartNumber[1] + "-" + inputtedPartNumber[2])
            searchCriteria.append(inputtedPartNumber[0] + "minus" + inputtedPartNumber[1] + "minus" + inputtedPartNumber[2])
            searchCriteria.append(inputtedPartNumber[0] + "-XXXXX-" + inputtedPartNumber[2])

            # Now go through and find and replace the different areas 
            for elem in newFileRoot.getiterator():
                try:
                    #Checking the text values
                    elem.text = elem.text.replace(searchCriteria[0],searchCriteria[3])
                    elem.text = elem.text.replace(searchCriteria[1],searchCriteria[4])
                    elem.text = elem.text.replace(searchCriteria[2],searchCriteria[5])
                except AttributeError:
                    pass
                
            for n in newFileXML.findall(".//"):
                for a in n.attrib:
                    # Checking the attributes
                    n.attrib[a] = n.attrib[a].replace(searchCriteria[0],searchCriteria[3])
                    n.attrib[a] = n.attrib[a].replace(searchCriteria[1],searchCriteria[4])
                    n.attrib[a] = n.attrib[a].replace(searchCriteria[2],searchCriteria[5])

            # Check if their is a previos part number and update if necessary
            for x in newFileRoot[0][3][0][2][1]:
                #Checks to find the correct area
                if x.attrib["ID"] == idName:
                    try:
                        #Trys to see if its their. if it isnt then dont put it in
                        x[3][2][2].text = searchCriteria[0]
                    except Exception:
                        pass
            #Save the xml file with updated details
            self.saveXML(newFileXML,newFilePath)

        self.partNumberLineEdit.setText("")
        self.typeComboBox.setCurrentIndex(0)
        # Generic message box saying updated if it reaches here
        QtWidgets.QMessageBox.about(None, "Updated", "File Updated Succesfully")

    def closeEvent(self, Previous, event):
        # Close the current ui screen
        Previous.hide()
        # Ignore the close button event
        event.ignore()
        # Import the loading screen ui
        from fileCreator import Ui_Dialog as Back
        # Creates a new Dialog
        self.dialog = QtWidgets.QDialog()
        # Assigns the ui element to the new Dialog
        self.dialog.ui = Back()
        self.dialog.ui.setupUi(self.dialog)
        # Shows the UI Dialog
        self.dialog.show()

    def setupUi(self, Dialog):
        #Code to create the UI Design

        Dialog.setObjectName("Dialog")
        Dialog.resize(774, 510)
        Dialog.closeEvent = partial(self.closeEvent, Dialog)
        self.valueLabel = QtWidgets.QLabel(Dialog)
        self.valueLabel.setGeometry(QtCore.QRect(410, 140, 71, 41))
        self.valueLabel.setWordWrap(True)
        self.valueLabel.setObjectName("valueLabel")
        self.vehicleComboBox = QtWidgets.QComboBox(Dialog)
        self.vehicleComboBox.setGeometry(QtCore.QRect(100, 90, 261, 21))
        self.vehicleComboBox.setObjectName("vehicleComboBox")
        self.vehicleComboBox.addItem("")
        self.fileLineEdit = QtWidgets.QLineEdit(Dialog)
        self.fileLineEdit.setGeometry(QtCore.QRect(100, 200, 261, 22))
        self.fileLineEdit.setObjectName("fileLineEdit")
        self.aByteFieldLabel = QtWidgets.QLabel(Dialog)
        self.aByteFieldLabel.setGeometry(QtCore.QRect(20, 313, 81, 31))
        self.aByteFieldLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.aByteFieldLabel.setWordWrap(True)
        self.aByteFieldLabel.setObjectName("aByteFieldLabel")
        self.hardwareComboBox = QtWidgets.QComboBox(Dialog)
        self.hardwareComboBox.setGeometry(QtCore.QRect(100, 150, 261, 21))
        self.hardwareComboBox.setObjectName("hardwareComboBox")
        self.hardwareComboBox.addItem("")
        self.valueComboBox = QtWidgets.QComboBox(Dialog)
        self.valueComboBox.setGeometry(QtCore.QRect(490, 150, 261, 21))
        self.valueComboBox.setObjectName("valueComboBox")
        self.valueComboBox.addItem("")
        self.vehicleLabel = QtWidgets.QLabel(Dialog)
        self.vehicleLabel.setGeometry(QtCore.QRect(20, 90, 55, 31))
        self.vehicleLabel.setWordWrap(True)
        self.vehicleLabel.setObjectName("vehicleLabel")
        self.createFileButton = QtWidgets.QPushButton(Dialog)
        self.createFileButton.setGeometry(QtCore.QRect(410, 200, 341, 28))
        self.createFileButton.setObjectName("createFileButton")
        self.aByteFieldLineEdit = QtWidgets.QLineEdit(Dialog)
        self.aByteFieldLineEdit.setGeometry(QtCore.QRect(140, 320, 611, 22))
        self.aByteFieldLineEdit.setText("")
        self.aByteFieldLineEdit.setObjectName("aByteFieldLineEdit")
        self.moduleComboBox = QtWidgets.QComboBox(Dialog)
        self.moduleComboBox.setGeometry(QtCore.QRect(490, 90, 261, 21))
        self.moduleComboBox.setObjectName("moduleComboBox")
        self.moduleComboBox.addItem("")
        self.fileLabel = QtWidgets.QLabel(Dialog)
        self.fileLabel.setGeometry(QtCore.QRect(20, 200, 61, 16))
        self.fileLabel.setObjectName("fileLabel")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(20, 240, 731, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.hardwareLabel = QtWidgets.QLabel(Dialog)
        self.hardwareLabel.setGeometry(QtCore.QRect(20, 150, 61, 16))
        self.hardwareLabel.setObjectName("hardwareLabel")
        self.moduleLabel = QtWidgets.QLabel(Dialog)
        self.moduleLabel.setGeometry(QtCore.QRect(410, 90, 55, 16))
        self.moduleLabel.setObjectName("moduleLabel")
        self.updateFileButton = QtWidgets.QPushButton(Dialog)
        self.updateFileButton.setGeometry(QtCore.QRect(20, 460, 731, 28))
        self.updateFileButton.setObjectName("updateFileButton")
        self.titleLabel = QtWidgets.QLabel(Dialog)
        self.titleLabel.setGeometry(QtCore.QRect(20, 10, 731, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setWordWrap(True)
        self.titleLabel.setObjectName("titleLabel")
        self.fileLocationLineEdit = QtWidgets.QLineEdit(Dialog)
        self.fileLocationLineEdit.setGeometry(QtCore.QRect(100, 50, 631, 22))
        self.fileLocationLineEdit.setReadOnly(True)
        self.fileLocationLineEdit.setObjectName("fileLocationLineEdit")
        self.fileLocationLabel = QtWidgets.QLabel(Dialog)
        self.fileLocationLabel.setGeometry(QtCore.QRect(20, 45, 71, 31))
        self.fileLocationLabel.setWordWrap(True)
        self.fileLocationLabel.setObjectName("fileLocationLabel")
        self.fileLocationButton = QtWidgets.QPushButton(Dialog)
        self.fileLocationButton.setGeometry(QtCore.QRect(730, 49, 21, 22))
        self.fileLocationButton.setObjectName("fileLocationButton")
        self.hashBinaryTableLineEdit = QtWidgets.QLineEdit(Dialog)
        self.hashBinaryTableLineEdit.setGeometry(QtCore.QRect(140, 357, 611, 22))
        self.hashBinaryTableLineEdit.setText("")
        self.hashBinaryTableLineEdit.setObjectName("hashBinaryTableLineEdit")
        self.hashBinaryTableLabel = QtWidgets.QLabel(Dialog)
        self.hashBinaryTableLabel.setGeometry(QtCore.QRect(20, 350, 111, 31))
        self.hashBinaryTableLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.hashBinaryTableLabel.setWordWrap(True)
        self.hashBinaryTableLabel.setObjectName("hashBinaryTableLabel")
        self.hashValueLabel = QtWidgets.QLabel(Dialog)
        self.hashValueLabel.setGeometry(QtCore.QRect(20, 383, 111, 31))
        self.hashValueLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.hashValueLabel.setWordWrap(True)
        self.hashValueLabel.setObjectName("hashValueLabel")
        self.hashValueLineEdit = QtWidgets.QLineEdit(Dialog)
        self.hashValueLineEdit.setGeometry(QtCore.QRect(140, 390, 611, 22))
        self.hashValueLineEdit.setText("")
        self.hashValueLineEdit.setObjectName("hashValueLineEdit")
        self.rootHashLabel = QtWidgets.QLabel(Dialog)
        self.rootHashLabel.setGeometry(QtCore.QRect(20, 413, 111, 31))
        self.rootHashLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.rootHashLabel.setWordWrap(True)
        self.rootHashLabel.setObjectName("rootHashLabel")
        self.rootHashLineEdit = QtWidgets.QLineEdit(Dialog)
        self.rootHashLineEdit.setGeometry(QtCore.QRect(140, 420, 611, 22))
        self.rootHashLineEdit.setText("")
        self.rootHashLineEdit.setObjectName("rootHashLineEdit")
        self.partNumberLineEdit = QtWidgets.QLineEdit(Dialog)
        self.partNumberLineEdit.setGeometry(QtCore.QRect(490, 280, 261, 22))
        self.partNumberLineEdit.setText("")
        self.partNumberLineEdit.setObjectName("partNumberLineEdit")
        self.typeComboBox = QtWidgets.QComboBox(Dialog)
        self.typeComboBox.setGeometry(QtCore.QRect(140, 280, 231, 22))
        self.typeComboBox.setObjectName("typeComboBox")
        self.typeComboBox.addItem("")
        self.partNumberLabel = QtWidgets.QLabel(Dialog)
        self.partNumberLabel.setGeometry(QtCore.QRect(400, 273, 81, 31))
        self.partNumberLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.partNumberLabel.setWordWrap(True)
        self.partNumberLabel.setObjectName("partNumberLabel")
        self.typeLabel = QtWidgets.QLabel(Dialog)
        self.typeLabel.setGeometry(QtCore.QRect(20, 273, 55, 31))
        self.typeLabel.setWordWrap(True)
        self.typeLabel.setObjectName("typeLabel")

        self.fileLocationButton.clicked.connect(self.fileLocationButtonPushed)
        self.createFileButton.clicked.connect(self.createFileButtonPushed)
        self.updateFileButton.clicked.connect(self.updateFileButtonPushed)

        self.vehicleComboBox.activated.connect(self.vehicleComboBoxSelected)
        self.moduleComboBox.activated.connect(self.moduleComboBoxSelected)
        self.hardwareComboBox.activated.connect(self.hardwareComboBoxSelected)
        self.valueComboBox.activated.connect(self.valueComboBoxSelected)
        self.typeComboBox.activated.connect(self.typeComboBoxSelected)

        self.retranslateUi(Dialog)
        self.InitalLoad()
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "ODXF Editor"))
        self.valueLabel.setText(_translate("Dialog", "Value to insert after:"))
        self.vehicleComboBox.setItemText(0, _translate("Dialog", "-- Select Vehicle --"))
        self.aByteFieldLabel.setText(_translate("Dialog", "A-Byte Field:"))
        self.hardwareComboBox.setItemText(0, _translate("Dialog", "-- Select Hardware --"))
        self.valueComboBox.setItemText(0, _translate("Dialog", "-- Select Value --"))
        self.vehicleLabel.setText(_translate("Dialog", "Vehicle Line:"))
        self.createFileButton.setText(_translate("Dialog", "Create File"))
        self.moduleComboBox.setItemText(0, _translate("Dialog", "-- Select Module --"))
        self.fileLabel.setText(_translate("Dialog", "File Name:"))
        self.hardwareLabel.setText(_translate("Dialog", "Hardware:"))
        self.moduleLabel.setText(_translate("Dialog", "Module:"))
        self.updateFileButton.setText(_translate("Dialog", "Update File"))
        self.titleLabel.setText(_translate("Dialog", "ODXF Creator"))
        self.fileLocationLineEdit.setPlaceholderText(_translate("Dialog", "Please Select Folder Location First"))
        self.fileLocationLabel.setText(_translate("Dialog", "ODXF File Location:"))
        self.fileLocationButton.setText(_translate("Dialog", "..."))
        self.hashBinaryTableLabel.setText(_translate("Dialog", "Hash Binary Table:"))
        self.hashValueLabel.setText(_translate("Dialog", "Hash Value:"))
        self.rootHashLabel.setText(_translate("Dialog", "Root Hash:"))
        self.typeComboBox.setItemText(0, _translate("Dialog", "-- Select Type --"))
        self.partNumberLabel.setText(_translate("Dialog", "Part Number:"))
        self.typeLabel.setText(_translate("Dialog", "Type:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
