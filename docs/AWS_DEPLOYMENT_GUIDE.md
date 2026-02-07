# VALClean – Full Step-by-Step AWS Deployment Guide

This guide walks you through deploying the VALClean booking system (Django + Next.js) on AWS. **Application runs on EC2**; **database and file storage use Supabase** (PostgreSQL + Storage buckets).

---

## Table of contents

1. [Prerequisites](#1-prerequisites)
2. [Architecture overview](#2-architecture-overview)
3. [Supabase: database and storage buckets](#3-supabase-database-and-storage-buckets)
4. [AWS account and region](#4-aws-account-and-region)
5. [VPC and networking](#5-vpc-and-networking)
6. [EC2 instance for application](#6-ec2-instance-for-application)
7. [Application setup on EC2](#7-application-setup-on-ec2)
8. [Load balancer and HTTPS](#8-load-balancer-and-https)
9. [Domain and DNS (Route 53)](#9-domain-and-dns-route-53)
10. [Environment variables checklist](#10-environment-variables-checklist)
11. [Deployment and updates](#11-deployment-and-updates)
12. [Optional: Redis (ElastiCache) and Celery](#12-optional-redis-elasticache-and-celery)

---

## 1. Prerequisites

- **Supabase account** ([supabase.com](https://supabase.com)) – for database and storage buckets (Supabase has its own free tier).
- **AWS account** with billing enabled. You can stay within **AWS Free Tier** for testing (see below).
- **Git** and **GitHub** repo with VALClean code (see [GITHUB_SETUP.md](../GITHUB_SETUP.md)).
- **Domain (optional but recommended)** for HTTPS and branding (e.g. `app.valclean.uk`).
- **Local machine**: SSH key pair for EC2, and basic use of terminal/PowerShell.

### AWS Free Tier (for testing)

Yes – this guide can use **AWS Free Tier** for test deployments:

| Service | Free Tier | Notes |
|--------|-----------|--------|
| **EC2** | **Yes** | 750 hours/month for 12 months for **t3.micro** (or t2.micro) in eligible regions. Use **t3.micro** for testing to stay free. |
| **VPC, Security groups** | **Yes** | No extra charge. |
| **Elastic IP** | **Yes** (while attached) | Free while attached to a running instance; small charge if left attached when instance is stopped. |
| **Application Load Balancer (ALB)** | **No** | ALB has an hourly cost. For **Free Tier testing**, use **single EC2 only** (no ALB): point DNS or use EC2 public IP / EC2 DNS name, with Nginx and a self-signed cert on the instance. |
| **Route 53** | **No** (low cost) | First hosted zone ~\$0.50/month; not part of Free Tier. You can skip Route 53 for tests and use EC2 IP/DNS only. |
| **Data transfer** | **Partial** | First 100 GB out/month (to internet) can be free in some cases; check current [AWS Free Tier](https://aws.amazon.com/free/) terms. |

**Free Tier test setup:** One **t3.micro** EC2 instance, default VPC, no ALB, no Route 53. Use EC2 public IP or default hostname (`ec2-x-x-x-x.compute.amazonaws.com`) with a self-signed certificate (Section 7.6 Option A). Database and storage are on Supabase (their free tier).  
**When you need ALB/Route 53:** Use them for production or when you add a real domain; that will incur small charges.

---

## 2. Architecture overview

```
Internet
    │
    ▼
[Application Load Balancer] ← HTTPS (ACM certificate)
    │
    └──► [EC2] Django (Gunicorn) + Next.js (Node) or static
              │
              ├──► [Supabase] PostgreSQL database (Django DATABASE_URL)
              └──► [Supabase] Storage buckets (media, job-photos, etc.)
```

- **ALB**: Terminates SSL, forwards to EC2.
- **EC2**: Runs backend (Django/Gunicorn) and frontend (Next.js or static). This is the only AWS compute.
- **Supabase**: Hosted PostgreSQL (Django data) and Storage buckets (file uploads). No RDS or S3.

---

## 3. Supabase: database and storage buckets

Set up Supabase first; EC2 will connect to it over the internet (no VPC peering needed).

### 3.1 Supabase project and database

1. Go to [Supabase Dashboard](https://app.supabase.com) and create a **new project** (or use an existing one).
2. **Settings → Database**: copy the **Connection string** (URI format).
   - Use **Connection pooling** (Session mode) for Django: e.g. `postgresql://postgres.[ref]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres`
   - Or **Direct connection**: `postgresql://postgres:[YOUR-PASSWORD]@db.[ref].supabase.co:5432/postgres`
   - Replace `[YOUR-PASSWORD]` with your database password. Store it in a password manager.
3. **Django `DATABASE_URL`** on EC2 will be this URI (use the same format your project uses; pooler is recommended for server apps).

### 3.2 Supabase API keys and JWT secret

1. **Settings → API**: note
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_ANON_KEY`
   - **service_role** key (keep secret) → `SUPABASE_SERVICE_ROLE_KEY`
2. **Settings → API → JWT Settings**: copy **JWT Secret** → `SUPABASE_JWT_SECRET` (needed for backend auth when verifying Supabase JWTs).

### 3.3 Supabase Storage buckets

VALClean uses Supabase Storage for uploads (e.g. job completion photos, general file uploads). Create the buckets in the Supabase Dashboard:

1. **Storage → New bucket**:
   - **job-photos** – for appointment completion photos (create with public or private policy as needed).
   - **images** (or any bucket name your app uses for general uploads via `/api/core/upload/`).
2. For each bucket, set **Policies** (RLS) so your app can read/write (e.g. allow `service_role` or define policies for authenticated users). The backend uses `SUPABASE_SERVICE_ROLE_KEY`, so it can access buckets when RLS allows the service role.

No AWS S3 or IAM is required; all file storage is in Supabase.

---

## 4. AWS account and region

1. Log in to [AWS Console](https://console.aws.amazon.com/).
2. Choose a **region** (e.g. `eu-west-2` for London). Use it consistently for all resources.
3. Create an **IAM user** for deployments (optional but recommended):
   - IAM → Users → Create user (e.g. `valclean-deploy`).
   - Attach policies: `AmazonEC2FullAccess`, `ElasticLoadBalancingFullAccess`, `AmazonRoute53FullAccess`, `AWSCertificateManagerFullAccess` (no RDS or S3 needed for this setup).
   - Create access key for CLI if you will use `aws cli`.

---

## 5. VPC and networking

Use the default VPC for simplicity, or create a dedicated VPC. Database and storage are on Supabase, so you only need security groups for the ALB and EC2.

### Option A – Use default VPC

- Note the **VPC ID** and **subnet IDs** (at least 2 in different AZs for the ALB).

### Option B – Create a new VPC

1. **VPC & more** (VPC wizard):
   - Name: `valclean-vpc`.
   - 2–3 AZs, 2–3 public subnets, 2–3 private subnets.
   - NAT gateway: 1 (so private instances can reach internet for Supabase and updates).
   - Create VPC and note **VPC ID**, **public subnet IDs**, **private subnet IDs**.

2. **Security groups** (create these in the chosen VPC):

   - **SG-ALB** (`valclean-alb-sg`):
     - Inbound: HTTPS 443 from `0.0.0.0/0`, HTTP 80 from `0.0.0.0/0` (redirect to HTTPS later).
     - Outbound: All.
   - **SG-EC2** (`valclean-ec2-sg`):
     - Inbound: TCP 8000 (or 80) from SG-ALB only (or from ALB SG).
     - Inbound: SSH 22 from your IP only (for admin).
     - Outbound: All (EC2 must reach Supabase over the internet for DB and Storage).

---

## 6. EC2 instance for application

1. **Launch instance**:
   - AMI: **Ubuntu Server 22.04 LTS**.
   - Instance type: **t3.micro** for **Free Tier** testing (1 vCPU, 1 GB RAM – enough for light use; Django + Node may be tight under load). For production or heavier use, choose **t3.small** (2 GB RAM) or larger.
   - Key pair: Create or select an existing one; download the `.pem` and keep it safe.
   - Network: your VPC; **subnet**: public (if you use ALB or single-EC2 with public IP) or private (then SSH via bastion or Session Manager).
   - Auto-assign public IP: **Enable** if in public subnet (needed for SSH and for single-EC2 access without ALB).
   - Security group: **SG-EC2** (from step 5).
   - Storage: 20–30 GB gp3 (first 30 GB EBS in Free Tier can be free for 12 months in eligible regions).

2. **Elastic IP (optional)**:
   - For **single EC2 (no ALB)** testing: allocate an Elastic IP and associate it so the instance keeps the same public IP. Free while the instance is running; small charge if you leave it attached when the instance is stopped.
   - If you use an ALB, you can rely on the ALB DNS name instead.

3. **Connect**:
   ```bash
   ssh -i your-key.pem ubuntu@<EC2-public-IP>
   ```

---

## 7. Application setup on EC2

Run these on the EC2 instance (Ubuntu).

### 7.1 System packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nodejs npm nginx git
```

Use Node 18+ (recommended for Next.js 14):

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 7.2 Clone repository

```bash
sudo mkdir -p /var/www
sudo chown ubuntu:ubuntu /var/www
cd /var/www
git clone https://github.com/YOUR_ORG/VALClean.git
cd VALClean
```

Replace `YOUR_ORG/VALClean` with your actual GitHub repo.

### 7.3 Backend (Django)

Django uses **Supabase** for the database and for file storage (buckets). Set `DATABASE_URL` and all `SUPABASE_*` vars in `.env` (see [Section 10](#10-environment-variables-checklist)).

```bash
cd /var/www/VALClean/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn dj-database-url
```

Create `.env` with your Supabase database URL and Supabase keys:

```bash
nano .env
# Paste production values: SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, etc.
```

Run migrations:

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # if first deploy
```

Test Gunicorn (same directory, venv active):

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

Then Ctrl+C. You will run it via systemd next.

### 7.4 Frontend (Next.js)

```bash
cd /var/www/VALClean/frontend
npm ci
npm run build
```

Create `.env.production` (or `.env.local`) with:

- `NEXT_PUBLIC_API_URL=https://api.yourdomain.com` (or your backend URL).

To run Next in production (Node server):

```bash
npm run start
```

Or use a static export if your app supports it (`next export` / `output: 'export'` in `next.config.js`), then serve the `out` folder with nginx.

### 7.5 Process managers (systemd)

**Gunicorn (Django)** – create `/etc/systemd/system/valclean-backend.service`:

```ini
[Unit]
Description=VALClean Django Gunicorn
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/VALClean/backend
Environment="PATH=/var/www/VALClean/backend/venv/bin"
EnvironmentFile=/var/www/VALClean/backend/.env
ExecStart=/var/www/VALClean/backend/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

**Next.js (optional, if not static)** – create `/etc/systemd/system/valclean-frontend.service`:

```ini
[Unit]
Description=VALClean Next.js
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/VALClean/frontend
Environment="NODE_ENV=production"
EnvironmentFile=/var/www/VALClean/frontend/.env.production
ExecStart=/usr/bin/npm run start
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable valclean-backend
sudo systemctl start valclean-backend
# If using Next.js server:
sudo systemctl enable valclean-frontend
sudo systemctl start valclean-frontend
```

### 7.6 Nginx (reverse proxy) – HTTPS only, always redirect HTTP → HTTPS

Single EC2 serving both Django and Next.js. **All HTTP traffic is redirected to HTTPS**; no plain HTTP is served to clients.

- Django (API/admin): backend → `http://127.0.0.1:8000`
- Next.js: frontend → `http://127.0.0.1:3000` (or serve static from `/var/www/VALClean/frontend/out`)

Choose one of the two options below depending on whether you are **testing (EC2 IP/DNS)** or **production (real domain)**.

---

#### Option A: Test deployment (EC2 IP or EC2 DNS from Amazon)

For test deployments you use the **EC2 public IP** or the **EC2 default DNS** (e.g. `ec2-1-2-3-4.compute-1.amazonaws.com`). Certbot/Let’s Encrypt cannot issue certificates for IPs or for that hostname in practice, so use a **self-signed certificate with OpenSSL**. Browsers will show a security warning (accept for testing); traffic is still HTTPS and HTTP is still redirected to HTTPS.

**1. Generate self-signed certificate (OpenSSL) on EC2:**

```bash
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/valclean-selfsigned.key \
  -out /etc/nginx/ssl/valclean-selfsigned.crt \
  -subj "/CN=localhost" \
  -addext "subjectAltName=IP:127.0.0.1,DNS:localhost"
```

**2. Nginx config for EC2 IP / EC2 DNS** – replace `EC2_PUBLIC_IP` or your EC2 hostname (e.g. `ec2-1-2-3-4.compute-1.amazonaws.com`) in `server_name`:

```nginx
# Upstreams
upstream django {
    server 127.0.0.1:8000;
}
upstream nextjs {
    server 127.0.0.1:3000;
}

# Always redirect HTTP to HTTPS (no exceptions)
server {
    listen 80 default_server;
    server_name _;
    return 301 https://$host$request_uri;
}

# Frontend + Backend on same host (test: one hostname/IP for all)
server {
    listen 443 ssl http2 default_server;
    server_name _;
    ssl_certificate     /etc/nginx/ssl/valclean-selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/valclean-selfsigned.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;

    location /api/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 20M;
    }
    location /admin/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location / {
        proxy_pass http://nextjs;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Access via `https://EC2_PUBLIC_IP` or `https://ec2-x-x-x-x.compute-1.amazonaws.com`. Set Django `ALLOWED_HOSTS` and frontend API URL to this IP or hostname. Browsers will warn about the self-signed cert—proceed for tests only.

---

#### Option B: Production (real domain, e.g. yourdomain.com)

When you have a **real domain** pointing to the server (e.g. via Route 53 or your registrar), use **Certbot (Let’s Encrypt)** so browsers trust the certificate.

**1. Install Certbot and obtain certificate:**

```bash
sudo apt install -y certbot python3-certbot-nginx
# DNS for yourdomain.com and api.yourdomain.com must point to this server, then:
sudo certbot certonly --nginx -d yourdomain.com -d api.yourdomain.com
# Certificates: /etc/letsencrypt/live/yourdomain.com/
```

**2. Nginx config for production (Certbot paths; HTTP always redirects to HTTPS):**

```nginx
# Upstreams
upstream django {
    server 127.0.0.1:8000;
}
upstream nextjs {
    server 127.0.0.1:3000;
}

# Always redirect HTTP to HTTPS (no exceptions)
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com;
    return 301 https://$host$request_uri;
}

# Frontend (HTTPS only)
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    location / {
        proxy_pass http://nextjs;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Backend API + Admin (HTTPS only)
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 20M;
    }
}
```

**Renewal:** `sudo certbot renew --nginx` (add to cron, e.g. `0 3 * * *`).

---

**Enable and test (same for A or B):**

```bash
sudo ln -s /etc/nginx/sites-available/valclean /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## 8. Load balancer and HTTPS (OpenSSL; always redirect HTTP → HTTPS)

We use **OpenSSL** for TLS. **All HTTP traffic is always redirected to HTTPS**—no exceptions.

- **Test (EC2 IP or EC2 DNS):** use a **self-signed certificate** (OpenSSL) on Nginx—no Certbot; see Section 7.6 Option A.
- **Production (real domain):** use **Certbot (Let’s Encrypt)** on Nginx; see Section 7.6 Option B.

### 8.1 Application Load Balancer (optional – not Free Tier)

**For AWS Free Tier testing, skip the ALB:** use a single EC2 instance with its public IP or Elastic IP and Nginx (Section 7.6 Option A). The ALB has an hourly cost.

When you want high availability or a fixed domain in front of EC2:

1. **EC2 → Load Balancers → Create**:
   - Type: **Application Load Balancer**.
   - Name: `valclean-alb`.
   - Scheme: **Internet-facing**.
   - VPC and subnets: at least 2 public subnets (different AZs).
   - Security group: **SG-ALB**.
   - Target group: Create new, name `valclean-tg`, target type **Instance**, protocol **HTTP**, port **80** (Nginx on EC2 listens on 80 and 443).
   - Register your EC2 instance in the target group (port 80).
   - Create ALB.

2. **Listeners (always redirect HTTP to HTTPS)**:
   - **HTTPS 443**: default action **forward** to `valclean-tg` (port 80). Attach your SSL certificate (from Certbot/OpenSSL on EC2, or upload to ACM if you use ALB for SSL—see 8.2).
   - **HTTP 80**: default action **Redirect to HTTPS** (protocol HTTPS, port 443, status 301). Do not serve content on port 80; redirect only.

### 8.2 SSL: self-signed (test) vs Certbot (production)

- **Test deployment (EC2 IP or EC2 DNS):** Use a **self-signed certificate** created with OpenSSL on EC2 (Section 7.6 Option A). No Certbot; no real domain required. Browsers will show a warning—accept only for testing.
- **Production (real domain):** Use **Certbot (Let’s Encrypt)** on EC2 (Section 7.6 Option B). Certbot uses OpenSSL and needs a domain that points to the server.
- **ALB in front of EC2:** Either terminate SSL on EC2 (Nginx with self-signed or Certbot certs) or on ALB (upload cert to ACM). In all cases, **HTTP 80 must redirect to HTTPS 443** (ALB and/or Nginx).
- **No ALB (single EC2):** Nginx on EC2 handles 80 (redirect only) and 443 (SSL). Use Option A or B from 7.6.

**Generate Django SECRET_KEY with OpenSSL** (on EC2 or locally):

```bash
openssl rand -hex 32
```

Use this value for `SECRET_KEY` in backend `.env`.

---

## 9. Domain and DNS (Route 53)

1. **Route 53 → Hosted zones**:
   - If you don’t have a hosted zone, **Create hosted zone** for `yourdomain.com` (you must own the domain; if it’s elsewhere, either transfer nameservers or create the zone and add the NS records at your registrar).
   - Create **A record** (alias): `yourdomain.com` → ALB (or EC2 Elastic IP if no ALB).
   - Create **A record** (alias): `api.yourdomain.com` → same ALB (routing is by host in Nginx).
   - DNS must point to the server **before** running Certbot (Let’s Encrypt validates via HTTP or DNS).

2. **CORS and ALLOWED_HOSTS**:
   - In Django `.env`: `ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com` and `CORS_ALLOWED_ORIGINS=https://yourdomain.com`.
   - In frontend: `NEXT_PUBLIC_API_URL=https://api.yourdomain.com` (HTTPS only).

---

## 10. Environment variables checklist

**Backend (`.env` on EC2)** – use your Supabase and app URLs. For **test (EC2 IP/DNS)** use `https://EC2_PUBLIC_IP` or `https://ec2-x-x-x-x.compute-1.amazonaws.com` in `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`; for **production** use your domain (e.g. `https://yourdomain.com`).

```bash
# Django
SECRET_KEY=<generate-with-openssl-rand-hex-32>
DEBUG=False
# Test: ALLOWED_HOSTS=ec2-x-x-x-x.compute-1.amazonaws.com,<EC2_PUBLIC_IP>
# Production: yourdomain.com,api.yourdomain.com,<ALB-DNS-name>
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Database – Supabase PostgreSQL (from Settings → Database → Connection string)
DATABASE_URL=postgresql://postgres.[ref]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
# Or direct: postgresql://postgres:[YOUR-PASSWORD]@db.[ref].supabase.co:5432/postgres

# CORS (Test: https://EC2_PUBLIC_IP or https://ec2-....amazonaws.com; Production: https://yourdomain.com)
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Supabase (required for auth + storage buckets)
SUPABASE_URL=https://[ref].supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
SUPABASE_JWT_SECRET=<from Supabase Dashboard → Settings → API → JWT Secret>

# Email (e.g. SendGrid)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<sendgrid-api-key>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

Storage is handled by Supabase buckets (e.g. `job-photos`, `images`); no AWS S3 keys needed.

**Frontend (`.env.production`)**:

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
# Any other NEXT_PUBLIC_* your app needs
```

Generate a secret key:

```bash
openssl rand -hex 32
```

---

## 11. Deployment and updates

1. **SSH to EC2**.
2. **Backend**:
   ```bash
   cd /var/www/VALClean && git pull
   cd backend && source venv/bin/activate
   pip install -r requirements.txt
   export DJANGO_SETTINGS_MODULE=config.settings.production
   python manage.py migrate
   python manage.py collectstatic --noinput
   sudo systemctl restart valclean-backend
   ```
3. **Frontend**:
   ```bash
   cd /var/www/VALClean/frontend
   npm ci && npm run build
   sudo systemctl restart valclean-frontend
   ```
4. **Nginx**: only if you changed site config: `sudo nginx -t && sudo systemctl reload nginx`.

---

## 12. Optional: Redis (ElastiCache) and Celery

If you use Celery for background tasks:

1. **ElastiCache → Redis**:
   - Create a Redis cluster in the same VPC; security group allow 6379 from SG-EC2.
   - Note the **primary endpoint**.

2. **Backend `.env`**:
   ```bash
   REDIS_URL=redis://valclean-redis.xxxxx.cache.amazonaws.com:6379/0
   ```

3. **Celery on EC2**: Install Celery and run `celery -A config worker` (and beat if needed) via systemd, same as Gunicorn.

---

## Summary checklist

- [ ] **Supabase**: Project created; database connection string, API keys (anon + service_role), and JWT secret noted; Storage buckets created (e.g. `job-photos`, `images`)
- [ ] VPC and security groups (ALB, EC2 only – no RDS)
- [ ] EC2 launched and SSH access verified
- [ ] Repo cloned; backend venv, dependencies, migrations, collectstatic
- [ ] Backend `.env` set with `DATABASE_URL` and all `SUPABASE_*` vars; Gunicorn running via systemd
- [ ] Frontend built; Next.js or static served; systemd if applicable
- [ ] Nginx configured and reloaded
- [ ] (Optional) ALB created; target group points to EC2; **HTTP 80 listener redirects to HTTPS 443** (skip for Free Tier; use single EC2 instead)
- [ ] **SSL with OpenSSL/Certbot**: Certbot (Let’s Encrypt) certificates on EC2; Nginx uses them for HTTPS
- [ ] Route 53 (or DNS) A records point to ALB (or EC2)
- [ ] CORS and ALLOWED_HOSTS match your domain (HTTPS URLs)
- [ ] **Always redirect HTTP → HTTPS** (Nginx and ALB); no plain HTTP served to users

For the first run, use HTTP on the ALB (port 80) and a single domain to verify Django and Next.js; then add ACM and HTTPS and the second domain.

This setup uses **EC2 for the app** and **Supabase for database and buckets**. Scale EC2 (instance size or multi-instance + Auto Scaling) as traffic grows; Supabase handles DB and storage scaling.
