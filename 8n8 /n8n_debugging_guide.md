# n8n Debugging & Troubleshooting Guide 🛠️

This guide provides essential commands for testing, validating, and debugging your native n8n server setup.

## 1. Process & Service Monitoring (PM2)

n8n is managed by PM2, a production process manager for Node.js.

| Command | Description |
| :--- | :--- |
| `pm2 status` | List all PM2 processes with their memory/CPU usage. |
| `pm2 restart n8n` | Restart the n8n process. |
| `pm2 stop n8n` | Stop the n8n process. |
| `pm2 start n8n` | Start the n8n process if stopped. |
| `pm2 info n8n` | Show detailed info (uptime, restarts, memory, env vars). |

## 2. Log Analysis

| Command | Description |
| :--- | :--- |
| `pm2 logs n8n` | View live trailing logs. |
| `pm2 logs n8n --lines 100` | View the last 100 lines. |
| `pm2 flush n8n` | Clear all logs to isolate new issues. |
| `cat /var/log/n8n_backup.log` | View auto-backup log history. |

## 3. Configuration Management

All n8n settings are stored in a single `.env` file for easy management.

| Command | Description |
| :--- | :--- |
| `sudo cat /etc/n8n/.env` | View your full n8n configuration. |
| `sudo nano /etc/n8n/.env` | Edit n8n settings (port, webhook, auth, database). |
| `pm2 restart n8n` | **Must run after editing** the .env to apply changes. |

## 4. Network & Firewall Checks

| Command | Description |
| :--- | :--- |
| `sudo netstat -tulpn \| grep $N8N_PORT` | Verify n8n is listening on the configured port. |
| `sudo ss -tulpn \| grep $N8N_PORT` | Alternative if `netstat` is not installed. |
| `curl -I http://localhost:5678` | Test local n8n HTTP response. |
| `sudo ufw status` | Check UFW firewall rules (Ubuntu/Debian). |
| `sudo firewall-cmd --list-ports` | Check firewalld rules (CentOS/Fedora). |
| `sudo iptables -L INPUT -v -n` | Check raw iptables rules. |

## 5. Static IP Diagnostics

| Command | Description |
| :--- | :--- |
| `ip addr show` | View current IP configuration on all interfaces. |
| `cat /etc/netplan/*.yaml` | View Netplan static IP config (Ubuntu). |
| `nmcli con show` | View NetworkManager connections (Fedora/RHEL). |
| `ip route` | View routing table and default gateway. |

## 6. Database Troubleshooting (PostgreSQL)

If you selected PostgreSQL as your database backend:

| Command | Description |
| :--- | :--- |
| `sudo systemctl status postgresql` | Check if PostgreSQL is running. |
| `sudo -u postgres psql -l` | List all databases. |
| `sudo -u postgres psql -d n8n -c "\dt"` | List all tables in the n8n database. |
| `sudo -u postgres psql -c "\du"` | List all database users and roles. |

## 7. Backup & Recovery

| Command | Description |
| :--- | :--- |
| `sudo n8n_backup.sh` | Run a manual backup immediately. |
| `ls -lh /var/backups/n8n/` | List all available backups with sizes. |
| `crontab -l` | View the current backup schedule. |
| `tar -xzf /var/backups/n8n/<file>.tar.gz -C ~/.n8n/` | Restore from a backup (stop n8n first). |

## 8. Update & Maintenance

| Command | Description |
| :--- | :--- |
| `sudo n8n_update.sh` | Update n8n to the latest version (stops, updates, restarts). |
| `n8n --version` | Check the currently installed n8n version. |
| `node -v` | Check the Node.js version. |
| `npm list -g n8n` | Check the exact installed n8n package version. |

## 9. Common Issues & Fixes

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| **"EADDRINUSE" Error** | Port conflict with another service. | Change `N8N_PORT` in `/etc/n8n/.env` and restart. |
| **Webhooks not working** | Incorrect `WEBHOOK_URL` or firewall blocking. | Verify URL in `.env` matches your public IP/domain. |
| **n8n not starting on boot** | PM2 startup not saved. | Run `pm2 save` and `pm2 startup`. |
| **DB connection refused** | PostgreSQL not running or wrong credentials. | Check `systemctl status postgresql` and `.env` credentials. |
| **Can't access from browser** | Firewall blocking the port. | Check firewall rules (Section 4 above). |
| **IP changed after reboot** | DHCP assigned a new IP. | Set a static IP using the script or manually via Netplan/nmcli. |
| **"Encryption key missing"** | `.env` file was deleted or permissions wrong. | Recreate from backup or re-run setup. Check `chmod 600 /etc/n8n/.env`. |
