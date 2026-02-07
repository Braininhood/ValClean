# Deploy frontend to EC2 without building on the server

Building Next.js on a small EC2 instance can take **15+ minutes**. This doc describes how to **build once in GitHub Actions** and **deploy the result** to EC2 so the server only runs `node server.js` (no `npm run build`).

## How it works

1. **GitHub Actions** (on every push to `main` that touches `frontend/`) runs `npm ci` and `npm run build:webpack` on a fast runner and produces a **standalone** bundle.
2. The workflow uploads the **frontend-standalone** artifact (contains `server.js`, `.next/static`, `public`, and traced dependencies).
3. On **EC2** you download the artifact, extract it, and run `node server.js`. No Node/npm build step on the server.

## One-time setup on EC2

1. Install Node (only needed to **run** the standalone server, not to build):
   ```bash
   sudo apt update && sudo apt install -y nodejs
   node -v   # v18+ is enough
   ```
2. Create a directory for the frontend deploy:
   ```bash
   sudo mkdir -p /var/www/VALClean-frontend
   sudo chown ubuntu:ubuntu /var/www/VALClean-frontend
   ```

## Deploy (after each frontend change)

### Option A: Download artifact from GitHub Actions (manual)

1. Open **GitHub** → your repo → **Actions** → latest **Build Frontend** run.
2. Under **Artifacts**, download **frontend-standalone**.
3. On EC2:
   ```bash
   cd /var/www/VALClean-frontend
   # Upload the zip you downloaded (e.g. with scp from your machine):
   # scp frontend-standalone.zip ubuntu@YOUR_EC2_IP:/var/www/VALClean-frontend/
   unzip -o frontend-standalone.zip -d .
   # Artifact contents are the standalone root (server.js, .next/, node_modules/). Run:
   PORT=3000 HOSTNAME=0.0.0.0 node server.js
   ```
   Or use a process manager (systemd) to run `node server.js` and restart on reboot.

### Option B: Still build on EC2 (slower)

If you prefer to keep building on the server:

```bash
cd /var/www/VALClean/frontend
git pull
npm ci
npm run build:webpack
# Run standalone server (no npm start):
cp -r public .next/standalone/ 2>/dev/null || true
cp -r .next/static .next/standalone/.next/ 2>/dev/null || true
cd .next/standalone
PORT=3000 HOSTNAME=0.0.0.0 node server.js
```

Use **Option A** to avoid long build times on small instances.

## Run standalone server with systemd

Create `/etc/systemd/system/valclean-frontend.service`:

```ini
[Unit]
Description=VALClean Next.js (standalone)
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/VALClean-frontend
Environment=PORT=3000
Environment=HOSTNAME=0.0.0.0
ExecStart=/usr/bin/node server.js
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable valclean-frontend
sudo systemctl start valclean-frontend
```

## Environment variables

Standalone server reads **runtime** env vars. Set `NEXT_PUBLIC_*` at **build time** in GitHub Actions (e.g. repo **Variables** in Settings → Secrets and variables → Actions). For the same values at runtime you can also put a `.env` in the standalone folder or pass them in the systemd unit with `Environment=NEXT_PUBLIC_API_URL=...`.

## Give the build more resources (when building on EC2)

If you build on EC2 and it’s slow or runs out of memory:

1. **More Node memory (if the instance has enough RAM)**  
   Use the heavy-memory script so Node can use up to 4GB:
   ```bash
   cd /var/www/VALClean/frontend
   npm run build:webpack:heavy
   ```
   Only use this if the instance has at least ~4.5GB RAM (e.g. t3.medium). On t3.micro/t3.small, skip or use 2048:
   ```bash
   NODE_OPTIONS=--max-old-space-size=2048 npm run build:webpack
   ```

2. **Larger instance for the build**  
   Temporarily change the instance type to **t3.medium** (2 vCPU, 4 GB RAM), run the build, then change back to t3.micro/t3.small if you want. In EC2 console: Instance → Actions → Instance settings → Change instance type.

3. **Swap (last resort on small instances)**  
   Add swap so the build doesn’t get killed when RAM is full (slower, but can complete):
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   npm run build:webpack
   ```

## Summary

| Method              | Build where     | EC2 does              | Build time on EC2 |
|---------------------|----------------|------------------------|-------------------|
| GitHub Actions + artifact | GitHub         | Download, unzip, run   | **0**             |
| Build on EC2        | EC2            | npm ci, build, run     | 10–15+ min        |

Use the artifact flow to avoid long builds on the server.
