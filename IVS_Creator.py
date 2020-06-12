


from PyQt5 import QtCore, QtGui, QtWidgets
import os, glob
import xml.etree.ElementTree as ET
import datetime
import json
from functools import partial

path = ""
comments = []
class Ui_Dialog(object):

    def InitalLoad(self):
        with open(r'config.json') as json_file:
            data = json.load(json_file)
            fileLocation = data["ivsPath"]
        if fileLocation != "":
            self.fileLocationLineEdit.setText(fileLocation)
            global path
            path = fileLocation + "\\"
            self.initaliseComboBox()

    def initaliseComboBox(self):
        #List all the vehicle lines that are available
        vehicles = []
        # Walk through the path and get all the main folders
        for x in os.walk(path):
            #Replace the full path with just the vehicle name
            vehicles.append(x[0].replace(path ,""))
        # Add a placeholder 
        vehicles[0] = " -- Select Vehicle --"
        #Clear the combobox and add items
        self.vehicleComboBox.clear()
        self.vehicleComboBox.addItems(vehicles)

    def vehicleComboBoxSelected(self):
        # get the modules available from the vehicle selected
        modules = []
        # Get the vehicle that was selected
        vehicle = self.vehicleComboBox.currentText()
        # Loop through all vehicles in the path
        for x in os.walk(path + vehicle + "\\"):
            # Get the path and split the vehicle line
            for y in x[2]:
                #Add to the modules list
                modules.append(y.split("-")[1])
        # Create a plaehoolder at beginign of list
        modules.insert(0,"-- Select Module --")
        modules.insert(1,"19L310")
        modules.insert(2,"19L320")
        #Remove dupliactes
        modules = list(dict.fromkeys(modules))
        #Clear the combo box and append the modules
        self.moduleComboBox.clear()
        self.moduleComboBox.addItems(modules)

    def moduleComboBoxSelected(self):
        # Get the different hardware models from previous inputs
        hardware = []
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
        
        #Set a placeholder Tag
        hardware.insert(0,"-- Select Hardware --")
        #remove duplicates from list
        hardware = list(dict.fromkeys(hardware))
        #Clear combobox and add new items
        self.hardwareComboBox.clear()
        self.hardwareComboBox.addItems(hardware)

    def hardwareComboBoxSelected(self):
        # Getting all the current valueswith the details enetered from previous boxs
        value = []
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
        
        # Create the placeholder value
        value.insert(0,"-- Select Value --")
        #Remove dupliacte values
        value = list(dict.fromkeys(value))
        # Clear combobox and add values
        self.valueComboBox.clear()
        self.valueComboBox.addItems(value)

    def valueComboBoxSelected(self):
        self.fileLineEdit.setText(self.hardwareComboBox.currentText() + "-" + self.moduleComboBox.currentText() + "-")
    
    def createFileButtonClicked(self):
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
        ET.register_namespace('ivs','platform:/resource/com.avl.ditest.dicore.ivs/model/ivs.xsd')
        
        #Open the previous file and parse through it
        prevFileXML = ET.parse(prevFilePath)
        prevFileRoot = prevFileXML.getroot()

        # If theres a successor in the file then open the successor
        # and set the predecessor value to be the new file
        successor = ""
        if "successorPartNumber" in prevFileRoot.attrib:
            successor = prevFileRoot.attrib["successorPartNumber"]
            successorFilePath = newPath + successor + ".xml"
            successorFileXML = ET.parse(successorFilePath)
            successorFileRoot = successorFileXML.getroot()
            successorFileRoot.set('predecessorPartNumber',newFile.split(".")[0])
            successorFileXML.write(successorFilePath, encoding='utf-8', xml_declaration=True)
        
        #Set the previousfile successor to be the new one
        prevFileRoot.set('successorPartNumber', newFile)
        # Save the previous file
        prevFileXML.write(prevFilePath, encoding='utf-8', xml_declaration=True) 

        #NOW WE USE THE PREVIOUS FILE FOR THE NEW ONE

        # If their is a successor then add the part number to the file
        if successor != "":
            prevFileRoot.set('successorPartNumber', successor)
        else:
            # If not then remove it from the board
            prevFileRoot.attrib.pop('successorPartNumber', None)
        # Set the predecessor value 
        prevFileRoot.set('predecessorPartNumber', prevFile)
        # Set the partnumber created earlier
        prevFileRoot.set('assyPN', newFile)
        # Save the file to the new file path
        prevFileXML.write(newFilePath, encoding='utf-8', xml_declaration=True)
        QtWidgets.QMessageBox.about(None, "Created", "File Created Succesfully")
        
        #Initalise the update area box
        self.initaliseUpdateComboBox()

    def initaliseUpdateComboBox(self):
        # Initalise the values in the combo box

        #Get the value from all the combo boxes
        vehicle = self.vehicleComboBox.currentText()
        module = self.moduleComboBox.currentText()
        hardware = self.hardwareComboBox.currentText()
        newValue = self.fileLineEdit.text()
        newPath = path + vehicle + "\\"
        
        # Gets the xml from the file and parses through it
        newFilePath = newPath + newValue + ".xml"
        tree = ET.parse(newFilePath)
        root = tree.getroot()

        #Initalise the needed variables
        parts = []
        global comments
        counter = 0
        
        #Loop through all elements in root
        for i, x in enumerate(root):
            # Look at their name and check correspondances
            if x.tag == "hardwareComponentPart":
                #If hardware add the details and move on.
                # Nothing more in the hardware node
                parts.append(str(counter) + " Hardware " + x.attrib["filePNPid"])
                comments.append(str(i))
                counter += 1
            if x.tag == "node":
                # Node has all the different software versions and details
                # Loop through all the next hierarchy
                for u, y in enumerate(x):
                    # Append the current branch and continue to move up further.
                    parts.append(str(counter) + " " + y.attrib["partType"] + " " + y.attrib["filePNPid"])
                    comments.append(str(i) + ", " + str(u))
                    counter += 1
                    # Loop through the next hierarchy
                    for o, z in enumerate(y):
                        # The details here may not have part numbers so try except
                        try:
                            # Append to the data list and continue looping through
                            parts.append(str(counter) + " " + y.attrib["partType"] + " " + y.attrib["filePNPid"] + " - " + z.attrib["partType"])
                            comments.append(str(i) + ", " + str(u) + ", " +str(o))
                            counter += 1
                        except Exception as e:
                            pass

        #Add an inital selection on combo box
        parts.insert(0, "-- Select Area --")
        #Clear current values and add new ones
        self.updateAreaComboBox.clear()
        self.updateAreaComboBox.addItems(parts)

    def updateAreaComboBoxSelected(self):
        # Get the values of the combobox. This allows to see where
        # the file needs to be saved.
        vehicle = self.vehicleComboBox.currentText()
        module = self.moduleComboBox.currentText()
        hardware = self.hardwareComboBox.currentText()
        prevValue = self.valueComboBox.currentText()
        newValue = self.fileLineEdit.text()
        newPath = path + vehicle + "\\"
        
        #Find the Path for the newfile which has been created
        newFilePath = newPath + newValue + ".xml"
        #Find the name of the new file 
        newFile = newValue + ".xml"

        # Parse the xml file into the python viewer and get the first root
        newFileXML = ET.parse(newFilePath)
        newFileRoot = newFileXML.getroot()

        # Find the location to be updated from the combo box
        idLoc = self.updateAreaComboBox.currentText().split(" ")[0]
        # Use the location in the comments variable to find location in xml
        values = comments[int(idLoc)].split(", ")
        #Convert to int
        values = list(map(int, values))

        # This looks at the position of the details need updating.
        # The area to be updated will get stored in tempRoot.
        # Needs to be able to access anywhere in the file
        tempRoot = None
        if len(values) == 1:
            tempRoot = newFileRoot[values[0]]
        elif len(values) == 2:
            tempRoot = newFileRoot[values[0]][values[1]]
        elif len(values) == 3:
            tempRoot = newFileRoot[values[0]][values[1]][values[2]]
        elif len(values) == 4:
            tempRoot = newFileRoot[values[0]][values[1]][values[2]][values[3]]
        else:
            #Never should reach here as no nodes go further than 4 hierarchy
            print("?")

        if 'hardware' in tempRoot.tag:
            # Hardware has different tags to everythign else
            temp = tempRoot.attrib['hardwareType'].split("-")
            self.updateFileLineEdit.setText(temp[0] + "-" + temp[1] + "-")
        else:
            # Normal tags
            temp = tempRoot.attrib['filePN'].split("-")
            self.updateFileLineEdit.setText(temp[0] + "-" + temp[1] + "-")
            

        

    def updateFileButtonClicked(self):
        # Get the values of the combobox. This allows to see where
        # the file needs to be saved.
        vehicle = self.vehicleComboBox.currentText()
        module = self.moduleComboBox.currentText()
        hardware = self.hardwareComboBox.currentText()
        prevValue = self.valueComboBox.currentText()
        newValue = self.fileLineEdit.text()
        newPath = path + vehicle + "\\"
        
        #Find the Path for the newfile which has been created
        newFilePath = newPath + newValue + ".xml"
        #Find the name of the new file 
        newFile = newValue + ".xml"

        # Parse the xml file into the python viewer and get the first root
        newFileXML = ET.parse(newFilePath)
        newFileRoot = newFileXML.getroot()

        # Find the location to be updated from the combo box
        idLoc = self.updateAreaComboBox.currentText().split(" ")[0]
        # Use the location in the comments variable to find location in xml
        values = comments[int(idLoc)].split(", ")
        #Convert to int
        values = list(map(int, values))

        # This looks at the position of the details need updating.
        # The area to be updated will get stored in tempRoot.
        # Needs to be able to access anywhere in the file
        tempRoot = None
        if len(values) == 1:
            tempRoot = newFileRoot[values[0]]
        elif len(values) == 2:
            tempRoot = newFileRoot[values[0]][values[1]]
        elif len(values) == 3:
            tempRoot = newFileRoot[values[0]][values[1]][values[2]]
        elif len(values) == 4:
            tempRoot = newFileRoot[values[0]][values[1]][values[2]][values[3]]
        else:
            #Never should reach here as no nodes go further than 4 hierarchy
            print("?")

        # Get the value which needs to be updated at the location
        parts = self.updateFileLineEdit.text().split("-")
        newLocation = ""
        
        #Checks if the value to update to is th efull vbf file or the end digits
        if len(parts) != 1:
            # If more than 1 then use the update file protocol
            newLocation = self.updateFileLineEdit.text()
        else:
            #If 1 get the current part number and replace the end digits
            if 'hardware' in tempRoot.tag:
                # Hardware has different tags to everythign else
                temp = tempRoot.attrib['hardwareType'].split("-")
                newLocation = tempRoot.attrib['hardwareType'].replace(temp[2],self.updateFileLineEdit.text())
            else:
                # Normal tags
                temp = tempRoot.attrib['filePN'].split("-")
                newLocation = tempRoot.attrib['filePN'].replace(temp[2],self.updateFileLineEdit.text())

        # Going to the previous file and putting a successor in for the update
        try:
            # Gets file path of previous file and parses through the xml.
            prevFilePath = glob.glob(newPath + hardware +"*" + module + "*" + prevValue + ".xml")[0]
            prevFileXML = ET.parse(prevFilePath)
            prevFileRoot = prevFileXML.getroot()

            # Finds the correspponding area as last time and stores it in tempPrevRoot
            tempPrevRoot = None
            if len(values) == 1:
                tempPrevRoot = prevFileRoot[values[0]]
            elif len(values) == 2:
                tempPrevRoot = prevFileRoot[values[0]][values[1]]
            elif len(values) == 3:
                tempPrevRoot = prevFileRoot[values[0]][values[1]][values[2]]
            elif len(values) == 4:
                tempPrevRoot = prevFileRoot[values[0]][values[1]][values[2]][values[3]]
            else:
                print("?")
            
            #Set the successor value as the new location
            tempPrevRoot.set('successorPartNumber', newLocation)
            #Save the prevFile back to its file path
            prevFileXML.write(prevFilePath, encoding='utf-8', xml_declaration=True)
            print("Previous File Updated")

        except Exception as e:
            pass
        
        if 'hardware' in tempRoot.tag:
            # In the main file set the predecessor part number as the old file
            tempRoot.set('predecessorPartNumber', tempRoot.attrib['hardwareType'])
            #Update the filePN with the value inserted
            tempRoot.set('hardwareType', newLocation)
        else:
            # Normal Tags to use
            #Update the date
            tempRoot.set('fileDateModified',datetime.datetime.now().strftime('%b-%d-%Y %H:%M:%S'))
            # Update the predecessor
            tempRoot.set('predecessorPartNumber', tempRoot.attrib['filePN'])
            # Update the main file part number
            tempRoot.set('filePN', newLocation)
        
        try:
            #Save the file back 
            newFileXML.write(newFilePath, encoding='utf-8', xml_declaration=True)
            # Output a message saying complete and reset the boxs for next value
            QtWidgets.QMessageBox.about(None, "Updated", "File Updated Succesfully")
            self.updateFileLineEdit.setText("")
            self.updateAreaComboBox.setCurrentIndex(0)
        except Exception as e:
            print(e)
        

    def fileLocationPressed(self):
        #Used for setting the location of the IVS Files
        with open(r'config.json') as json_file:
            data = json.load(json_file)
            fileLocation = data["ivsPath"]
            
        fileLoc = str(QtWidgets.QFileDialog.getExistingDirectory(None, "Select Directory", fileLocation))
        #Stores it in the filelocationLineEdit
        data["ivsPath"] = fileLoc
        
        with open(r'config.json', 'w') as outfile:
            json.dump(data, outfile)

        self.fileLocationLineEdit.setText(fileLoc)
        global path
        path = fileLoc + "\\"
        
        #Initalise the combobox for vehicles
        self.initaliseComboBox()

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
        Dialog.resize(774, 415)
        Dialog.closeEvent = partial(self.closeEvent, Dialog)
        self.valueLabel = QtWidgets.QLabel(Dialog)
        self.valueLabel.setGeometry(QtCore.QRect(410, 140, 71, 41))
        self.valueLabel.setWordWrap(True)
        self.valueLabel.setObjectName("valueLabel")
        self.updateAreaComboBox = QtWidgets.QComboBox(Dialog)
        self.updateAreaComboBox.setGeometry(QtCore.QRect(100, 290, 261, 22))
        self.updateAreaComboBox.setObjectName("updateAreaComboBox")
        self.updateAreaComboBox.addItem("")
        self.vehicleComboBox = QtWidgets.QComboBox(Dialog)
        self.vehicleComboBox.setGeometry(QtCore.QRect(100, 90, 261, 21))
        self.vehicleComboBox.setObjectName("vehicleComboBox")
        self.vehicleComboBox.addItem("")
        self.fileLineEdit = QtWidgets.QLineEdit(Dialog)
        self.fileLineEdit.setGeometry(QtCore.QRect(100, 200, 261, 22))
        self.fileLineEdit.setObjectName("fileLineEdit")
        self.updateFileLabel = QtWidgets.QLabel(Dialog)
        self.updateFileLabel.setGeometry(QtCore.QRect(410, 290, 71, 31))
        self.updateFileLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.updateFileLabel.setWordWrap(True)
        self.updateFileLabel.setObjectName("updateFileLabel")
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
        self.updateFileLineEdit = QtWidgets.QLineEdit(Dialog)
        self.updateFileLineEdit.setGeometry(QtCore.QRect(490, 290, 261, 22))
        self.updateFileLineEdit.setText("")
        self.updateFileLineEdit.setObjectName("updateFileLineEdit")
        self.moduleComboBox = QtWidgets.QComboBox(Dialog)
        self.moduleComboBox.setGeometry(QtCore.QRect(490, 90, 261, 21))
        self.moduleComboBox.setObjectName("moduleComboBox")
        self.moduleComboBox.addItem("")
        self.updateAreaLabel = QtWidgets.QLabel(Dialog)
        self.updateAreaLabel.setGeometry(QtCore.QRect(20, 280, 55, 31))
        self.updateAreaLabel.setWordWrap(True)
        self.updateAreaLabel.setObjectName("updateAreaLabel")
        self.fileLabel = QtWidgets.QLabel(Dialog)
        self.fileLabel.setGeometry(QtCore.QRect(20, 200, 61, 16))
        self.fileLabel.setObjectName("fileLabel")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(20, 240, 731, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.hardwareLabel = QtWidgets.QLabel(Dialog)
        self.hardwareLabel.setGeometry(QtCore.QRect(20, 150, 55, 16))
        self.hardwareLabel.setObjectName("hardwareLabel")
        self.moduleLabel = QtWidgets.QLabel(Dialog)
        self.moduleLabel.setGeometry(QtCore.QRect(410, 90, 55, 16))
        self.moduleLabel.setObjectName("moduleLabel")
        self.updateFileButton = QtWidgets.QPushButton(Dialog)
        self.updateFileButton.setGeometry(QtCore.QRect(20, 340, 731, 28))
        self.updateFileButton.setObjectName("updateFileButton")
        self.titleLabe = QtWidgets.QLabel(Dialog)
        self.titleLabe.setGeometry(QtCore.QRect(20, 10, 731, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.titleLabe.setFont(font)
        self.titleLabe.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabe.setWordWrap(True)
        self.titleLabe.setObjectName("titleLabe")
        self.fileLocationLineEdit = QtWidgets.QLineEdit(Dialog)
        self.fileLocationLineEdit.setGeometry(QtCore.QRect(100, 50, 631, 22))
        self.fileLocationLineEdit.setObjectName("fileLocationLineEdit")
        self.fileLocationLineEdit.setReadOnly(True)
        self.fileLocationLabel = QtWidgets.QLabel(Dialog)
        self.fileLocationLabel.setGeometry(QtCore.QRect(20, 45, 71, 31))
        self.fileLocationLabel.setWordWrap(True)
        self.fileLocationLabel.setObjectName("fileLocationLabel")
        self.fileLocationButton = QtWidgets.QPushButton(Dialog)
        self.fileLocationButton.setGeometry(QtCore.QRect(730, 49, 21, 22))
        self.fileLocationButton.setObjectName("fileLocationButton")
        
        #Activating the Combo Boxes when they are selected
        self.vehicleComboBox.activated.connect(self.vehicleComboBoxSelected)
        self.hardwareComboBox.activated.connect(self.hardwareComboBoxSelected)
        self.moduleComboBox.activated.connect(self.moduleComboBoxSelected)
        self.valueComboBox.activated.connect(self.valueComboBoxSelected)
        self.updateAreaComboBox.activated.connect(self.updateAreaComboBoxSelected)

        #Activating the Buttons on the UI When they are pressed
        self.createFileButton.clicked.connect(self.createFileButtonClicked)
        self.updateFileButton.clicked.connect(self.updateFileButtonClicked)
        self.fileLocationButton.clicked.connect(self.fileLocationPressed)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.InitalLoad()
        

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "IVS Editor"))
        self.valueLabel.setText(_translate("Dialog", "Value to insert after"))
        self.updateAreaComboBox.setItemText(0, _translate("Dialog", "-- Select Area --"))
        self.vehicleComboBox.setItemText(0, _translate("Dialog", "-- Select Vehicle --"))
        self.updateFileLabel.setText(_translate("Dialog", "Update File Name:"))
        self.hardwareComboBox.setItemText(0, _translate("Dialog", "-- Select Hardware --"))
        self.valueComboBox.setItemText(0, _translate("Dialog", "-- Select Value --"))
        self.vehicleLabel.setText(_translate("Dialog", "Vehicle Line"))
        self.createFileButton.setText(_translate("Dialog", "Create File"))
        self.moduleComboBox.setItemText(0, _translate("Dialog", "-- Select Module --"))
        self.updateAreaLabel.setText(_translate("Dialog", "Update Area:"))
        self.fileLabel.setText(_translate("Dialog", "File Name"))
        self.hardwareLabel.setText(_translate("Dialog", "Hardware"))
        self.moduleLabel.setText(_translate("Dialog", "Module"))
        self.updateFileButton.setText(_translate("Dialog", "Update File"))
        self.titleLabe.setText(_translate("Dialog", "IVS Creator"))
        self.fileLocationLineEdit.setPlaceholderText(_translate("Dialog", "Please Select Folder Location First"))
        self.fileLocationLabel.setText(_translate("Dialog", "IVS File Location:"))
        self.fileLocationButton.setText(_translate("Dialog", "..."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
