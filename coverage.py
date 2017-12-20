import unittest
import work_log

from unittest.mock import patch
from playhouse.test_utils import test_database
from peewee import *
from work_log import Entry


test_db = SqliteDatabase(':memory:')


class Tests(unittest.TestCase):
    def create_entry(self):
        Entry.create(
            name='Redha Achour',
            title='Project 4',
            date='2017-12-17',
            time='45',
            notes='work log using database')

    @patch('work_log.search_menu')
    @patch('work_log.add_entry')
    @patch('builtins.input', side_effect=['1', '2', '3'])
    def test_main_menu(self, mock_input, mock_add, mock_search):
        work_log.main_menu()
        self.assertTrue(mock_add.called)
        work_log.main_menu()
        self.assertTrue(mock_search.called)
        with self.assertRaises(SystemExit):
            work_log.main_menu()

    @patch('work_log.main_menu')
    @patch('builtins.input',
           side_effect=['Redha Achour', 'Python', '2017-12-17', '45', '', ''])
    def test_add_entry(self, mock_input, mock_main_menu):
        with test_database(test_db, [Entry]):
            work_log.add_entry()
            entry = Entry.get(Entry.id == 1)
            count = Entry.select().where(
                                (Entry.name == 'Redha Achour') &
                                (Entry.title == 'Python')).count()
            self.assertEqual(entry.name, 'Redha Achour')
            self.assertFalse(entry.notes)
            self.assertTrue(entry.title)
            self.assertEqual(count, 1)
            self.assertTrue(mock_main_menu.called)

    @patch('builtins.input', side_effect=['date', '2017/12/17', '2017-12-17'])
    def test_ask_date(self, mock_input):
        result = work_log.ask_date()
        self.assertEqual(result, '2017-12-17')

    @patch('builtins.input', side_effect=['one', '1', 'int'])
    def test_ask_time(self, mock_input):
        result = work_log.ask_time()
        self.assertEqual(result, '1')

    @patch('work_log.main_menu')
    @patch('work_log.date_search')
    @patch('work_log.term_search')
    @patch('work_log.exact_search')
    @patch('work_log.time_search')
    @patch('work_log.date_rang')
    @patch('builtins.input', side_effect=['1', '2', '3', '4', '5', '6'])
    def test_search_menu(self, mock_input, mock_date_rang, mock_time_search,
                         mock_exact_search, mock_term_search,
                         mock_date_search, mock_main_menu):
        work_log.search_menu()
        self.assertTrue(mock_date_rang.called)
        work_log.search_menu()
        self.assertTrue(mock_time_search.called)
        work_log.search_menu()
        self.assertTrue(mock_exact_search.called)
        work_log.search_menu()
        self.assertTrue(mock_term_search.called)
        work_log.search_menu()
        self.assertTrue(mock_date_search.called)
        work_log.search_menu()
        self.assertTrue(mock_main_menu.called)

    @patch('work_log.display')
    @patch('builtins.input', side_effect=['2017-12-17'])
    def test_date_search(self, mock_input, mock_display):
        with test_database(test_db, [Entry]):
            self.create_entry()
            work_log.date_search()
            self.assertTrue(mock_display.called)

    @patch('work_log.search_menu')
    @patch('work_log.display')
    @patch('builtins.input', side_effect=['2017-12-16', '2017-12-18'])
    def test_date_range(self, mock_input, mock_display, mock_search_menu):
        with test_database(test_db, [Entry]):
            self.create_entry()
            work_log.date_rang()
            self.assertTrue(mock_display.called)
            self.assertFalse(mock_search_menu.called)

    @patch('work_log.search_menu')
    @patch('work_log.display')
    @patch('builtins.input', side_effect=['Redha', 'Redha Achour'])
    def test_exact_search(self, mock_input, mock_display, mock_search_menu):
        with test_database(test_db, [Entry]):
            self.create_entry()
            work_log.exact_search()
            self.assertTrue(mock_display.called)
            self.assertFalse(mock_search_menu.called)

    @patch('work_log.search_menu')
    @patch('work_log.display')
    @patch('builtins.input', side_effect=['database'])
    def test_term_search(self, mock_input, mock_display, mock_search_menu):
        with test_database(test_db, [Entry]):
            self.create_entry()
            work_log.term_search()
            self.assertTrue(mock_display.called)
            self.assertFalse(mock_search_menu.called)

    @patch('work_log.search_menu')
    @patch('work_log.display')
    @patch('builtins.input', side_effect=['45'])
    def test_time_search(self, mock_input, mock_display, mock_search_menu):
        with test_database(test_db, [Entry]):
            self.create_entry()
            work_log.time_search()
            self.assertTrue(mock_display.called)
            self.assertFalse(mock_search_menu.called)

    @patch('work_log.search_menu')
    @patch('work_log.edit')
    @patch('builtins.input', side_effect=['e', 'd', 'b', 'p', 'n'])
    def test_display(self, mock_input, mock_edit, mock_search_menu):
        with test_database(test_db, [Entry]):
            self.create_entry()
            work_log.display(Entry.select())
            self.assertTrue(mock_edit.called)
            self.assertTrue(mock_search_menu.called)

    @patch('builtins.input', side_effect=['1', 'database', ''])
    def test_edit_title(self, mock_input):
        with test_database(test_db, [Entry]):
            self.create_entry()
            entry = Entry.get(Entry.id == 1)
            work_log.edit(entry)
            self.assertEqual(entry.title, 'database')

    @patch('builtins.input', side_effect=['2', '120', ''])
    def test_edit_time(self, mock_input):
        with test_database(test_db, [Entry]):
            self.create_entry()
            entry = Entry.get(Entry.id == 1)
            work_log.edit(entry)
            self.assertEqual(entry.time, '120')

    @patch('builtins.input', side_effect=['3', '2017-12-10', ''])
    def test_edit_date(self, mock_input):
        with test_database(test_db, [Entry]):
            self.create_entry()
            entry = Entry.get(Entry.id == 1)
            work_log.edit(entry)
            self.assertEqual(entry.date, '2017-12-10')

    @patch('builtins.input', side_effect=['4', 'using peewee', ''])
    def test_edit_notes(self, mock_input):
        with test_database(test_db, [Entry]):
            self.create_entry()
            entry = Entry.get(Entry.id == 1)
            work_log.edit(entry)
            self.assertEqual(entry.notes, 'using peewee')


if __name__ == '__main__':
    unittest.main()
