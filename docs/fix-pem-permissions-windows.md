# Fix .pem key permissions on Windows (SSH "bad permissions")

SSH refuses to use a private key if other users can read it. On Windows you must remove inherited permissions and allow only your user to read the file.

## Option 1: PowerShell (run in PowerShell as your user)

Replace `D:\ValClean.pem` with the full path to your `.pem` file.

```powershell
# Remove inheritance and all existing permissions
$path = "D:\ValClean.pem"
$acl = Get-Acl $path
$acl.SetAccessRuleProtection($true, $false)  # disable inheritance, don't copy parent rules
$acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) | Out-Null }

# Grant only the current user Full Control
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule($user, "FullControl", "Allow")
$acl.AddAccessRule($rule)
Set-Acl $path $acl

# Verify: only your user should have access
Get-Acl $path | Format-List
```

Then try SSH again:

```powershell
ssh -i D:\ValClean.pem ubuntu@13.135.109.229
```

## Option 2: GUI (Properties → Security)

1. Right-click **ValClean.pem** → **Properties** → **Security** tab.
2. **Advanced** → **Disable inheritance** → choose **Remove all inherited permissions**.
3. **Add** → **Select a principal** → type your Windows username → **Check names** → OK.
4. Grant **Read** (and **Read & execute** if listed). OK.
5. Remove any other principals (e.g. "Authenticated Users") so only **your user** remains.
6. **Apply** → OK.

## If you still see "Authenticated Users"

- In **Security** → **Advanced** → **Change** next to owner: set owner to your user, then apply.
- Remove the "Authenticated Users" entry; keep only your account and (if present) SYSTEM.

After fixing, run:

```powershell
ssh -i D:\ValClean.pem ubuntu@13.135.109.229
```
