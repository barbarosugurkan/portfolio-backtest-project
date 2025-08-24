# General Project Plan

As I mentioned, the one of the main aims of this project is to learn data science and use it with practical purposes. Therefore the plan is made for educational purposes and how to apply those learnings to practise as quick as possible.

## Phase 1: Basics of Python and Pandas

In this phase, I will start a pandas course for data analysis. 
The link of the course: [Coursera - Python Data Analysis](https://www.coursera.org/learn/python-data-analysis/)
For the reason why Pandas is chosen please check: [adr folder](adr/)
The main reason why this course is selected is:
- It is short and do not dive deep into Pandas details
- It contains enough information for my project (according to Gemini)
- It had many good comments

This phase is basically about finishing the course and doing some practise on CSV files about data collection with yfinance.

Note: My python knowledge is intermediate so I did not need any python courses.

## Phase 2: Data Storage (SQL)

In this phase, I will start a sql course.
The link of the course: [Coursera - SQL for Data Science](https://www.coursera.org/learn/sql-for-data-science/)
For the reason why SQL is chosen please check: [adr folder](adr/) or [specific document for this selection](database_design.md)
The main reason why this course is selected is:
- It is kind of summary of SQL.
- It contains enough information for my project (according to Gemini)

This phase is basically about finishing the course and then practising learning in a database like Chinook.

## Phase 3: Creating Database and Collecting Data for Project

This is the first part of the project that something is done practically.
Please check any selection for [database_design.md](database_design.md)

1. Make the design of database. Draw an ER Diagram and make an data dictionary.
2. Research platforms for database system (SQLite, PostGRESQL, etc.)
3. Create empty tables.
4. Select how to collect data. 
5. Fill the tables by collecting data, write pyhton scripts for data collection.
6. Create logging system for python scripts and database operations.
6. Data cleaning, cleanse NaN data, make validation rules, missing data handling and standartizationç
7. Test the database by making SQL query in Python.
8. Have a backup of a database, make a recovery strategy.

The extentions that will be done in other phases will be:
- Fill the database with the whole BIST data
- Fill the database with the whole assets that will be used
- Automation for data collection
- Some changes for decisions (for example, if I select sqlite, I might change it to postgresql later, etc.)

## Phase 4: Retrieve Data from SQL and Use it in Score System

- Automation for data collection

To be continued...

## Phase 5: Backtesting

Learn backtester library

To be continued...

## Phase 6: Web Page

Corey Schafer Flask Course (Backend) and The Odin Project (Frontend - HTML/CSS/JS)

To be continued...
