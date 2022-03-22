#!/usr/bin/env python3

import os
import re
import stat
import shutil
import subprocess


class Controller:
    def __init__(self):
        
        #self.PROGRAM_DIR = os.path.dirname(os.path.realpath('AppimageController.py'))
        # Methods
        self.save_file()            # A file to store user default install directory
        self.verify_variables()     # verify user set variables
        self.handle_errors()        # handle any errors that verify_variables() reports
        self.get_app_dir_only()     # get the application dir without the apps name
        self.get_app_title()        # get the app name in a neat title form
        self.extract_app()          # extract the appimage for icon and .desktop file
        self.find_app_icon()        # find the appropriate icon from squashfs-root
        self.get_desktop_file()     # find and edit the .desktop file
        self.move_appimage()        # move the appimage to its install directory

               
    # takes variables from do_install(self) in appinstaller-gui    
    # sorts and verifies paths, gets app name
    # this section should probably be split/restructured
    def verify_variables(
            self, 
            install_dir,
            app_dir,
            install_dir_mod,
            get_installDir_text,
            app_dir_mod, 
            get_appDir_text
            ):   #:)
            
              # get the directory of the program
            self.install_dir = install_dir             
            self.app_dir = app_dir                     
            self.install_dir_mod = install_dir_mod     
            self.installDir_text = get_installDir_text
            self.app_dir_mod = app_dir_mod
            self.appDir_text = get_appDir_text           
            self.app_name = ''      # Will get this from self.app_dir
            self.app_title = ''     # will get this from self.app_name,app title
            self.app_dir_only = ''  # get the apps directory without app name included
            self.icon_name = ''     # name of appimage icon
            
            # check if QLineEdits have been modified,
            # if so set the values
            if self.app_dir_mod:
                self.app_dir = self.appDir_text
            if self.install_dir_mod:
                self.install_dir = self.installDir_text
                
            # check if app_dir directory is False
            if os.path.exists(self.app_dir) == False:
                self.app_dir = False                           
            # get the app_name from app_dir
            elif self.app_dir != False:
                if self.app_dir.split('/')[-1].lower().endswith('.appimage'):
                    self.app_name = app_dir.split('/')[-1]
                    # split the appimage from directory
                    
                else:
                    self.app_name = False
                
            # check install directory exists
            # if install directory is different from the one in save file, save it.
            if os.path.exists(self.install_dir):
                if self.install_dir != Controller.save_file(self, self.install_dir, 'read'):
                    Controller.save_file(self, self.install_dir, 'write')
            else:
                self.install_dir = False
                
                
    # deals with saving/writing the install directory to file
    # to be loaded next time program is opened.
    def save_file(self, directory_name, read_or_write):   
        
        os.chdir(self.PROGRAM_DIR)
        
        try:
            if read_or_write == 'read':
                with open(f'{self.PROGRAM_DIR}/default.txt', 'r') as text_file:
                    _line = text_file.readline()
                    text_file.close()
                    return _line
        except FileNotFoundError:
            with open(f'{self.PROGRAM_DIR}/default.txt', 'w') as text_file:
                text_file.write(f"/home/{os.getlogin()}/Applications")
                text_file.close()
                return f"/home/{os.getlogin()}/Applications"
        else:
            with open(f'{self.PROGRAM_DIR}/default.txt', 'w') as text_file:
                text_file.write(directory_name)
                text_file.close()
    
                
    
    # Deal with errors if any of the directories/file is = False
    def handle_errors(self):
        error_dict = {self.app_dir:'Selected AppImage directory invalid.',
                      self.app_name: 'Select a valid AppImage file.',
                      self.install_dir: 'Install directory invalid'
                      }
        error_list = []
        error_string = ''
        
        # gather any errors(False) values and append to list
        for key,value in error_dict.items():
            if key == False:
                error_list.append(value)
        
        # Put errors into a readable form, to be displayed in error_msg()       
        if error_list != []:
            for item in error_list:
                error_string += ('ERROR: ' + item + "\n")
        
        return error_string
    
    
    # remove appimage name from the application directory
    def get_app_dir_only(self):
        self.app_dir_only = self.app_dir.split('/')[:-1]
        self.app_dir_only = '/'.join(self.app_dir_only)
    
        Controller.get_app_title(self)
        
        
    # Use re to get the name of the app without version numbers, extra spaces, or extension.
    def get_app_title(self):
        self.app_name_regex = re.compile(r'\D+[-|_]')
        self.app_title = self.app_name_regex.match(self.app_name).group()
        self.app_title = re.split('-|_', self.app_title)
        self.app_title = ' '.join(self.app_title).lower().strip()
           
        Controller.make_icon_directory(self)
    
        
    # make directory for icon to go to.
    def make_icon_directory(self):
        PATH = f"/home/{os.getlogin()}/.local/share/applications"
        if os.path.exists(PATH):
            os.chdir(PATH)
            if os.path.exists('appimage-icons') == False:
                os.mkdir('appimage-icons')
        
        Controller.extract_app(self)
    
    
    # extract the appimage using terminal command, used to find icon
    # go ahead and make it executable as well
    def extract_app(self):
        os.chdir(self.app_dir_only)
        os.chmod(self.app_name, 0o755)
        with open(f"{self.PROGRAM_DIR}/output.txt", 'w') as out:
            subprocess.run([f"{self.app_dir}", "--appimage-extract"], stdout=out)
        out.close()
            
        Controller.find_app_icon(self)
        
        
    # use regex to find list of probable icons   
    def find_app_icon(self):
        self.icon_name_regex = re.compile(r'(.*png$)|(.*svg$)|(.*jpg$)|(.*jpeg$)')
        icon_match_list = []
        
        if os.path.exists("squashfs-root"):
            os.chdir("squashfs-root")
            for icon in os.listdir():
                if self.icon_name_regex.match(icon):
                    icon_match_list.append(icon)
        
        # Sometimes 'squashfs-root' folder is found in home directory
        #  instead of the current location of app. So search there if icon
        #  list is empty.
        elif icon_match_list == []:
            if os.path.exists(f"/home/{os.getlogin()}/squashfs-root"):
                os.chdir(f"/home/{os.getlogin()}/squashfs-root")
                for icon in os.listdir():
                    if self.icon_name_regex.match(icon):
                        icon_match_list.append(icon)
        
        # split title name for iterations
        # match up icon name to app title name
        title_list = self.app_title.split(' ')             
        # match up icon to appname
        for icon in icon_match_list:
            for name in title_list:
                if name.lower() in icon.lower():
                    self.icon_name = icon
        
        # return the cwd and icon
        shutil.copy(os.getcwd() + f"/{self.icon_name}", 
                    f"/home/{os.getlogin()}/.local/share/applications/appimage-icons")

        
        # next method
        Controller.get_desktop_file(self, title_list)


    def get_desktop_file(self, title_list):
        # find the right .desktop file if it exists
        ICON_HOME_DIR = f"/home/{os.getlogin()}/.local/share/applications/appimage-icons"
        DESKTOP_FILE_DIR = f"/home/{os.getlogin()}/.local/share/applications"
        desktop_file = ''
        
        # match appimage name to its <appname>.desktop file
        for files in os.listdir():
            if files.endswith(".desktop"):
                for name in title_list:
                    if name.lower() in files.lower():
                        desktop_file = files
        
        # get text from desktop file
        read_file = open(desktop_file, 'r')
        _lines = read_file.readlines()
        read_file.close()
    
        
        # set executable and icon path
        for index, line in enumerate(_lines):
            if "Exec=" in line:
                _lines[index] = f"Exec={self.install_dir}/{self.app_name}\n"
            if "Icon=" in line:
                _lines[index] = f"Icon={ICON_HOME_DIR}/{self.icon_name}\n"
        
        # write the lines back into the file.
        write_file = open(desktop_file, 'w')
        write_file.writelines(_lines)
        write_file.close()
        
        # move file to ~/.local/share/applications
        shutil.copy(os.getcwd() + f"/{desktop_file}", DESKTOP_FILE_DIR)
    
        Controller.move_appimage(self)
    
    
    # move the appimage to its directory
    def move_appimage(self):
        os.chdir(self.app_dir_only)     
        # move the appimage
        shutil.copy(self.app_name, self.install_dir)
        
        self.dialog.exec_()
        
        
def main():
    Controller
    
if __name__=='__main__':
    main()
