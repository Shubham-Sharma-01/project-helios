# Fixing Python 3.13 Compatibility Issues

You're encountering this error because **SQLAlchemy 2.0.23 doesn't fully support Python 3.13** yet.

## ✅ **Recommended Solution: Use Python 3.11 or 3.12**

This is the cleanest and most reliable fix.

### Option A: Install Python 3.12 via Homebrew

```bash
# Install Python 3.12
brew install python@3.12

# Remove old virtual environment
cd ~/garage-week-project
rm -rf venv

# Create new venv with Python 3.12
python3.12 -m venv venv

# Activate it
source venv/bin/activate

# Verify Python version
python --version
# Should show: Python 3.12.x

# Install dependencies
pip install -r requirements.txt

# Run app
python app.py
```

### Option B: Use pyenv to manage Python versions

```bash
# Install pyenv (if not already installed)
brew install pyenv

# Install Python 3.12
pyenv install 3.12.7

# Set it for this project
cd ~/garage-week-project
pyenv local 3.12.7

# Remove old venv
rm -rf venv

# Create new venv
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run app
python app.py
```

---

## 🔧 Alternative: Quick Workaround (If you must use Python 3.13)

If you can't switch Python versions, try this workaround:

### Step 1: Install without SSL verification (temporary)

```bash
cd ~/garage-week-project
source venv/bin/activate

# Install specific package versions that work better with Python 3.13
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sqlalchemy==2.0.35 greenlet==3.1.1
```

### Step 2: Use the compatibility wrapper

```bash
# Run using the wrapper script instead
python run_app.py
```

---

## ⚠️ Why This Happens

Python 3.13 introduced changes to the `typing` module that break SQLAlchemy 2.0.23. The error:

```
AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'> directly inherits TypingOnly but has additional attributes
```

This is a known incompatibility that will be fixed in future versions of SQLAlchemy.

---

## 🎯 Recommended Path Forward

1. **For this project**: Use Python 3.12 (most stable)
2. **Check your Python version**:
   ```bash
   python3 --version
   python3.12 --version  # If installed
   python3.11 --version  # If installed
   ```
3. **Use the highest version below 3.13**

---

## 📝 Quick Commands Summary

### If you have Python 3.12 installed:
```bash
cd ~/garage-week-project
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### If you only have Python 3.13:
```bash
cd ~/garage-week-project
brew install python@3.12
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## ✅ Verification

After switching Python versions, verify it worked:

```bash
source venv/bin/activate
python --version  # Should show 3.12.x or 3.11.x
python -c "import sqlalchemy; print(sqlalchemy.__version__)"  # Should not error
```

Then run the app:

```bash
python app.py
```

---

## 🆘 Still Having Issues?

If you still get errors:

1. **Make sure you activated the virtual environment**:
   ```bash
   source venv/bin/activate
   # You should see (venv) in your terminal prompt
   ```

2. **Verify you're using the right Python**:
   ```bash
   which python
   # Should show: /Users/shubhams1/garage-week-project/venv/bin/python
   ```

3. **Try completely fresh install**:
   ```bash
   cd ~/garage-week-project
   rm -rf venv
   python3.12 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   python app.py
   ```

---

**Once you switch to Python 3.12, everything should work perfectly!** 🚀

