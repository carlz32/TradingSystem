import os
import sys

# Determine the base directory for data storage
if getattr(sys, 'frozen', False):
    # If packaged as an app, use the user's Documents/MonteCarloRS folder
    BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "MonteCarloRS")
else:
    # If running as script, use the project root directory (parent of mcdesk)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ensure the directory exists
if not os.path.exists(BASE_DIR):
    try:
        os.makedirs(BASE_DIR)
    except OSError:
        pass

DATA_FILE = os.path.join(BASE_DIR, "rr_history.json")
