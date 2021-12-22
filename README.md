# PowerSchool-Merge-Student

## DO NOT RUN THIS WITHOUT A GOOD BACKUP

There is no claim that this will work as intended and may destroy your entire database.

You will need to install the following python packages (pip install...)
python-dotenv
cx_Oracle

For cx_Oracle, you'll need the Oracle instantclient basiclite on your system

You'll need to either use the environment variables listed in .env-default or copy that file to .env and fill in your database details.

### Before merging a student
This does not bring over the current school enrollment for the student to be deleted. You'll need to re-enroll that student with a fake date so the current enrollment gets pushed to the re-enrollments table.
