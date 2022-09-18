# pantry-app
Pantry: your grocery managing app, built for Hack the North 2022.

## What it does
Pantry is an all-in-one solution for managing the items in your pantry, from buying to eating. 
Pantry will ensure you never have to ask yourself, *Do we have milk at home? How old is our 
bread? Do we have enough pasta?* Pantry provides an easy interface for making grocery lists, 
managing pantry items, and tracking grocery spending habits. It will help you cut down on food 
waste in no time!

## How it's built
Pantry is built using Flask and sqlite3 for the backend and HTML and CSS with Bootstrap and jQuery 
for the frontend. 

## How to run it
1. Install the `requirements.txt` python packages.
2. Go into the src directory.
3. Run `flask --app pantry-app init-db`.
4. Run `flask --app pantry-app run`.

## Inspiration
I have a problem with managing expired foods. Many times over, I have disappointedly pulled jars 
from my pantry that turned out to be *a few years* too old or grabbed cheese that was a *little bit* 
greener than it should be. It haunts my dreams. So, I decided to build a solution: an app that can
track my food for me. 

## Challenges
This was my first time making a complete web application from scratch, which was an interesting challenge,
especially as a solo developer. I usually struggle with finding a good starting place for a project, 
so I tried to not overthink anything and just start programming. Sometimes I would not understand why a 
particular CSS property was not working as I thought it should, especially in combination with Bootstrap.

## What I learned
I learned how to store user data, design the front end, and create a cohesive user experience. I was 
able to get a small slice of fullstack development through this project.

## What's next for Pantry
Right now, Pantry requires all information to be manually inputted, which takes away from the convenience
of it. But, it would be a lot better if we could use a camera to scan some information directly from the 
receipt. Sending notifications to alert people when something is going bad in advanced would be a helpful
feature, and having a dedicated mobile app.

## Credits
- [Groceries icons created by Freepik - Flaticon](https://www.flaticon.com/free-icons/groceries)