# Imports

import tkinter as tk
from tkinter import ttk
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
root.geometry("600x300")                    # Set window dimensions
root.title("Example program")               # Set title of window


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
            # Update the listbox
            on_entry_change()

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

    # This is something you haven't seen yet, we can create functions INSIDE other functions
    # We can only use these functions while we're in the menu_member_1() function though
    # But this gives us the ability to work with our window and access the variables
    def editwindow_save():
        # We could perform some error checking here to make sure there is a member loaded
        # Get the member data from the global list
        global member_list
        member_data = member_list[member_index_displayed]
        # Insert the new values into the list
        member_data[0] = ent_name_var.get()
        member_data[1] = ent_surname_var.get()
        member_data[2] = ent_address_var.get()
        member_data[3] = ent_mobile_var.get()
        member_data[4] = radio_mtype_var.get()
        member_data[5] = radio_dur_var.get()
        # Since there were other data in the CSV, we only insert what we need
        # The other data will be preserved since we have not touched it

        # Now we just replace the existing member data with the updated
        member_list[member_index_displayed] = member_data

        # Optionally, we can update the other window to show the updated data
        display_member(member_index_displayed)

    def editwindow_cancel():
        memberedit.destroy()

    global member_index_displayed
    global member_list
    if(member_index_displayed is None):
        msgbox.showerror("Warning", "Please select a member first")
        return

    memberedit = tk.Toplevel(root)
    memberedit.geometry("300x370")
    memberedit.title("Edit")

    # Variables
    global radio_mtype_var                  # Due to a quirk with radio buttons
    global radio_dur_var                    # We need to set the variables to global
                                            # Otherwise they will go out of scope and
                                            # cannot be updated correctly
    ent_name_var = tk.StringVar()
    ent_surname_var = tk.StringVar()
    ent_address_var = tk.StringVar()
    ent_mobile_var = tk.StringVar()
    radio_mtype_var = tk.StringVar()
    radio_dur_var = tk.StringVar()

    # Define widgets
    frame_details = ttk.LabelFrame(memberedit, text="Member Details:")
    frame_membership = ttk.LabelFrame(memberedit, text="Membership Type:")
    frame_duration = ttk.LabelFrame(memberedit, text="Membership Duration:")
    frame_actions = ttk.LabelFrame(memberedit, text="Actions:")

    lbl_name = ttk.Label(frame_details, text = "First Name:")
    ent_name = tk.Entry(frame_details, textvariable = ent_name_var, width = 30)
    lbl_surname = ttk.Label(frame_details, text = "Last Name:")
    ent_surname = tk.Entry(frame_details, textvariable = ent_surname_var, width = 30)
    lbl_address = ttk.Label(frame_details, text = "Address:")
    ent_address = tk.Entry(frame_details, textvariable = ent_address_var, width = 30)
    lbl_mobile = ttk.Label(frame_details, text = "Mobile:")
    ent_mobile = tk.Entry(frame_details, textvariable = ent_mobile_var, width = 30)

    radio_mtype_1 = ttk.Radiobutton(frame_membership, text = "Basic", variable = radio_mtype_var, value = "Basic")
    radio_mtype_2 = ttk.Radiobutton(frame_membership, text = "Regular", variable = radio_mtype_var, value = "Regular")
    radio_mtype_3 = ttk.Radiobutton(frame_membership, text = "Premium", variable = radio_mtype_var, value = "Premium")

    radio_dur_1 = ttk.Radiobutton(frame_duration, text = "3 Months", variable = radio_dur_var, value = "3 Months")
    radio_dur_2 = ttk.Radiobutton(frame_duration, text = "12 Months", variable = radio_dur_var, value = "12 Months")
    radio_dur_3 = ttk.Radiobutton(frame_duration, text = "24 Months", variable = radio_dur_var, value = "24 Months")

    btn_save = ttk.Button(frame_actions, text = "Save", command = editwindow_save)
    btn_cancel = ttk.Button(frame_actions, text = "Cancel", command = editwindow_cancel)

    # Position widgets
    memberedit.columnconfigure(0, weight=1)

    # Frames
    frame_details.grid(column=0, row=0, padx= 10, pady = 10, sticky="news")
    frame_membership.grid(column=0, row=1, padx= 10, pady = 10, sticky="news")
    frame_duration.grid(column=0, row=2, padx= 10, pady = 10, sticky="news")
    frame_actions.grid(column=0, row=3, padx= 10, pady = 10, sticky="news")

    # Widgets
    lbl_name.grid(row = 0, column = 0, padx= 5, pady = 5, sticky="w")
    ent_name.grid(row = 0, column = 1, padx= 5, pady = 5, sticky="w")
    lbl_surname.grid(row = 1, column = 0, padx= 5, pady = 5, sticky="w")
    ent_surname.grid(row = 1, column = 1, padx= 5, pady = 5, sticky="w")
    lbl_address.grid(row = 2, column = 0, padx= 5, pady = 5, sticky="w")
    ent_address.grid(row = 2, column = 1, padx= 5, pady = 5, sticky="w")
    lbl_mobile.grid(row = 3, column = 0, padx= 5, pady = 5, sticky="w")
    ent_mobile.grid(row = 3, column = 1, padx= 5, pady = 5, sticky="w")

    radio_mtype_1.grid(row = 0, column = 0, padx= 5, pady = 5, sticky="w")
    radio_mtype_2.grid(row = 0, column = 1, padx= 5, pady = 5, sticky="w")
    radio_mtype_3.grid(row = 0, column = 2, padx= 5, pady = 5, sticky="w")

    radio_dur_1.grid(row = 0, column = 0, padx= 5, pady = 5, sticky="w")
    radio_dur_2.grid(row = 0, column = 1, padx= 5, pady = 5, sticky="w")
    radio_dur_3.grid(row = 0, column = 2, padx= 5, pady = 5, sticky="w")

    btn_save.grid(row = 0, column = 0, padx= 5, pady = 5, sticky="w")
    btn_cancel.grid(row = 0, column = 1, padx= 5, pady = 5, sticky="w")

    # Set the text and options based on the member selected
    member_data = member_list[member_index_displayed]
    # When we're reading from the CSV, sometimes it will add spaces
    # In your CSV file it might be fine but if not, then you'll need to strip the spaces
    ent_name_var.set(member_data[0].strip())
    ent_surname_var.set(member_data[1].strip())
    ent_address_var.set(member_data[2].strip())
    ent_mobile_var.set(member_data[3].strip())
    radio_mtype_var.set(member_data[4].strip())
    radio_dur_var.set(member_data[5].strip())
    

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
# Functions
#---------------

def memberlist_clicked(event):
    global member_index_displayed
    # Get the text that was clicked
    item_clicked = lb_members.curselection()
    # Quick error checking, don't continue if nothing was clicked
    if(lb_members.curselection() == ()):
        return
    item = lb_members.get(item_clicked)
    # Find the member from the member_list
    # NOTE: This program won't support people with the same name, we would need to make some more modifications
    # ...but for simplicity and demonstration we only have unique names
    for i in range(len(member_list)):
        member = member_list[i]
        # Find member that matches the clicked item
        if(member[0] + member[1] == item):
            # Call the display functions
            member_index_displayed = i
            display_member(i)
            break

def on_entry_change(*args):
    # Reset the listbox
    lb_members.delete(0, tk.END)
    # Obtain the text inside the entry box
    current_text = ent_search_var.get()
    # Loop through our membership list
    for item in member_list:
        # If a blank was found in our list skip it, this shouldn't happen but just in case
        if(len(item) < 1):
            continue
        # Check if the current text is found inside the member list name found in the 0 index
        # Convert both to lower text to compare so it is not case-sensitive
        if(current_text.lower() in item[0].lower()):
            # In our listbox, place the membership name item[0] and item[1] to make full name
            full_name = item[0] + "" + item[1]
            lb_members.insert(tk.END, full_name)

def display_member(index):
    if(index is None):
        return
    member_data = member_list[index]
    # Update the widgets to show the member details
    # Sometimes CSV will add whitespace, you can choose to remove this
    lbl_name2.config(text=member_data[0].strip() + " " + member_data[1].strip())
    lbl_address2.config(text=member_data[2].strip())
    lbl_mobile2.config(text=member_data[3].strip())
    lbl_membertype2.config(text=member_data[4].strip())
    lbl_memberduration2.config(text=member_data[5].strip())


#---------------
# Variables
#---------------
# Global variables we will be using in our project go here

data_file = ""                              # The file we open
member_list = []                            # A list of the members, this will be loaded from the csv
                                            # ...and used for viewing and saving

ent_search_var = tk.StringVar()             # Member entry widget variable
member_index_displayed = None               # The member current being displayed


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
member_menu.add_command(label="Edit Member", command=menu_member_1)

#### Help
help_menu.add_command(label="About...", command=menu_help_about)


#---------------
# Main GUI interface
#---------------

#---------------
# Define widgets

frame_search = ttk.LabelFrame(root, text="Member Search:")

frame_member = ttk.LabelFrame(root, text="Member Details")

ent_search = ttk.Entry(frame_search, textvariable = ent_search_var, width = 30)
lb_members = tk.Listbox(frame_search, height = 10, width = 30)

lbl_name = ttk.Label(frame_member, text = "Name:")
lbl_name2 = ttk.Label(frame_member, text = "")
lbl_address = ttk.Label(frame_member, text = "Address:")
lbl_address2 = ttk.Label(frame_member, text = "")
lbl_mobile = ttk.Label(frame_member, text = "Mobile:")
lbl_mobile2 = ttk.Label(frame_member, text = "")
lbl_membertype = ttk.Label(frame_member, text = "Membership:")
lbl_membertype2 = ttk.Label(frame_member, text = "")
lbl_memberduration = ttk.Label(frame_member, text = "Duration:")
lbl_memberduration2 = ttk.Label(frame_member, text = "")


#---------------
# Position widgets

# Configure column 1 to allow expanding to fill the area
root.columnconfigure(1, weight=1)

# Frame search
frame_search.grid(column=0, row=0, padx= 10, pady = 10)

# Member frame display
# Use sticky to allow it to expand to the area available
frame_member.grid(column=1, row=0, padx= 10, pady = 10, sticky="news")

# Widgets inside search frame
ent_search.grid(row = 0, column = 0, padx= 5, pady = 5)
lb_members.grid(row = 1, column = 0, padx= 5, pady = 5)

# Widgets inside display frame
lbl_name.grid(row = 0, column = 0, padx= 5, pady = 5, sticky="w")
lbl_name2.grid(row = 0, column = 1, padx= 5, pady = 5, sticky="w")
lbl_address.grid(row = 1, column = 0, padx= 5, pady = 5, sticky="w")
lbl_address2.grid(row = 1, column = 1, padx= 5, pady = 5, sticky="w")
lbl_mobile.grid(row = 2, column = 0, padx= 5, pady = 5, sticky="w")
lbl_mobile2.grid(row = 2, column = 1, padx= 5, pady = 5, sticky="w")
lbl_membertype.grid(row = 4, column = 0, padx= 5, pady = 5, sticky="w")
lbl_membertype2.grid(row = 4, column = 1, padx= 5, pady = 5, sticky="w")
lbl_memberduration.grid(row = 5, column = 0, padx= 5, pady = 5, sticky="w")
lbl_memberduration2.grid(row = 5, column = 1, padx= 5, pady = 5, sticky="w")

#---------------
# Binding widgets

# Clicking on the listbox
lb_members.bind("<<ListboxSelect>>", memberlist_clicked)
# Entering text into the entry box
ent_search_var.trace("w", on_entry_change)

#---------------
# Tkinter main loop
#---------------

root.mainloop()