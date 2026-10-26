import sqlite3
import unittest
from university import connect,register,transcript
class UniversityTests(unittest.TestCase):
    def setUp(self):
        self.db=connect(':memory:')
        self.db.execute("INSERT INTO students VALUES(1,'Demo','demo@example.test')")
        self.db.execute("INSERT INTO students VALUES(2,'Other','other@example.test')")
        self.db.execute("INSERT INTO courses VALUES('SE','Engineering',3,1)")
        self.db.commit()
    def tearDown(self): self.db.close()
    def test_capacity_and_foreign_keys(self):
        register(self.db,1,'SE')
        with self.assertRaises(ValueError):register(self.db,2,'SE')
        self.assertEqual(len(transcript(self.db,1)['courses']),1)
    def test_transcript_grades(self):
        register(self.db,1,'SE')
        self.assertIsNone(transcript(self.db,1)['gpa'])
        self.db.execute("UPDATE enrollments SET grade=3.5")
        self.assertEqual(transcript(self.db,1)['gpa'],3.5)
        with self.assertRaises(sqlite3.IntegrityError):self.db.execute('UPDATE enrollments SET grade=5')
    def test_unknown_student(self):
        with self.assertRaises(sqlite3.IntegrityError): register(self.db,55,'SE')
        with self.assertRaises(ValueError):transcript(self.db,55)
