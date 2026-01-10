# 🚀 Server Management Scripts

## ✅ Scripts Created

Two PowerShell scripts have been created in the project root to easily start and stop both servers:

### 1. `start-dev.ps1` - Start Both Servers
- Starts backend (Django) server on port 8000
- Starts frontend (Next.js) server on port 3000
- Opens two separate PowerShell windows (one for each server)
- Checks if servers are already running and stops them first
- Checks if virtual environment and node_modules exist
- Installs frontend dependencies if missing

### 2. `stop-dev.ps1` - Stop Both Servers
- Stops backend server on port 8000
- Stops frontend server on port 3000
- Stops any Python/Django processes
- Stops any Node/Next.js processes
- Safe to run multiple times (checks if servers are running)

---

## 📋 Usage

### Start Both Servers:
```powershell
.\start-dev.ps1
```

This will:
1. Check if servers are already running and stop them
2. Open a PowerShell window for backend (http://localhost:8000)
3. Wait 3 seconds
4. Open a PowerShell window for frontend (http://localhost:3000)
5. Display all URLs and information

### Stop Both Servers:
```powershell
.\stop-dev.ps1
```

This will:
1. Stop backend server on port 8000
2. Stop frontend server on port 3000
3. Stop any related processes
4. Confirm completion

---

## ✅ Features

### `start-dev.ps1` Features:
- ✅ **Path detection** - Automatically detects project root directory
- ✅ **Pre-checks** - Verifies backend and frontend directories exist
- ✅ **Virtual environment check** - Verifies venv exists before starting
- ✅ **Node modules check** - Verifies node_modules exists (installs if missing)
- ✅ **Port conflict handling** - Stops existing servers on ports 8000 and 3000
- ✅ **Separate windows** - Opens each server in its own PowerShell window
- ✅ **Visual feedback** - Shows progress and URLs for each server
- ✅ **Error handling** - Exits with error messages if directories/files are missing

### `stop-dev.ps1` Features:
- ✅ **Port-based stopping** - Stops servers on ports 8000 and 3000
- ✅ **Process-based stopping** - Stops Python and Node processes
- ✅ **Safe execution** - Can be run multiple times safely
- ✅ **Visual feedback** - Shows what was stopped
- ✅ **Error handling** - Handles errors gracefully

---

## 🎯 Quick Start

**Every time you need to start development servers:**

1. Open PowerShell in project root (`D:\VALClean`)
2. Run: `.\start-dev.ps1`
3. Two PowerShell windows will open - one for backend, one for frontend
4. Servers will start automatically

**To stop servers:**

1. Press `Ctrl+C` in each server window, OR
2. Run: `.\stop-dev.ps1`

---

## 📝 Example Output

### Starting Servers:
```
========================================
  VALClean Booking System
  Starting Development Servers
========================================

Starting Backend Server (Django)...
URL: http://localhost:8000
API: http://localhost:8000/api/
Docs: http://localhost:8000/api/docs/
Admin: http://localhost:8000/admin/

Starting Frontend Server (Next.js)...
URL: http://localhost:3000

========================================
  Servers Starting...
========================================

Backend:  http://localhost:8000
Frontend: http://localhost:3000

Two PowerShell windows will open:
  1. Backend server (Django)
  2. Frontend server (Next.js)

✅ Servers are starting in separate windows...
```

### Stopping Servers:
```
========================================
  VALClean Booking System
  Stopping Development Servers
========================================

Checking Backend Server (port 8000)...
✅ Backend server stopped (port 8000)

Checking Frontend Server (port 3000)...
✅ Frontend server stopped (port 3000)

✅ Servers stopped successfully!
```

---

## ⚙️ Configuration

The scripts use these paths (automatically detected):
- **Project Root:** Where `start-dev.ps1` is located
- **Backend:** `{project_root}/backend/`
- **Frontend:** `{project_root}/frontend/`
- **Virtual Environment:** `{project_root}/backend/venv/`

The scripts automatically detect the correct paths, so they work from any location as long as you run them from the project root.

---

## ✅ Status

**Scripts Created:**
- ✅ `start-dev.ps1` - Start both servers (118 lines)
- ✅ `stop-dev.ps1` - Stop both servers (93 lines)

**Ready to Use:**
- ✅ Both scripts are fully functional
- ✅ All servers have been stopped
- ✅ Scripts are ready to use immediately

---

## 🎉 Usage from Now On

**Always use these scripts to start/stop servers:**

```powershell
# Start servers
.\start-dev.ps1

# Stop servers
.\stop-dev.ps1
```

No need to manually navigate to directories or activate virtual environments - the scripts handle everything!
