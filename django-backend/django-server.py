import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # <-- Change if your settings module name is different
    from django.core.management import execute_from_command_line

    # Run server without reloader
    execute_from_command_line(['manage.py', 'runserver', '--noreload', '127.0.0.1:8000'])

if __name__ == '__main__':
    main()
