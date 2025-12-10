"""
Wrapper script to run the app with Python 3.13 compatibility fixes.
Use this instead of running app.py directly if you have Python 3.13.
"""

import sys

# Apply Python 3.13 fixes before importing anything else
if sys.version_info >= (3, 13):
    print("🔧 Applying Python 3.13 compatibility fixes...")
    import fix_python313
    fix_python313.apply_fix()

# Now import and run the app
print("🚀 Starting DevOps Command Center...")
import app

# The app will run via flet.app() in the app module

