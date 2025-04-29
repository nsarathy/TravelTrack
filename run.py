import os
import subprocess
import webbrowser
import time

def main():
    # Get directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Step 1: cd into django-backend
    django_backend_dir = os.path.join(script_dir, 'django-backend')
    if os.path.isdir(django_backend_dir):
        os.chdir(django_backend_dir)
        print(f"Changing directory to {django_backend_dir}...")
        
        print("Running makemigrations...")
        subprocess.run(['python', 'manage.py', 'makemigrations'], check=True)

        print("Running migrate...")
        subprocess.run(['python', 'manage.py', 'migrate'], check=True)

        print("Starting Django server...")
        # Start Django server in background
        subprocess.Popen(['python', 'manage.py', 'runserver'], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        print(f"'django-backend' directory not found at {django_backend_dir}")
        return

    # Step 2: cd back to script directory
    os.chdir(script_dir)

    # Step 3: npm run dev
    vue_frontend_dir = os.path.join(script_dir, 'vue-frontend')
    if os.path.isdir(vue_frontend_dir):
        os.chdir(vue_frontend_dir)
        print(f"Changing directory to {vue_frontend_dir}...")
        
        print("Starting Vue frontend server...")
        subprocess.Popen('npm run dev', shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        print(f"'vue-frontend' directory not found at {vue_frontend_dir}")
        return

    # Step 4: Open browser
    time.sleep(3)  # give npm some time to start
    print("Opening browser at http://localhost:5173/...")
    webbrowser.open('http://localhost:5173/')

if __name__ == "__main__":
    main()
