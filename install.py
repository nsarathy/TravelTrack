import os
import subprocess

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Step 1: cd into django-backend and install Python requirements
    django_backend_dir = os.path.join(script_dir, 'django-backend')
    if os.path.isdir(django_backend_dir):
        os.chdir(django_backend_dir)
        print(f"Installing Python requirements in {django_backend_dir}...")
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True, shell=True)
    else:
        print(f"'django-backend' directory not found at {django_backend_dir}")
        return

    # Step 2: cd back to parent (script_dir)
    os.chdir(script_dir)

    # Step 3: cd into vue-frontend and run npm install
    vue_frontend_dir = os.path.join(script_dir, 'vue-frontend')
    if os.path.isdir(vue_frontend_dir):
        os.chdir(vue_frontend_dir)
        print(f"Installing npm packages in {vue_frontend_dir}...")
        subprocess.run(['npm', 'install'], check=True, shell=True)
    else:
        print(f"'vue-frontend' directory not found at {vue_frontend_dir}")
        return

if __name__ == "__main__":
    main()
