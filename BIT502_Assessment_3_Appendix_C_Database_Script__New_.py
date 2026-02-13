
# Imports

import sqlite3

# Connect to our database (or create a new one if none exists)

conn = sqlite3.connect("C:/Temp/library_database.db")

cursor = conn.cursor()

# Create the database
cursor.execute('''CREATE TABLE IF NOT EXISTS Memberships (
                    MemberID INTEGER PRIMARY KEY NOT NULL,
                    First_Name TEXT NOT NULL,
                    Last_Name TEXT NOT NULL,
                    Address TEXT NOT NULL,
                    Mobile TEXT NOT NULL,
                    Membership_Plan TEXT NOT NULL,
                    Payment_Plan TEXT NOT NULL,
                    Extra_Book_Rental BOOLEAN NOT NULL,
                    Extra_Private_Area BOOLEAN NOT NULL,
                    Extra_Booklet BOOLEAN NOT NULL,
                    Extra_Ebook_Rental BOOLEAN NOT NULL,
                    Has_Library_Card BOOLEAN NOT NULL,
                    Library_Card_Number TEXT
                    )''')

# Standard insert new member function
def insert_new_member(First_Name, Last_Name, Address, Mobile, Membership_Plan, Payment_Plan, Extra_Book_Rental, Extra_Private_Area, Extra_Booklet, Extra_Ebook_Rental, Has_Library_Card, Library_Card_Number):
    cursor.execute('''INSERT INTO Memberships (First_Name, Last_Name, Address, Mobile, Membership_Plan, Payment_Plan, Extra_Book_Rental, Extra_Private_Area, Extra_Booklet, Extra_Ebook_Rental, Has_Library_Card, Library_Card_Number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (First_Name, Last_Name, Address, Mobile, Membership_Plan, Payment_Plan, Extra_Book_Rental, Extra_Private_Area, Extra_Booklet, Extra_Ebook_Rental, Has_Library_Card, Library_Card_Number))

# Populate the database with some data
insert_new_member("Charlie", "Zavier", "123 Maple Lane", "555 123-4567", "Premium", "Annual", False, True, False, False, True, "39582")
insert_new_member("Scott", "Winters", "456 Oak Street", "555 123-5478", "Regular", "Monthly", True, False, False, True, False, "")
insert_new_member("Jean", "Winters", "456 Oak Street", "555 123-7853", "Premium", "Annual", True, False, False, True, True, "42678")
insert_new_member("Raven", "Whiteholm", "321 Birch Boulevard", "555 124-4127", "Premium", "Monthly", True, False, False, False, True, "23789")
insert_new_member("Logan", "Howl", "654 Cedar Drive", "555 127-8543", "Regular", "Monthly", False, False, True, True, False, "")
insert_new_member("Kurtis", "Vanger", "987 Spruce Way", "555 122-2289", "Regular", "Monthly", False, False, False, False, False, "")
insert_new_member("Peter", "Driver", "246 Elm Court", "555 125-8873", "Kids", "Annual", False, True, True, True, True, "89765")
insert_new_member("Eric", "Lensher", "135 Willow Road", "555 121-2398", "Premium", "Annual", True, True, False, False, True, "33245")
insert_new_member("Nathaniel", "Winters", "456 Oak Street", "555 123-1299", "Kids", "Annual", False, False, True, True, False, "")
insert_new_member("Cassandra", "Starr", "369 Chestnut Place", "555 157-3788", "Premium", "Annual", False, False, True, True, True, "87965")
insert_new_member("Steven", "Rogiers", "77 Manuka Street", "555 223-0985", "Premium", "Monthly", True, False, True, True, False, "")

# Example function to show current members
def show_all_members():
    for row in cursor.execute('''SELECT * FROM Memberships'''):
        print(row)

show_all_members()

# Close the database before exiting
conn.commit()
conn.close()