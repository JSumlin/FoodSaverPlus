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

4). Fill out meals/ingredients databases. (Medium priority)

6). Implement reservation functionality. Reservations should reserve items with the soonest expiration date first. (High priority)

7). Fix design problems for html pages (Low priority)

9). Implement Google Maps API functionality (Medium priority)

10). Implement Browse filters (Low priority)

12). Implement ability for users to upload images for their items. (Medium Priority)

13). Clean up, comment, and refactor code. (Low priority for now. Functionality is most important at the moment.)

COMPLETED:

1). Store sign up functionality is operational. Google Maps API elements not included.

2/11). Users may now sign in. Certain pages require you be logged in to access them. Others, namely the login in and signup pages,
redirect users who are logged in to the home page. Logging out redirects you to the login page.

3). Users may now add items to their account and post them for sale.

5). Postings and meals are accurately represented from the database on their respective pages. The earliest expiration date
for an item at a given price point is shown. If the same item is posted at different prices, they will be listed
separately.

8). Meal suggestion page is function (excluding filters).