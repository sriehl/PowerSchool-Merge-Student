#!/usr/bin/env python3

import cx_Oracle
import os
from dotenv import load_dotenv
load_dotenv()

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_sid = os.getenv("DB_SID")

# Enter both Student Numbers
# be sure to re-enroll the student if you need to keep the current enrollment

primary_student_number = input(" Student Number to KEEP: ")
dupe_student_number = input("Student Number to merge: ")

# primary_student_number =
# dupe_student_number =

class Student:
    def __init__(self, ids):
        self.id = ids[0]
        self.dcid = ids[1]
        self.student_number = ids[2]
        self.lastfirst = ids[3]
        self.enroll_status = ids[4]
        self.entrydate = ids[5]
        self.exitdate = ids[6]
        self.grade_level = ids[7]
        self.state_studentnumber = ids[8]
        self.dob = ids[9]


def print_student(label, student):
    print(f'{label}:')
    print(f'             Name: {student.lastfirst}')
    print(f'              DoB: {student.dob}')
    print(f'    Enroll Status: {student.enroll_status}')
    print(f'  Last Entry/Exit: {student.entrydate} - {student.exitdate}')
    print(f'      Grade Level: {student.grade_level}')
    print(f'         Local ID: {student.student_number}')
    print(f'         State ID: {student.state_studentnumber}')
    print(f'             DCID: {student.dcid}')

    print()


with cx_Oracle.connect(db_user, db_pass, f'{db_host}/{db_sid}', encoding="UTF-8") as connection:
    cursor = connection.cursor()

    # Lookup ids for each student
    student_query = "select id, dcid, cast(student_number as integer) student_number, lastfirst, case enroll_status when 0 then 'ACTIVE' when 2 then 'Transferred Out' when -1 then 'Pre-Registered' when 3 then 'Graduated' when 4 then 'Imported as Historical' else '' end, to_char(entrydate, 'YYYY-MM-DD'), to_char(exitdate, 'YYYY-MM-DD'), grade_level, state_studentnumber, to_char(dob, 'MM/DD/YYYY') from students where student_number = :student_number"
    cursor.execute(student_query, [primary_student_number])
    primary_student = Student(cursor.fetchone())
    cursor.execute(student_query, [dupe_student_number])
    dupe_student = Student(cursor.fetchone())

    print_student('  Primary Student', primary_student)
    print_student('Duplicate Student', dupe_student)

    while (confirm := input("Do you want to merge these students? (Enter y/n) ").lower()) not in {"y", "n"}:
        pass

    if confirm == "n":
        exit()

    # Update Student IDs
    tables = {
        "storedgrades",
        "attendance",
        "studenttestscore",
        "studenttest",
        "reenrollments"
    }
    for table in tables:
        update_sql = f'update {table} set studentid = :primary_student where studentid = :dupe_student'
        cursor.execute(update_sql, [primary_student.id, dupe_student.id])

    # Update Student DCIDs
    tables = {
        "standardgraderollup",
        "standardgraderollupcomment",
        "standardgradesection",
        "standardgradesectioncomment",
        "standardretakescore",
        "standardscore",
        "assignmentdroppedbylowscore",
        "assignmentretakescore",
        "assignmentscore",
        "assignmentscorecomment",
        "assignmentstudentassoc"
    }
    for table in tables:
        update_sql = f'update {table} set studentsdcid = :primary_student where studentsdcid = :dupe_student'
        cursor.execute(update_sql, [primary_student.dcid, dupe_student.dcid])

    # Move FormBuilder Responses
    update_sql = "update u_fb_form_response set student_id = :primary_student where student_id = :dupe_student"
    cursor.execute(update_sql, [primary_student.id, dupe_student.id])

    # Move CC records, need to change student_id and studyear
    update_sql = "update cc set studentid = :primary_student, studyear = studentid || floor(abs(termid/100)) where studentid = :dupe_student"
    cursor.execute(update_sql, [primary_student.id, dupe_student.id])

    # Delete Dupe Student
    delete_sql = "delete from students where dcid = :dupe_student"
    cursor.execute(delete_sql, [dupe_student.dcid])

    delete_sql = "delete from studentrace where studentid = :dupe_student"
    cursor.execute(delete_sql, [dupe_student.id])

    connection.commit()
