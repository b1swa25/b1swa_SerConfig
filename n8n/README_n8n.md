# Native n8n Server Setup Tool v3.0 🚀

![n8n Banner](/home/b1swa/.gemini/antigravity/brain/935a5dee-7148-4f01-a865-0b32d86fb798/n8n_banner_1780132224151.png)

A production-ready, interactive bash script to configure an **n8n Workflow Automation Server** on any major Linux distribution. Handles networking, database, security, backups, and process management automatically.

## ✨ Features
- **Cross-Distro**: Supports `apt` (Ubuntu/Debian), `dnf` (Fedora/RHEL), `yum` (CentOS), `pacman` (Arch).
- **Static IP Setup**: Optional built-in static IP configuration using Netplan or NetworkManager.
- **Database Choice**: Pick between SQLite (simple) or PostgreSQL (production-grade).
- **Secure .env Config**: All secrets stored in `/etc/n8n/.env` with `chmod 600`.
- **Auto-Generated Encryption Key**: Credentials are encrypted with a unique key.
- **PM2 Process Manager**: Auto-restarts n8n on crash and system boot.
- **Smart Firewall**: Auto-detects `ufw`, `firewalld`, or `iptables`.
- **Daily Backups**: Optional cron-based backup with 7-day retention.
- **One-Liner Update**: Run `sudo n8n_update.sh` anytime to update.

## 📥 Installation

```bash
chmod +x setup_n8n_native.sh
sudo ./setup_n8n_native.sh
```

The interactive UI will guide you through every setting.

## 🛠️ Post-Installation Commands

| Command | Description |
| :--- | :--- |
| `pm2 status` | Check n8n process status |
| `pm2 logs n8n` | View live logs |
| `pm2 restart n8n` | Restart n8n |
| `sudo nano /etc/n8n/.env` | Edit configuration |
| `sudo n8n_update.sh` | Update n8n to latest |
| `sudo n8n_backup.sh` | Backup n8n data now |

## 📂 File Locations

| Path | Purpose |
| :--- | :--- |
| `/etc/n8n/.env` | All n8n environment configuration |
| `/usr/local/bin/start_n8n.sh` | PM2 start script (loads .env) |
| `/usr/local/bin/n8n_update.sh` | Update helper script |
| `/usr/local/bin/n8n_backup.sh` | Backup script |
| `/var/backups/n8n/` | Backup storage directory |
| `~/.n8n/` | n8n data directory (workflows, credentials) |

## 🐛 Troubleshooting

For detailed debugging commands, see the **[n8n Debugging Guide](n8n_debugging_guide.md)**.
