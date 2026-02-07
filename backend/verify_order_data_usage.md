# How to Run verify_order_data.py

This script shows what data is saved to the database, what's visible in admin, and delete behavior.

## ✅ Correct Ways to Run

### Option 1: Django Shell (RECOMMENDED)

```powershell
cd backend
.\venv\Scripts\python.exe manage.py shell
```

Then in the shell:
```python
exec(open('verify_order_data.py').read())
show_order_data()
```

### Option 2: Direct Command (Windows PowerShell)

```powershell
cd backend
Get-Content verify_order_data.py | .\venv\Scripts\python.exe manage.py shell
```

### Option 3: As Standalone Script

```powershell
cd backend
.\venv\Scripts\python.exe verify_order_data.py
```

### Option 4: Copy-Paste into Django Shell

1. Open Django shell: `python manage.py shell`
2. Copy the `show_order_data()` function code
3. Paste and run it

---

## ❌ Common Mistakes

- ❌ `python verify_order_data.py` (without venv or Django setup)
- ❌ Running with system Python instead of venv Python
- ❌ Running without Django environment configured

---

## 📋 What the Script Shows

1. **Order Fields Saved to Database** - All fields and values
2. **Order Items** - Services in the order
3. **Appointments** - Linked appointments (if any)
4. **Admin Panel Info** - What you see in admin
5. **Delete Behavior** - What gets deleted and what stays
