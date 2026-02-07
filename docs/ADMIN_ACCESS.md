# Admin Panel Access - VALClean Booking System

## 🔐 Development Credentials

### Default Admin User

**Username:** `admin`  
**Email:** `admin@valclean.uk` or `admin@valclean.local` (if created via seed_data)  
**Password:** `admin123`  
**Role:** `admin`

---

## 🔗 Access Links

| Purpose | URL |
|--------|-----|
| **Django Admin (backend)** | http://localhost:8000/admin/ |
| **Admin Dashboard (frontend)** | http://localhost:3000/ad/dashboard |
| **Frontend login (then go to Dashboard)** | http://localhost:3000/login |

- **Django Admin:** Manage users, orders, appointments, services, etc. directly in the backend. Log in with username `admin` and password `admin123`.
- **Admin Dashboard:** Metrics, recent orders, upcoming appointments, quick actions. Log in at http://localhost:3000/login with the same admin credentials (use **email** + password), then click **Dashboard** in the nav or open http://localhost:3000/ad/dashboard.

---

## 🔄 Restore Superuser Account

If you forgot the admin password or the superuser was lost (e.g. after DB reset):

### Option 1: Reset existing superuser password (recommended)

From the `backend` folder:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python reset_admin_password.py
```

This sets the password to `admin123` for all users that are superuser or staff.

- **Django admin:** Log in with **username** `admin` and password `admin123`.
- **Frontend (Admin Dashboard):** Log in at http://localhost:3000/login with **email** (e.g. `admin@valclean.uk`) and password `admin123`, then go to Dashboard.

### Option 2: Create or update the `admin` user

From the `backend` folder:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python create_superuser.py
```

This creates a user with username `admin`, email `admin@valclean.uk`, password `admin123`, and sets `role=admin`, `is_staff=True`, `is_superuser=True`. If the user already exists, it updates the password and flags.

### Option 3: Seed data (creates admin + sample data)

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py seed_data --settings=config.settings.development
```

Creates admin user `admin@valclean.local` with default password (see seed_data output, often `ChangeMe123!`). Then reset password if needed: `python reset_admin_password.py` (after ensuring that user is superuser) or use `python create_superuser.py` for `admin` / `admin@valclean.uk`.

### Option 4: Django changepassword (if you know the username)

```powershell
python manage.py changepassword admin
```

You will be prompted to enter a new password.

---

## 📋 Admin Panel Features

The Django admin panel allows you to manage:

- **Users & Profiles** - Manage all user accounts, roles, and profiles
- **Managers** - Configure manager permissions and assignments
- **Services & Categories** - Manage service offerings and categories
- **Staff** - Manage staff members, schedules, service areas, and assignments
- **Customers** - View and manage customer accounts and addresses
- **Appointments** - View and manage all appointments and bookings
- **Subscriptions** - Manage recurring service subscriptions
- **Orders** - Manage multi-service orders (including guest orders)
- **Calendar Sync** - View calendar sync settings for users

---

## 🚀 First-Time Access

1. **Start the backend server:**
   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1  # Windows
   python manage.py runserver
   ```

2. **Access admin panel:**
   - Open browser: http://localhost:8000/admin/
   - Login with credentials above

3. **Change password (recommended):**
   - After first login, go to: http://localhost:8000/admin/accounts/user/{your_user_id}/password/
   - Set a secure password for production use

---

## 🔒 Creating Additional Admin Users

### Method 1: Via Django Admin Panel
1. Login to admin panel
2. Go to "Users" section
3. Click "Add user"
4. Fill in username, email, password
5. Set role to "admin"
6. Check "Staff status" and "Superuser status"
7. Save

### Method 2: Via Django Shell
```bash
cd backend
.\venv\Scripts\Activate.ps1
python manage.py shell
```

```python
from apps.accounts.models import User

# Create new admin user
admin = User.objects.create_user(
    username='newadmin',
    email='newadmin@valclean.uk',
    password='secure_password_here',
    role='admin',
    is_staff=True,
    is_superuser=True,
    is_verified=True
)
admin.save()
print(f"Admin user created: {admin.username}")
```

### Method 3: Via Management Command
```bash
cd backend
.\venv\Scripts\Activate.ps1
python manage.py createsuperuser
```

---

## 🔐 User Roles

The system supports four user roles:

1. **Admin** (`admin`) - Full system access
2. **Manager** (`manager`) - Flexible permissions (configured by admin)
3. **Staff** (`staff`) - Staff portal access for job management
4. **Customer** (`customer`) - Customer portal access for bookings

---

## ⚠️ Security Notes

### Development Environment
- Default password is provided for convenience
- Only use default credentials in local development
- Never commit `.env` files with real credentials

### Production Environment
- **Always change the default admin password**
- Use strong, unique passwords
- Enable two-factor authentication (if available)
- Regularly rotate admin passwords
- Limit admin user accounts to necessary personnel only
- Monitor admin panel access logs

---

## 🛠️ Troubleshooting

### Can't Login to Admin Panel

**Issue:** "Please enter a correct username and password"

**Solutions:**
1. Verify you're using the correct credentials:
   - Username: `admin`
   - Password: `admin123`

2. Check if the user exists:
   ```bash
   python manage.py shell
   ```
   ```python
   from apps.accounts.models import User
   admin = User.objects.filter(username='admin').first()
   print(admin)  # Should print the user object
   ```

3. Reset password:
   ```bash
   python manage.py changepassword admin
   ```

4. Create new superuser if needed:
   ```bash
   python manage.py createsuperuser
   ```

### User Exists But Can't Access Admin

**Issue:** User exists but shows "Forbidden" error

**Solutions:**
1. Ensure user has `is_staff=True`:
   ```python
   from apps.accounts.models import User
   admin = User.objects.get(username='admin')
   admin.is_staff = True
   admin.is_superuser = True
   admin.save()
   ```

2. Ensure user role is 'admin':
   ```python
   admin.role = 'admin'
   admin.save()
   ```

---

## 📝 Admin Panel URLs

- **Django Admin (backend):** http://localhost:8000/admin/
- **Admin Dashboard (frontend):** http://localhost:3000/ad/dashboard
- **Frontend login:** http://localhost:3000/login (use admin email + password, then open Dashboard)
- **API Documentation:** http://localhost:8000/api/docs/
- **API Root:** http://localhost:8000/api/
- **API Schema:** http://localhost:8000/api/schema/

---

## 🔗 Related Documentation

- [README.md](README.md) - Main project documentation
- [SETUP_COMPLETE.md](SETUP_COMPLETE.md) - Setup instructions
- [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) - Development roadmap

---

**Last Updated:** Week 1 Day 5 (Database Models Complete)
