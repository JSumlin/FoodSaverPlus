# FoodSaverPlus

Project for Software Engineering.
Contributors: Joseph Sumlin, Harsha Palacherla, Yuvraj Goyal, and Mikail Alli

Background:
Originally intended to utilize MySQL and React when submitting this project, but a change in project parameters has shifted our focus to ensuring we implement as much functionality as possible above anything else. Hence, we decided to go for SQLite and possibly drop our React ideas. Perhaps we'll come back afterwards to transfer everything to MySQL and implement React.

Purpose:
A mock web-based marketplace where soon-to-be expired food is posted at a highly discounted rate. Stores sign up and post their food. Customers don't sign up; they place a reservation and pick the item up from the store. Payment is handled at the store.

Utilizies:
Python, Flask, SQLite, SQLAlchemy, HTML/CSS.

TO-DO:

3). Add functionality so that users may add items for sale. (High priority)

4). Fill out meals/ingredients databases. (High priority)

5). Make it so that item postings are properly queried from the database and displayed on the browse page. The soonest expiration date of an item should be displayed. (High priority)

6). Implement reservation functionality. Reservations should reserve items with the soonest expiration date first. (High priority)

7). Fix design problem for html pages (Low priority)

8). Implement meal suggestion functionality (High priority)

9). Implement Google Maps API functionality (Medium priority)

10). Implement Browse filters (Low priority)

11). Make aspects of the pages change based on if a user is signed in (Low priority)

COMPLETED:

1). Store sign up functionality is operational. Google Maps API elements not included.

2). Users may now sign in. Certain pages require you be logged in to access them. Others, namely the login in and signup pages,
redirect users who are logged in to the home page. Logging out redirects you to the login page.