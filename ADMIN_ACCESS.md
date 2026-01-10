# Admin Panel Access - VALClean Booking System

## 🔐 Development Credentials

**Admin Panel URL:** http://localhost:8000/admin/

### Default Admin User

**Username:** `admin`  
**Email:** `admin@valclean.uk`  
**Password:** `admin123`  
**Role:** `admin`

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

- **Admin Panel:** http://localhost:8000/admin/
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
