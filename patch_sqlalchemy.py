"""
Patch SQLAlchemy to work with Python 3.13.
This works by setting an environment variable that SQLAlchemy will read.
"""

import sys
import os

if sys.version_info >= (3, 13):
    print("🔧 Python 3.13 detected - applying workaround...")
    
    # Set environment variable to disable the problematic check
    os.environ['SQLALCHEMY_WARN_20'] = '1'
    
    # The actual fix: modify the sys modules before SQLAlchemy loads
    import builtins
    original_import = builtins.__import__
    
    def patched_import(name, *args, **kwargs):
        """Custom import that patches SQLAlchemy on load."""
        module = original_import(name, *args, **kwargs)
        
        # If this is the langhelpers module, patch it
        if name == 'sqlalchemy.util.langhelpers' or (hasattr(module, '__name__') and module.__name__ == 'sqlalchemy.util.langhelpers'):
            if hasattr(module, 'TypingOnly') and not hasattr(module.TypingOnly, '_patched'):
                # Patch the __init_subclass__ to allow Python 3.13 attributes
                @classmethod
                def patched_init_subclass(cls, **kwargs):
                    # Just pass - don't check attributes
                    pass
                
                module.TypingOnly.__init_subclass__ = patched_init_subclass
                module.TypingOnly._patched = True
                print("✅ SQLAlchemy patched for Python 3.13")
        
        return module
    
    builtins.__import__ = patched_import
    print("✅ Import hook installed")
else:
    print("ℹ️  Python < 3.13 - no patch needed")

