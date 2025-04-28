# TravelTrack

nsarathy CS348 project

Travel Log application

## Framework
Vue + Vite, Django, SQLite, Node.js
- Frontend: vue-frontend/
- Backend: django-backend/
- DB schema: django-backend/api/models.py
- SQLite prepared statements: django-backend/api/views.py
- Django ORM statements: django-backend/api/views.py
- DB indexes: django-backend/api/models.py

## Installation
In command-line
### After downloading code
```
cd TravelTrack
```
### Installing requirements
- Install python if not already installed.
```
cd django-backend
pip install -r requrirements.txt
```
- Back to `TravelTrack/` - `cd ..`
- Install node.js if not already installed. 
```
cd vue-frontend
npm install
```
## Usage
In `TravelTrack/`
```
cd django-backend
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
In another terminal in `TravelTrack/`
```
npm run dev
```
Then go to [localhost:5173](http://localhost:5173/)

## Message for contributers, forkers, and other developers
- Please read LICENSE.md
- If you wish to fork this project or use any of the code for deployment please read through settings.py and any other file that may use placeholders for keys that cannot be public knowledge in case of deployment or production use so change them accordingly when necessary.