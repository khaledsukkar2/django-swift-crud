#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    
    # Set the default Django settings module for the 'django' command-line utility
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    
    try:
        # Import the function to execute the command-line utility
        # This import is done inside the try block to catch import errors
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Check if 'django' is in the list of imported modules
        if 'django' not in sys.modules:
            # Raise an ImportError with a clear message if Django is not imported
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc
        else:
            # Re-raise the original ImportError if it's not related to Django
            raise

    # Execute the command-line utility with the given arguments
    execute_from_command_line(sys.argv)


# If this script is executed as the main program, run the main function
if __name__ == '__main__':
    main()
