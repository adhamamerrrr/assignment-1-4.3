"""New executable subset of the university requirements; Python 3.10+, SQLite."""
import argparse
import json
import sqlite3
from pathlib import Path

SCHEMA = '''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS students(
 id INTEGER PRIMARY KEY, name TEXT NOT NULL CHECK(length(trim(name))>0),
 email TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS courses(
 code TEXT PRIMARY KEY, title TEXT NOT NULL,
 credits INTEGER NOT NULL CHECK(credits BETWEEN 1 AND 6),
 capacity INTEGER NOT NULL CHECK(capacity>0));
CREATE TABLE IF NOT EXISTS enrollments(
 student_id INTEGER REFERENCES students(id), course_code TEXT REFERENCES courses(code),
 grade REAL CHECK(grade BETWEEN 0 AND 4), PRIMARY KEY(student_id,course_code));
'''
def connect(path):
    db=sqlite3.connect(path)
    db.row_factory=sqlite3.Row
    db.executescript(SCHEMA)
    return db

def register(db, student_id, course_code):
    # Serialize capacity checks with all writers, not just this process.
    try:
        db.execute('BEGIN IMMEDIATE')
        course=db.execute('SELECT capacity FROM courses WHERE code=?',(course_code,)).fetchone()
        if not course: raise ValueError('Unknown course')
        if db.execute('SELECT count(*) FROM enrollments WHERE course_code=?',(course_code,)).fetchone()[0] >= course[0]:
            raise ValueError('Course is full')
        db.execute('INSERT INTO enrollments(student_id,course_code) VALUES (?,?)',(student_id,course_code))
        db.commit()
    except Exception:
        db.rollback()
        raise

def transcript(db, student_id):
    student=db.execute('SELECT * FROM students WHERE id=?',(student_id,)).fetchone()
    if not student: raise ValueError('Unknown student')
    rows=[dict(r) for r in db.execute('''SELECT c.code,c.title,c.credits,e.grade
        FROM enrollments e JOIN courses c ON c.code=e.course_code
        WHERE e.student_id=? ORDER BY c.code''',(student_id,))]
    completed=[r for r in rows if r['grade'] is not None]
    attempted=sum(r['credits'] for r in completed)
    return {'student':dict(student),'courses':rows,
        'gpa': round(sum(r['grade']*r['credits'] for r in completed)/attempted,3) if attempted else None,
        'graded_credits':attempted}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',default='university.db')
    sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('student');s.add_argument('name');s.add_argument('email')
    s=sub.add_parser('course');s.add_argument('code');s.add_argument('title');s.add_argument('credits',type=int);s.add_argument('capacity',type=int)
    s=sub.add_parser('register');s.add_argument('student_id',type=int);s.add_argument('course_code')
    s=sub.add_parser('grade');s.add_argument('student_id',type=int);s.add_argument('course_code');s.add_argument('grade',type=float)
    s=sub.add_parser('transcript');s.add_argument('student_id',type=int)
    s=sub.add_parser('backup');s.add_argument('destination')
    a=p.parse_args()
    try:
        with connect(a.db) as db:
            if a.command=='student':
                if '@' not in a.email: raise ValueError('Enter an email address')
                row=db.execute('INSERT INTO students(name,email) VALUES (?,?)',(a.name.strip(),a.email.strip()))
                print(json.dumps({'student_id':row.lastrowid}))
            elif a.command=='course':
                db.execute('INSERT INTO courses VALUES (?,?,?,?)',(a.code,a.title,a.credits,a.capacity))
            elif a.command=='register': register(db,a.student_id,a.course_code)
            elif a.command=='grade':
                row=db.execute('UPDATE enrollments SET grade=? WHERE student_id=? AND course_code=?',(a.grade,a.student_id,a.course_code))
                if row.rowcount!=1: raise ValueError('Enrollment not found')
            elif a.command=='transcript': print(json.dumps(transcript(db,a.student_id),indent=2))
            elif a.command=='backup':
                target=Path(a.destination)
                if target.exists(): raise ValueError('Backup destination already exists')
                with sqlite3.connect(target) as backup: db.backup(backup)
    except (ValueError,sqlite3.Error) as e: p.exit(2,f'Error: {e}\n')
if __name__=='__main__': main()
