#!/usr/bin/env python3

"""GUI for AppImage installer"""

from AppimageController import Controller
import os
import sys
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLineEdit,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QMessageBox)

class InstallerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Main Layout
        self.setWindowTitle("AppImage Installer")
        self.setWindowIcon(QtGui.QIcon('appimage-installer.png'))
        
        # Stack the horizontal boxes vertically.
        generalLayout = QVBoxLayout()
        self.layout1 = QHBoxLayout()
        self.layout2 = QHBoxLayout()
        self.layout3 = QHBoxLayout()
        self.layout4 = QHBoxLayout()
        self.layout5 = QHBoxLayout()
        self.layout6 = QHBoxLayout()
        self.layout7 = QHBoxLayout()
              
        layouts = [self.layout1,
                   self.layout2,
                   self.layout3,
                   self.layout4,
                   self.layout5,
                   self.layout6,
                   self.layout7]
        
        # Generate generalLayout
        for layout in layouts:
            generalLayout.addLayout(layout)
        
        # Set the central widget
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(generalLayout)       
        
        
        # Variables  
        self.file_directory = f"/home/{os.getlogin()}/Downloads"
        # get directory in save file
        self.get_default_directory = Controller.save_file(self, None, 'read')
        
        # Initialize widget layout functions
        self.install_dir_label()
        self.install_dir_text()
        self.install_dir_button()
        self.app_dir_label()
        self.app_dir_selection()
        self.app_dir_button()
        self.selected_app_label()
        self.app_selection_display()
        self.install_button()
        self.dialog_box()
        
            
    # Make first label "Install Directory" - layout1
    def install_dir_label(self):
        firstLabel = QLabel()
        firstLabel.setText("Install Directory")
        firstLabel.setAlignment(Qt.AlignCenter)
        self.layout1.addWidget(firstLabel)
    
    # Set up QLineEdit for install directory path.
    # Added to same row with install_dir_button  - layout 2
    def install_dir_text(self):
        self.installDir = QLineEdit()
        self.installDir.setFixedWidth(600)
        self.installDir.setText(self.get_default_directory)
        self.installDir.setAlignment(Qt.AlignLeft)
        self.layout2.addWidget(self.installDir)
        
        
    # Button to select a different installation directory. layout 2
    def install_dir_button(self):
        installDirButton = QPushButton("Change")
        installDirButton.clicked.connect(self.select_dir_dialog)
        self.layout2.addWidget(installDirButton)
    
    # The label for search area - layout 3
    def app_dir_label(self):
        appLabel = QLabel()
        appLabel.setText("Select AppImage from directory")
        appLabel.setAlignment(Qt.AlignCenter)
        self.layout3.addWidget(appLabel)
    
    # QLineEdit directory path for appimages to be
    # selected for install - layout 4
    # OpenFileNameDialog() sets text to dir when file is selected
    def app_dir_selection(self):
        self.appDir = QLineEdit()
        self.appDir.setFixedWidth(600)
        self.appDir.setText(f"/home/{os.getlogin()}/Downloads")
        self.appDir.setAlignment(Qt.AlignLeft)
        self.layout4.addWidget(self.appDir)
    
    # BUtton to change directory - layout 4
    def app_dir_button(self):
        appsButton = QPushButton("Select")
        appsButton.clicked.connect(self.open_file_dialog)
        self.layout4.addWidget(appsButton)
    
    # Selected app area label - layout 5
    def selected_app_label(self):
        selectedApp = QLabel()
        selectedApp.setText("Selected AppImage")
        selectedApp.setAlignment(Qt.AlignCenter)
        self.layout5.addWidget(selectedApp)
    
    # Display the selected app - layout 6
    def app_selection_display(self):
        self.appSelection = QLineEdit()
        self.appSelection.setFixedWidth(500)
        self.appSelection.setText('None')
        self.appSelection.setReadOnly(True)
        self.appSelection.setAlignment(Qt.AlignCenter)
        self.layout6.addWidget(self.appSelection)
        
    
    # QFileDialog.getExistingDirectory() window
    # Select install directory
    def select_dir_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ShowDirsOnly
        install_directory = QFileDialog.getExistingDirectory(
            self,
            "Select a folder",
            self.get_default_directory,
            options=options)
        
        # Set app_dir_selection() display to selected directory
        if install_directory:
            self.get_default_directory = install_directory
            self.installDir.setText(self.get_default_directory)        
    

    # QFileDialog.getOpenFileName() window    
    # File picker, connected to app_dir_button in layout 4
     # todo: not sure if custom file types can be set, check into it later  
    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        self.file_directory, check = QFileDialog.getOpenFileName(
            self,
            "Select AppImage File",
            self.file_directory,
            "",
            "All Files (*);;AppImage Files (*.appimage)",
            options=options)
        
        # Set app_dir_selection() path to file_directory
        # and set selected_app_display() to file_directory
        if self.file_directory:
            self.appDir.setText(self.file_directory)
            self.appSelection.setText(self.file_directory.split('/')[-1])

    # Pops up to tell the user install is done
    # Also acts as an error dialog in case of wrong directory/file type.        
    def dialog_box(self):
        self.dialog = QMessageBox()
        self.dialog.setWindowTitle("Install Complete")
        self.dialog.setText("Done.")
            
    # the Install button, connects to do_install()
    def install_button(self):
        installButton = QPushButton("Install")
        installButton.setFixedWidth(200)
        installButton.clicked.connect(self.do_install)
        self.layout7.addWidget(installButton)
    
    # Triggers controller.py and sends 6 types of info to controller.py
    def do_install(self):
        
        # Checks if variable information is valid
        # if all checks True, start install sequence
        Controller.verify_variables(
            self,
            self.get_default_directory,     # selected install directory
            self.file_directory,            # current directory of selected ap
            self.installDir.isModified(),   # check if install QLineEdit was manually edited
            self.installDir.text(),         # send in case QLineEdit was modified
            self.appDir.isModified(),       # check if appDir QlineEdit was manually edited
            self.appDir.text()              # send in case QlineEdit was modified
            )             
        
        # Check for errors, if any return True open error dialog
        if Controller.handle_errors(self) != '':
            self.dialog.setText(Controller.handle_errors(self))
            self.dialog.setWindowTitle("Error")
            self.dialog.exec_()
        
        # if no errors, begin the install
        else:
            Controller.get_app_dir_only(self)
        
                            
def main():
    app = QApplication(sys.argv)
    window = InstallerGUI()
    window.show()
    app.exec_()
               
if __name__=='__main__':
    main()
