# University management requirements and SQLite prototype

The original PDF is a requirements document. `university.py` is a new October 2026 implementation of a **subset**, not recovered original code or a full university platform.

Python 3.10+, no external packages:

```sh
python university.py student "Demo Student" demo@example.test
python university.py course SE101 "Software Engineering" 3 30
python university.py register 1 SE101
python university.py grade 1 SE101 3.5
python university.py transcript 1
python university.py backup backup.db
python -m unittest discover -s tests -v
```

Implemented: persistent student records, course definitions, enrollment with transaction-protected capacity checks, grades, credit-weighted transcript GPA and SQLite backups. Grades use a demo 0-4 scale; this is not an implementation of any university's academic regulations.

The PDF's billing, scheduling, instructors, authentication, encryption, permissions, graduation clearance and other requirements remain unimplemented. This local educational CLI has no access control; use fictional data. Database files are excluded from git. SQL is parameterized and foreign-key/check constraints enforce integrity.
