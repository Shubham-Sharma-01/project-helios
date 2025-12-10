# 🚀 Quick Start - macOS (3 Minutes)

Run the DevOps Command Center on your Mac in 3 minutes.

---

## ⚠️ **Important: Python Version**

This app requires **Python 3.11 or 3.12** (NOT 3.13 yet).

### Check your Python version:
```bash
python3 --version
```

If you have **Python 3.13**, please see [PYTHON313_FIX.md](PYTHON313_FIX.md) for instructions on installing Python 3.12.

---

## Step 1: Open Terminal

Press `Cmd + Space`, type "Terminal", press Enter.

---

## Step 2: Navigate to Project

```bash
cd ~/garage-week-project
```

---

## Step 3: Create Virtual Environment

**If you have Python 3.12:**
```bash
python3.12 -m venv venv
source venv/bin/activate
```

**If you have Python 3.11:**
```bash
python3.11 -m venv venv
source venv/bin/activate
```

**If you have Python 3.10 or older:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

Wait ~2 minutes for installation to complete.

---

## Step 5: Run the App

```bash
python app.py
```

The app will open automatically! 🎉

---

## First Time Setup

### 1. Create Account
- Click "Sign up"
- Enter email & password
- Click "Sign Up"

### 2. Sign In
- Enter your credentials
- Click "Sign In"

### 3. Create a Task
- Click "My Tasks" in sidebar
- Click "➕ New Task"
- Fill in details
- Click "Create"

---

## Next Time

```bash
# 1. Open terminal
# 2. Navigate to project
cd ~/garage-week-project

# 3. Activate virtual environment
source venv/bin/activate

# 4. Run app
python app.py
```

---

## Stop the App

Press `Cmd + C` in the terminal.

---

## Need Help?

See [SETUP_MAC.md](SETUP_MAC.md) for detailed guide.

---

**That's it! You're ready to go!** 🚀

