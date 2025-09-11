# Deployment Guide

## Quick Start

### Local Development
```bash
# Clone and setup
git clone <repository-url>
cd vehicle-fleet-management
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize database
python src/init_db.py

# Start development server
python src/main.py
```

Access the application at `http://localhost:5001`

### Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Manager | manager | manager123 |
| Driver | driver1 | driver123 |

## Production Deployment

### Using Docker

1. **Build and run with Docker Compose:**
```bash
docker-compose up -d
```

2. **Initialize database:**
```bash
docker-compose exec web python src/init_db.py
```

### Manual Production Setup

1. **Install dependencies:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql nginx
```

2. **Setup application:**
```bash
# Create user and directory
sudo useradd -m fleetapp
sudo mkdir -p /opt/fleet-management
sudo chown fleetapp:fleetapp /opt/fleet-management

# Setup application
cd /opt/fleet-management
git clone <repository-url> .
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

3. **Configure database:**
```bash
sudo -u postgres createuser fleetapp
sudo -u postgres createdb fleet_management -O fleetapp
sudo -u postgres psql -c "ALTER USER fleetapp PASSWORD 'your_password';"
```

4. **Environment configuration:**
```bash
cat > .env << EOF
FLASK_ENV=production
DATABASE_URL=postgresql://fleetapp:your_password@localhost:5432/fleet_management
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
EOF
```

5. **Initialize database:**
```bash
python src/init_db.py
```

6. **Setup systemd service:**
```ini
# /etc/systemd/system/fleet-management.service
[Unit]
Description=Fleet Management Application
After=network.target

[Service]
Type=exec
User=fleetapp
WorkingDirectory=/opt/fleet-management
Environment=PATH=/opt/fleet-management/venv/bin
EnvironmentFile=/opt/fleet-management/.env
ExecStart=/opt/fleet-management/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 src.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

7. **Configure Nginx:**
```nginx
# /etc/nginx/sites-available/fleet-management
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/fleet-management/src/static/;
        expires 1y;
    }
}
```

8. **Start services:**
```bash
sudo systemctl enable fleet-management
sudo systemctl start fleet-management
sudo ln -s /etc/nginx/sites-available/fleet-management /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

## Cloud Deployment

### AWS (Elastic Beanstalk)
1. Install EB CLI: `pip install awsebcli`
2. Initialize: `eb init`
3. Deploy: `eb create production`

### Google Cloud Platform
1. Install gcloud CLI
2. Deploy: `gcloud app deploy`

### Azure
1. Install Azure CLI
2. Deploy: `az webapp up --name fleet-management`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| FLASK_ENV | Environment mode | development |
| DATABASE_URL | Database connection string | sqlite:///src/database/app.db |
| SECRET_KEY | Flask secret key | (required) |
| JWT_SECRET_KEY | JWT signing key | (required) |
| HOST | Server host | 0.0.0.0 |
| PORT | Server port | 5001 |

## Security Checklist

- [ ] Change default passwords
- [ ] Set strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Configure HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Enable database authentication
- [ ] Configure backup procedures
- [ ] Set up monitoring and logging

## Troubleshooting

### Common Issues

1. **Database connection errors:**
   - Check DATABASE_URL format
   - Verify database server is running
   - Check user permissions

2. **Permission errors:**
   - Verify file ownership and permissions
   - Check systemd service user configuration

3. **Port conflicts:**
   - Change PORT in environment variables
   - Check for other services using the same port

### Logs

- Application logs: `/opt/fleet-management/logs/`
- System service logs: `journalctl -u fleet-management`
- Nginx logs: `/var/log/nginx/`

## Monitoring

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Performance Monitoring
- Monitor CPU and memory usage
- Check database performance
- Monitor response times
- Set up alerts for errors

## Backup and Recovery

### Database Backup
```bash
pg_dump -h localhost -U fleetapp fleet_management > backup.sql
```

### Application Backup
```bash
tar -czf fleet-app-backup.tar.gz /opt/fleet-management
```

### Recovery
```bash
# Restore database
psql -h localhost -U fleetapp fleet_management < backup.sql

# Restore application
tar -xzf fleet-app-backup.tar.gz -C /
```

## Scaling

### Horizontal Scaling
- Use load balancer (Nginx, HAProxy)
- Deploy multiple application instances
- Use shared database and file storage

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Optimize database configuration
- Tune application settings

## Support

For deployment issues:
1. Check logs for error messages
2. Verify configuration settings
3. Test database connectivity
4. Review security settings
5. Contact support with detailed error information

