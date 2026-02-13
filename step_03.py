# menu.py

# Imports

import tkinter as tk
from tkinter import messagebox as msgbox
from tkinter import filedialog as fd
import csv

#------------------------------
# Tkinter setup
#------------------------------

#---------------
# Tkinter setup
#---------------
root = tk.Tk()
root.geometry("320x240")                    # Set window dimensions
root.title("Example program")               # Set title of window
root.config(background = "Light Blue")     # Set a background colour


#---------------
# Functions for our menu commands
#---------------
# Remember we need to declare the functions before we use them
# It helps to have a section for them near the top of the file

# NOTE: You can name these how you like but it may help to use a format to make it easy to identify

def menu_file_open():
    # Get the variable data_file and member_list from the global scope
    # We want to be able to use the file throughout the program, so we need to store it in a variable
    global data_file
    global member_list
    # Ask the open a file
    # We can tell which file types we want to allow the user to open
    data_file = fd.askopenfile(filetypes = [("CSV Files", "*.csv"), ("All Files", "*.*")])
    # Check to ensure a file has been selected
    if(data_file is not None):
        # Read the file using the csv reader
        csv_reader = csv.reader(data_file)
        # Only continue if the reader is not empty
        if(csv_reader):
            # Reset the member_list
            member_list = []
            # With the csv file loaded, we need to convert it into a Python list so we can use it in our program
            for row in csv_reader:
                # Loop through the csv_reader and add each row found into our member_list variable
                # This will convert it into a format we can use
                if(len(row) < 1):       # Skip blank rows
                    continue
                member_list.append(row)

def menu_file_save():
    # Get the variable data_file and member_list from the global scope
    global data_file
    global member_list
    # Check if a file has been opened first, for this program the user must open an existing file
    if(not data_file):
        msgbox.showerror(title = "Warning", message = "You must open a file first.")
        return
    file = fd.asksaveasfile(initialfile = data_file.name, defaultextension = ".csv", filetypes = [("CSV Files", "*.csv"), ("All Files", "*.*")])
    # Only proceed if a file was selected
    if(file):
        # Open the file for writing, remember to use the "w" to allow write
        # We will overwrite the file rather than append
        with open(file.name, "w") as new_file:
            # Create a csv writer so we can write to the file using csv
            csv_writer = csv.writer(new_file)
            for row in member_list:
                # Loop through our member_list and write a row for each member
                csv_writer.writerow(row)


def menu_member_1():
    print("Membership > Membership 1")

def menu_help_about():
    # Create a help window, this works similar to our root window
    help = tk.Toplevel(root)
    help.title("Help")
    help.resizable(False, False)            # Prevent the window from being resized
    # Add our widgets
    lbl_help1 = tk.Label(help, text = "About this program\nVersion 1.0\nSuper Gym Memberships")
    btn_ok = tk.Button(help, text = "OK", command = help.quit)
    lbl_help1.grid(row = 0, column = 0)
    btn_ok.grid(row = 1, column = 0)


#---------------
# Variables
#---------------
# Global variables we will be using in our project go here

data_file = ""                              # The file we open
member_list = []                            # A list of the members, this will be loaded from the csv
                                            # ...and used for viewing and saving



#---------------
# Tkinter menu setup
#---------------

menubar = tk.Menu(root)                     # Create a new menubar
root.config(menu=menubar)                   # Attach to the window

#---------------
# Menu options

# Declare the menu options and attach them to the menubar
# tearoff = False will disable the Tkinter feature to detach menus
file_menu = tk.Menu(menubar, tearoff=False)
member_menu = tk.Menu(menubar, tearoff=False)
help_menu = tk.Menu(menubar, tearoff=False)

#---------------
# Add menus to the menu bar

menubar.add_cascade(label="File", menu=file_menu)
menubar.add_cascade(label="Membership", menu=member_menu)
menubar.add_cascade(label="Help", menu=help_menu)

#---------------
# Menu commands
# Add your menu commands to the menu you want them attached to
# The commands will appear in the order added, simply move them around as you'd like

#### File
# Open
file_menu.add_command(label="Open", command=menu_file_open)
# Save
file_menu.add_command(label="Save", command=menu_file_save)
# Add a separator in the menu
file_menu.add_separator()
# Exit will close the program, a special command will tell the window to close
file_menu.add_command(label="Exit", command=root.quit)

#### Membership
member_menu.add_command(label="Option 1", command=menu_member_1)

#### Help
help_menu.add_command(label="About...", command=menu_help_about)


#---------------
# Tkinter main loop
#---------------

root.mainloop()