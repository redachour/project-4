import csv
import os
import re
import sys
import datetime

from peewee import *


db = SqliteDatabase('work_log.db')


# Model for our entry table
class Entry(Model):
    name = CharField(max_length=100)
    title = CharField(max_length=100)
    date = DateField()
    time = IntegerField()
    notes = TextField()
    
    class Meta:
        database = db


# Helper to clean the screen
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# main menu with 3 options
def main_menu():
    clear()
    print('''\n\n\t\tMAIN MENU:\n\n
          1 - Add new entry
          2 - Search for existing entry
          3 - Quit\n\n''')
    while True:
        select = input('Select a number from the previous options >> ')
        if select == '1':
            add_entry()
            break
        elif select == '2':
            search_menu()
            break
        elif select == '3':
            clear()
            sys.exit()
        else:
            print('Please select a number from 1 to 3')


# add entry to csv file
def add_entry():
    clear()
    print("\n\n\t\tADD ENTRY\n\n")
    name = input('Enter a name for the entry >> ')
    title = input('Enter a title for the entry >> ')
    date = ask_date()
    time = ask_time()
    notes = input('\nEnter any notes (optional) >> ')
    Entry.create(name=name, title=title, notes=notes, time=time, date=date)
    input('\n\nThe task was added. Press enter to main menu')
    main_menu()


# Helper to input a date whithout errors
def ask_date():
    while True:
        date = input('\nEnter Date format: YYYY-MM-DD >> ')
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            print('Wrong format, Try again')
        else:
            return date


# Helper to input time spent whithout errors
def ask_time():
    while True:
        time = input('\nEnter the time spent (minutes) >> ')
        try:
            int(time)
        except ValueError:
            print('Wrong format it should be an integer, Try again')
        else:
            return time


# Search menu with 6 options
def search_menu():
    clear()
    print('''\n\n\t\tSEARCH MENU\n\n
        1 - search by rang of dates
        2 - Search by time spent
        3 - Search by employee name
        4 - Search by term
        5 - Search by date
        6 - Return to main menu\n\n''')
    search = None
    while not search:
        search = input('Select a number from the previous options >> ')
        if search == '1':
            date_rang()
        elif search == '2':
            time_search()
        elif search == '3':
            exact_search()
        elif search == '4':
            term_search()
        elif search == '5':
            date_search()
        elif search == '6':
            main_menu()
        else:
            print('Please select a number from 1 to 6')
            search = None


# Helper to display the results if there is any
def run(results):
    if len(results) == 0:
        input('\nNo results found. Press enter for search menu.')
        search_menu()
    else:
        display(results)


# function to filter search by a specific date
def date_search():
    clear()
    entries = Entry.select().order_by(Entry.date.desc())
    dates = []
    print('\nThere is a list of available dates:\n')
    for entry in entries:
        if entry.date not in dates:
            dates.append(entry.date)
            print(entry.date)
    date = ask_date()
    results = entries.where(Entry.date == date)
    run(results)


# filter search by a rang of dates
def date_rang():
    clear()
    while True:
        print('\nEnter rang of dates below in format YYYY-MM-DD\n')
        try:
            date_1 = datetime.datetime.strptime(input('1 st >> '), '%Y-%m-%d')
            date_2 = datetime.datetime.strptime(input('2 nd >> '), '%Y-%m-%d')
        except ValueError:
            print('Wrong format. Try again.')
        else:
            if date_1 > date_2:
                print('First date should be after the second one.')
            else:
                break
    results = Entry.select().where(Entry.date >= date_1.strftime('%Y-%m-%d'),
                                   Entry.date <= date_2.strftime('%Y-%m-%d'))
    run(results)


# filter to search by a specific string
def exact_search():
    clear()
    entries = Entry.select()
    print('\nThere is a list of employee names:\n')
    for entry in entries:
        print(entry.name)
    string = input('\nChoose an employee name >> ')
    search = entries.where(Entry.name.contains(string))
    print('\nThere is a list of possible matches:\n')
    for entry in search:
        print(entry.name)
    name = input('\nEnter excact full name>>')
    result = search.where(Entry.name == name)
    run(result)


# Filter using a term from title or notes
def term_search():
    clear()
    search = input('\nEnter a term to be searched >> ')
    results = Entry.select().where(Entry.title.contains(search) |
                                   Entry.notes.contains(search))
    run(results)


# search filter by the exact time spent
def time_search():
    clear()
    time = ask_time()
    results = Entry.select().where(Entry.time == time)
    run(results)


# display a list of results and providing some options
def display(results):
    index = 1
    while True:
        clear()
        entry = results[index - 1]
        print('''\n\n\t\tYOUR RESULTS\n\n
            Result {} of {}:\n
            Entry title: {}
            Entry name: {}
            Time spent: {}
            Date: {}
            Notes: {}'''.format(index, len(results), entry.title, entry.name,
                                entry.time, entry.date, entry.notes))
        print('\nOptions: {} {} [B]ack, [E]dit, [D]elete\n'.format(
              '[N]ext,' if index < len(results) else "",
              '[P]revious,' if index > 1 else ""))

        selection = input('Enter the first letter of your option >> ').lower()
        if selection == 'e':
            edit(entry)
            break
        elif selection == 'd':
            entry.delete_instance()
            break
        elif selection == 'b':
            break
        elif selection == 'p' and index > 1:
            index -= 1
        elif selection == 'n' and index < len(results):
            index += 1
        else:
            input('Wrong selection. Press enter to try again')
    search_menu()


# Helper to edit a specific entry
def edit(entry):
    edit = []
    field = None
    while not field:
        clear()
        fields = {'1': 'title', '2': 'time', '3': 'date', '4': 'notes'}
        field = input('''\n\tSelect field to edit:\n
            1 - title,
            2 - time,
            3 - date,
            4 - notes.\n\n>> ''')
        if field == '1':
            update = input('\nEnter your update >> ')
            entry.title = update
            entry.save()
        elif field == '2':
            update = ask_time()
            entry.time = update
            entry.save()
        elif field == '3':
            update = ask_date()
            entry.date = update
            entry.save()
        elif field == '4':
            update = input('\nEnter your update >> ')
            entry.notes = update
            entry.save()
        else:
            input('Wrong selection. Press enter to try again')
            field = None

    input('\nEntry edited. Press enter for search menu')


if __name__ == "__main__":
    db.connect()
    db.create_tables([Entry], safe=True)
    main_menu()
