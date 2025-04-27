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

## Usage
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
Back to `TravelTrack/` - `cd ..`
Install node.js if not already installed. 
```
cd vue-frontend
npm install
```
### Usage
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