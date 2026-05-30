#!/bin/bash

# ==============================================================================
# Script: setup_n8n_native.sh
# Description: Cross-Distro Native n8n Server Setup with Progress Tracking
# Version: 3.0 (Production-Ready Edition)
# Copyright: © b1swa
# Contact: sandipbiswa10@gmail.com
# ==============================================================================

# Exit on error and catch pipeline failures
set -e
set -o pipefail

# Sanitize PATH to prevent user NVM binaries from polluting or breaking global system installation
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export DEBIAN_FRONTEND=noninteractive

# Parse command line options
SILENT=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --silent) SILENT=true; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done

# Setup logging
LOG_FILE="/var/log/n8n_install.log"
touch "$LOG_FILE" 2>/dev/null || LOG_FILE="/tmp/n8n_install.log"
echo "=== n8n Native Setup Started at $(date) ===" > "$LOG_FILE"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Detect correct user and home directory (handles running directly as root or via sudo)
REAL_USER="${SUDO_USER:-root}"
if [ "$REAL_USER" = "root" ]; then
    USER_HOME="/root"
else
    USER_HOME="/home/$REAL_USER"
fi

# Paths
N8N_ENV_FILE="/etc/n8n/.env"
N8N_BACKUP_DIR="/var/backups/n8n"
N8N_DATA_DIR="$USER_HOME/.n8n"

cleanup_on_error() {
    local exit_code=$?
    if [ $exit_code -ne 0 ] && [ "$exit_code" -ne 130 ]; then
        echo -e "\n${RED}❌ Installation failed.${NC}"
        if [ -f "$LOG_FILE" ]; then
            echo -e "Please check the log file for details: ${YELLOW}$LOG_FILE${NC}"
            echo -e "\n${CYAN}--- Last 20 lines of $LOG_FILE ---${NC}"
            tail -n 20 "$LOG_FILE"
            echo -e "${CYAN}------------------------------------------------${NC}"
        fi
    fi
}
trap cleanup_on_error EXIT

# Clear screen
if [ "$SILENT" != "true" ]; then
    clear
fi

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run with sudo.${NC}"
    exit 1
fi

# ==============================================================================
# DISTRO DETECTION
# ==============================================================================
PKG_MANAGER=""
DISTRO_NAME="Unknown"
if command -v apt-get &> /dev/null; then
    PKG_MANAGER="apt"
    DISTRO_NAME=$(lsb_release -ds 2>/dev/null || cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo "Debian/Ubuntu")
elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
    DISTRO_NAME=$(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo "Fedora/RHEL")
elif command -v yum &> /dev/null; then
    PKG_MANAGER="yum"
    DISTRO_NAME=$(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo "CentOS/RHEL")
elif command -v pacman &> /dev/null; then
    PKG_MANAGER="pacman"
    DISTRO_NAME=$(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo "Arch Linux")
else
    echo -e "${RED}Unsupported package manager. Could not detect apt, dnf, yum, or pacman.${NC}"
    exit 1
fi

# ==============================================================================
# WHIPTAIL BOOTSTRAP
# ==============================================================================
install_whiptail() {
    if ! command -v whiptail &> /dev/null; then
        echo -e "${GREEN}Installing dialog/whiptail for interactive setup...${NC}"
        case $PKG_MANAGER in
            apt) apt-get update -y > /dev/null && apt-get install -y whiptail > /dev/null ;;
            dnf) dnf install -y newt > /dev/null ;;
            yum) yum install -y newt > /dev/null ;;
            pacman) pacman -Sy --noconfirm libnewt > /dev/null ;;
        esac
    fi
}

if [ "$SILENT" != "true" ]; then
    install_whiptail
fi

# ==============================================================================
# NETWORK HELPERS
# ==============================================================================
detect_interface() {
    ip route | grep default | awk '{print $5}' | head -1
}

detect_current_ip() {
    hostname -I | awk '{print $1}'
}

detect_gateway() {
    ip route | grep default | awk '{print $3}' | head -1
}

detect_dns() {
    grep -m1 "nameserver" /etc/resolv.conf 2>/dev/null | awk '{print $2}' || echo "8.8.8.8"
}

detect_subnet_cidr() {
    local iface=$(detect_interface)
    ip -o -f inet addr show "$iface" | awk '{print $4}' | head -1
}

# ==============================================================================
# BRANDING
# ==============================================================================
show_branding() {
    local HOSTNAME=$(hostname)
    local HOST_IP=$(detect_current_ip)
    local IFACE=$(detect_interface)
    
    whiptail --title "b1swa | Native n8n Installer v3.0 🚀" --msgbox "Welcome to the n8n Workflow Automation Setup!

[ System Information ]
Hostname:   $HOSTNAME
Host IP:    $HOST_IP
Interface:  $IFACE
Distro:     $DISTRO_NAME
Pkg Mgr:    $PKG_MANAGER

Engine:     Node.js / n8n
Copyright © b1swa
Contact:    sandipbiswa10@gmail.com

This tool will configure a production-ready n8n server.
Press OK to continue." 20 65
}

if [ "$SILENT" != "true" ]; then
    show_branding
fi

# ==============================================================================
# PHASE 1: STATIC IP CONFIGURATION (Optional)
# ==============================================================================
STATIC_IP_CONFIGURED="No"
if [ "$SILENT" != "true" ] && whiptail --title "b1swa | Network: Static IP" --yesno "RECOMMENDED: Do you want to set a Static IP for this server?

A static IP ensures your n8n webhooks and access URL never change.
If you skip this, your current dynamic IP will be used.

Current IP: $(detect_current_ip)
Interface:  $(detect_interface)" 14 65; then

    IFACE=$(detect_interface)
    CURRENT_IP=$(detect_current_ip)
    CURRENT_GW=$(detect_gateway)
    CURRENT_DNS=$(detect_dns)
    CURRENT_CIDR=$(detect_subnet_cidr)
    # Extract just the prefix length
    CURRENT_PREFIX=$(echo "$CURRENT_CIDR" | cut -d'/' -f2)

    STATIC_IP=$(whiptail --title "b1swa | Static IP: Address" --inputbox "Enter the static IP address for this server:" 10 60 "$CURRENT_IP" 3>&1 1>&2 2>&3)
    STATIC_PREFIX=$(whiptail --title "b1swa | Static IP: Subnet Prefix" --inputbox "Enter the subnet prefix length (e.g., 24 for /24 = 255.255.255.0):" 10 60 "$CURRENT_PREFIX" 3>&1 1>&2 2>&3)
    STATIC_GW=$(whiptail --title "b1swa | Static IP: Gateway" --inputbox "Enter the default gateway:" 10 60 "$CURRENT_GW" 3>&1 1>&2 2>&3)
    STATIC_DNS=$(whiptail --title "b1swa | Static IP: DNS Server" --inputbox "Enter the DNS server (comma-separated for multiple):" 10 60 "$CURRENT_DNS" 3>&1 1>&2 2>&3)

    # Apply static IP using Netplan (Ubuntu) or nmcli (RHEL/Fedora) or ip (Arch)
    if [ -d /etc/netplan ]; then
        # Netplan (Ubuntu 18.04+)
        cat <<EOF > /etc/netplan/01-n8n-static.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    $IFACE:
      addresses:
        - $STATIC_IP/$STATIC_PREFIX
      routes:
        - to: default
          via: $STATIC_GW
      nameservers:
        addresses: [${STATIC_DNS//,/, }]
EOF
        netplan apply > /dev/null 2>&1 || true
    elif command -v nmcli &> /dev/null; then
        # NetworkManager (Fedora/RHEL/CentOS)
        nmcli con mod "$IFACE" ipv4.addresses "$STATIC_IP/$STATIC_PREFIX" > /dev/null 2>&1
        nmcli con mod "$IFACE" ipv4.gateway "$STATIC_GW" > /dev/null 2>&1
        nmcli con mod "$IFACE" ipv4.dns "$STATIC_DNS" > /dev/null 2>&1
        nmcli con mod "$IFACE" ipv4.method manual > /dev/null 2>&1
        nmcli con up "$IFACE" > /dev/null 2>&1 || true
    else
        # Fallback: direct ip command (temporary, won't persist across reboots without further config)
        ip addr flush dev "$IFACE" > /dev/null 2>&1
        ip addr add "$STATIC_IP/$STATIC_PREFIX" dev "$IFACE" > /dev/null 2>&1
        ip route add default via "$STATIC_GW" > /dev/null 2>&1 || true
    fi

    HOST_IP="$STATIC_IP"
    STATIC_IP_CONFIGURED="Yes ($STATIC_IP)"
    sleep 2
else
    HOST_IP=$(detect_current_ip)
fi

# ==============================================================================
# PHASE 2: n8n CONFIGURATION
# ==============================================================================
if [ "$SILENT" = "true" ]; then
    : "${N8N_PORT:=5678}"
    : "${N8N_WEBHOOK_URL:=http://$HOST_IP:$N8N_PORT}"
else
    N8N_PORT=$(whiptail --title "b1swa | Configuration: Port" --inputbox "Enter the port for n8n to listen on (Default: 5678):" 10 60 "5678" 3>&1 1>&2 2>&3)
    if [ -z "$N8N_PORT" ]; then N8N_PORT="5678"; fi

    N8N_WEBHOOK_URL=$(whiptail --title "b1swa | Configuration: Webhook URL" --inputbox "Enter the public URL for webhooks:

Examples:
  https://n8n.yourdomain.com
  http://$HOST_IP:$N8N_PORT" 12 70 "http://$HOST_IP:$N8N_PORT" 3>&1 1>&2 2>&3)
    if [ -z "$N8N_WEBHOOK_URL" ]; then N8N_WEBHOOK_URL="http://$HOST_IP:$N8N_PORT"; fi
fi

# ==============================================================================
# PHASE 3: DATABASE SELECTION
# ==============================================================================
DB_POSTGRESDB_HOST=""
DB_POSTGRESDB_PORT=""
DB_POSTGRESDB_DATABASE=""
DB_POSTGRESDB_USER=""
DB_POSTGRESDB_PASSWORD=""

if [ "$SILENT" = "true" ]; then
    : "${DB_TYPE:=sqlite}"
    : "${INSTALL_POSTGRES:=false}"
    if [ "$DB_TYPE" = "postgres" ]; then
        : "${DB_POSTGRESDB_HOST:=localhost}"
        : "${DB_POSTGRESDB_PORT:=5432}"
        : "${DB_POSTGRESDB_DATABASE:=n8n}"
        : "${DB_POSTGRESDB_USER:=n8n}"
        : "${DB_POSTGRESDB_PASSWORD:=n8npass}"
    fi
else
    DB_TYPE=$(whiptail --title "b1swa | Database Backend" --menu "Select the database for n8n to use:

SQLite  = Simple, zero-config (good for testing)
Postgres = Recommended for production (durable, scalable)" 15 65 2 \
        "sqlite" "SQLite (Default - No extra setup)" \
        "postgres" "PostgreSQL (Recommended for production)" \
        3>&1 1>&2 2>&3)

    if [ "$DB_TYPE" = "postgres" ]; then
        if whiptail --title "b1swa | PostgreSQL: Install?" --yesno "Do you want this script to install PostgreSQL locally?

Select 'No' if PostgreSQL is already running on this or another machine." 10 65; then
            INSTALL_POSTGRES="true"
        else
            INSTALL_POSTGRES="false"
        fi

        DB_POSTGRESDB_HOST=$(whiptail --title "b1swa | PostgreSQL: Host" --inputbox "Database host:" 10 60 "localhost" 3>&1 1>&2 2>&3)
        DB_POSTGRESDB_PORT=$(whiptail --title "b1swa | PostgreSQL: Port" --inputbox "Database port:" 10 60 "5432" 3>&1 1>&2 2>&3)
        DB_POSTGRESDB_DATABASE=$(whiptail --title "b1swa | PostgreSQL: Database" --inputbox "Database name:" 10 60 "n8n" 3>&1 1>&2 2>&3)
        DB_POSTGRESDB_USER=$(whiptail --title "b1swa | PostgreSQL: User" --inputbox "Database user:" 10 60 "n8n" 3>&1 1>&2 2>&3)
        DB_POSTGRESDB_PASSWORD=$(whiptail --title "b1swa | PostgreSQL: Password" --passwordbox "Database password:" 10 60 3>&1 1>&2 2>&3)
    fi
fi

# ==============================================================================
# PHASE 4: SECURITY
# ==============================================================================
N8N_BASIC_AUTH_ACTIVE="false"
N8N_BASIC_AUTH_USER=""
N8N_BASIC_AUTH_PASSWORD=""

if [ "$SILENT" = "true" ]; then
    : "${N8N_BASIC_AUTH_ACTIVE:=false}"
    if [ "$N8N_BASIC_AUTH_ACTIVE" = "true" ]; then
        : "${N8N_BASIC_AUTH_USER:=admin}"
        : "${N8N_BASIC_AUTH_PASSWORD:=adminpass}"
    fi
else
    if whiptail --title "b1swa | Security: Basic Auth" --yesno "Do you want to enable Basic Authentication for the n8n web interface?

This adds a login prompt before anyone can access n8n." 10 65; then
        N8N_BASIC_AUTH_ACTIVE="true"
        N8N_BASIC_AUTH_USER=$(whiptail --title "b1swa | Basic Auth: Username" --inputbox "Enter a username:" 10 60 "admin" 3>&1 1>&2 2>&3)
        N8N_BASIC_AUTH_PASSWORD=$(whiptail --title "b1swa | Basic Auth: Password" --passwordbox "Enter a password:" 10 60 3>&1 1>&2 2>&3)
    fi
fi

# ==============================================================================
# PHASE 5: BACKUP CONFIGURATION
# ==============================================================================
ENABLE_BACKUP="false"
BACKUP_CRON=""

if [ "$SILENT" = "true" ]; then
    : "${ENABLE_BACKUP:=false}"
    if [ "$ENABLE_BACKUP" = "true" ]; then
        : "${BACKUP_CRON:=02:00}"
    fi
else
    if whiptail --title "b1swa | Backup: Auto-Backup" --yesno "Do you want to enable automatic daily backups of your n8n data?

Backups will be stored at: $N8N_BACKUP_DIR
Retention: Last 7 days" 12 65; then
        ENABLE_BACKUP="true"
        BACKUP_CRON=$(whiptail --title "b1swa | Backup: Schedule" --inputbox "Enter the backup time (24h format, e.g., 02:00 for 2 AM):" 10 60 "02:00" 3>&1 1>&2 2>&3)
    fi
fi

# ==============================================================================
# PHASE 6: REVERSE PROXY & SSL (Optional)
# ==============================================================================
ENABLE_PROXY="false"
N8N_DOMAIN=""
ENABLE_SSL="false"
SSL_EMAIL=""

if [ "$SILENT" = "true" ]; then
    : "${ENABLE_PROXY:=false}"
    : "${ENABLE_SSL:=false}"
    if [ "$ENABLE_PROXY" = "true" ]; then
        : "${N8N_DOMAIN:=$HOST_IP}"
        if [ "$ENABLE_SSL" = "true" ]; then
            : "${SSL_EMAIL:=admin@example.com}"
        fi
    fi
else
    if whiptail --title "b1swa | Reverse Proxy: Nginx" --yesno "Do you want to set up Nginx as a reverse proxy?

This is RECOMMENDED if you plan to:
  - Use a domain name (e.g., n8n.yourdomain.com)
  - Enable HTTPS/SSL for secure webhook connections
  - Hide the port number from the URL

If you skip this, n8n will be accessed directly via IP:Port." 16 65; then
        ENABLE_PROXY="true"
        N8N_DOMAIN=$(whiptail --title "b1swa | Reverse Proxy: Domain" --inputbox "Enter the domain or subdomain for n8n:

(Use the server IP if you don't have a domain)" 12 60 "$HOST_IP" 3>&1 1>&2 2>&3)
        if [ -z "$N8N_DOMAIN" ]; then N8N_DOMAIN="$HOST_IP"; fi

        if whiptail --title "b1swa | SSL: Let's Encrypt" --yesno "Do you want to enable FREE SSL (HTTPS) via Let's Encrypt?

Requirements:
  - A valid domain name pointing to this server
  - Port 80 and 443 must be accessible from the internet

Note: This will NOT work with a raw IP address." 14 65; then
            ENABLE_SSL="true"
            SSL_EMAIL=$(whiptail --title "b1swa | SSL: Email" --inputbox "Enter your email for Let's Encrypt certificate notifications:" 10 60 "" 3>&1 1>&2 2>&3)
        fi
    fi
fi

# ==============================================================================
# PHASE 7: PERFORMANCE TUNING
# ==============================================================================
if [ "$SILENT" = "true" ]; then
    : "${N8N_MEMORY_LIMIT:=1G}"
else
    N8N_MEMORY_LIMIT=$(whiptail --title "b1swa | Performance: Memory Limit" --inputbox "Set a maximum memory limit for n8n (PM2 will auto-restart if exceeded).

Examples: 512M, 1G, 2G
Leave blank for no limit:" 12 60 "1G" 3>&1 1>&2 2>&3)
fi

# ==============================================================================
# REVIEW & CONFIRM
# ==============================================================================
PROXY_STATUS="Disabled"
if [ "$ENABLE_PROXY" = "true" ]; then
    PROXY_STATUS="Nginx → $N8N_DOMAIN"
    if [ "$ENABLE_SSL" = "true" ]; then PROXY_STATUS="$PROXY_STATUS (SSL)"; fi
fi

REVIEW_TEXT="Ready to install n8n?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ Network ]
  Static IP:    $STATIC_IP_CONFIGURED
  Port:         $N8N_PORT
  Webhook URL:  $N8N_WEBHOOK_URL

[ Reverse Proxy ]
  Proxy:        $PROXY_STATUS

[ Database ]
  Backend:      $DB_TYPE

[ Security ]
  Basic Auth:   $N8N_BASIC_AUTH_ACTIVE

[ Performance ]
  Memory Limit: ${N8N_MEMORY_LIMIT:-None}

[ Maintenance ]
  Auto-Backup:  $ENABLE_BACKUP

Press Yes to begin automated setup."

if [ "$SILENT" != "true" ]; then
    whiptail --title "b1swa | Review Configuration" --yesno "$REVIEW_TEXT" 28 60 || exit 0
fi

# ==============================================================================
# AUTOMATED INSTALLATION
# ==============================================================================
run_installation() {
    echo 2; sleep 1
    echo "XXX"
    echo "📦 Phase 1/11: Installing Dependencies..."
    echo "XXX"
    case $PKG_MANAGER in
        apt)
            apt-get update -y >> "$LOG_FILE" 2>&1
            apt-get install -y curl wget gnupg2 >> "$LOG_FILE" 2>&1
            ;;
        dnf|yum)
            $PKG_MANAGER install -y curl wget >> "$LOG_FILE" 2>&1
            ;;
        pacman)
            pacman -Sy --noconfirm curl wget >> "$LOG_FILE" 2>&1
            ;;
    esac

    echo 10; sleep 1
    echo "XXX"
    echo "🟩 Phase 2/11: Installing Node.js (v20)..."
    echo "XXX"
    if ! command -v node &> /dev/null || [[ $(node -v | cut -d. -f1 | tr -d 'v') -lt 18 ]]; then
        case $PKG_MANAGER in
            apt)
                curl -fsSL https://deb.nodesource.com/setup_20.x 2>> "$LOG_FILE" | bash - >> "$LOG_FILE" 2>&1
                apt-get install -y nodejs >> "$LOG_FILE" 2>&1
                ;;
            dnf|yum)
                curl -fsSL https://rpm.nodesource.com/setup_20.x 2>> "$LOG_FILE" | bash - >> "$LOG_FILE" 2>&1
                $PKG_MANAGER install -y nodejs >> "$LOG_FILE" 2>&1
                ;;
            pacman)
                pacman -Sy --noconfirm nodejs npm >> "$LOG_FILE" 2>&1
                ;;
        esac
    fi

    echo 20; sleep 1
    echo "XXX"
    echo "🐘 Phase 3/11: Configuring Database..."
    echo "XXX"
    if [ "$DB_TYPE" = "postgres" ] && [ "$INSTALL_POSTGRES" = "true" ]; then
        case $PKG_MANAGER in
            apt)
                apt-get install -y postgresql postgresql-contrib >> "$LOG_FILE" 2>&1
                ;;
            dnf|yum)
                $PKG_MANAGER install -y postgresql-server postgresql-contrib >> "$LOG_FILE" 2>&1
                postgresql-setup --initdb >> "$LOG_FILE" 2>&1 || true
                ;;
            pacman)
                pacman -Sy --noconfirm postgresql >> "$LOG_FILE" 2>&1
                su - postgres -c "initdb --locale en_US.UTF-8 -D /var/lib/postgres/data" >> "$LOG_FILE" 2>&1 || true
                ;;
        esac
        systemctl enable postgresql >> "$LOG_FILE" 2>&1
        systemctl start postgresql >> "$LOG_FILE" 2>&1

        # Create DB and User
        sudo -u postgres psql -c "CREATE USER $DB_POSTGRESDB_USER WITH PASSWORD '$DB_POSTGRESDB_PASSWORD';" >> "$LOG_FILE" 2>&1 || true
        sudo -u postgres psql -c "CREATE DATABASE $DB_POSTGRESDB_DATABASE OWNER $DB_POSTGRESDB_USER;" >> "$LOG_FILE" 2>&1 || true
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_POSTGRESDB_DATABASE TO $DB_POSTGRESDB_USER;" >> "$LOG_FILE" 2>&1 || true
    fi

    echo 30; sleep 1
    echo "XXX"
    echo "☁️  Phase 4/11: Installing n8n & PM2..."
    echo "XXX"
    npm install -g n8n pm2 >> "$LOG_FILE" 2>&1

    # Detect absolute paths of newly installed pm2 and n8n to avoid any PATH issues
    PM2_PATH=$(command -v pm2 || echo "/usr/bin/pm2")
    N8N_PATH=$(command -v n8n || echo "/usr/bin/n8n")

    echo 40; sleep 1
    echo "XXX"
    echo "📝 Phase 5/11: Creating Environment Configuration..."
    echo "XXX"
    # Create a proper .env file for all n8n settings
    mkdir -p /etc/n8n
    cat <<EOF > "$N8N_ENV_FILE"
# ==============================================================================
# n8n Environment Configuration
# Generated by setup_n8n_native.sh on $(date)
# ==============================================================================

# Server
N8N_PORT=$N8N_PORT
N8N_HOST=0.0.0.0
WEBHOOK_URL=$N8N_WEBHOOK_URL
N8N_PROTOCOL=http
GENERIC_TIMEZONE=$(cat /etc/timezone 2>/dev/null || timedatectl show --property=Timezone --value 2>/dev/null || echo "UTC")

# Security
N8N_BASIC_AUTH_ACTIVE=$N8N_BASIC_AUTH_ACTIVE
N8N_BASIC_AUTH_USER=$N8N_BASIC_AUTH_USER
N8N_BASIC_AUTH_PASSWORD=$N8N_BASIC_AUTH_PASSWORD

# Encryption key for credentials (auto-generated)
N8N_ENCRYPTION_KEY=$(openssl rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | xxd -p | tr -d '\n' | head -c 64)
EOF

    # Add database config to .env if PostgreSQL
    if [ "$DB_TYPE" = "postgres" ]; then
        cat <<EOF >> "$N8N_ENV_FILE"

# Database (PostgreSQL)
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=$DB_POSTGRESDB_HOST
DB_POSTGRESDB_PORT=$DB_POSTGRESDB_PORT
DB_POSTGRESDB_DATABASE=$DB_POSTGRESDB_DATABASE
DB_POSTGRESDB_USER=$DB_POSTGRESDB_USER
DB_POSTGRESDB_PASSWORD=$DB_POSTGRESDB_PASSWORD
EOF
    fi

    chmod 600 "$N8N_ENV_FILE"

    echo 48; sleep 1
    echo "XXX"
    echo "⚙️  Phase 6/11: Configuring PM2 Service..."
    echo "XXX"
    
    # Create a start script that loads the env file and runs n8n using absolute path
    cat <<STARTEOF > /usr/local/bin/start_n8n.sh
#!/bin/bash
# Load environment variables from the n8n config file
set -a
source /etc/n8n/.env
set +a
exec $N8N_PATH
STARTEOF
    chmod +x /usr/local/bin/start_n8n.sh

    # Stop any existing n8n process using absolute PM2 path and correct user context
    sudo -u $REAL_USER $PM2_PATH delete n8n >> "$LOG_FILE" 2>&1 || $PM2_PATH delete n8n >> "$LOG_FILE" 2>&1 || true

    # Start n8n under PM2 (with optional memory limit)
    PM2_ARGS="--name n8n"
    if [ -n "$N8N_MEMORY_LIMIT" ]; then
        PM2_ARGS="$PM2_ARGS --max-memory-restart $N8N_MEMORY_LIMIT"
    fi
    sudo -u $REAL_USER $PM2_PATH start /usr/local/bin/start_n8n.sh $PM2_ARGS >> "$LOG_FILE" 2>&1 || $PM2_PATH start /usr/local/bin/start_n8n.sh $PM2_ARGS >> "$LOG_FILE" 2>&1
    sudo -u $REAL_USER $PM2_PATH save >> "$LOG_FILE" 2>&1 || $PM2_PATH save >> "$LOG_FILE" 2>&1

    # Setup PM2 log rotation
    sudo -u $REAL_USER $PM2_PATH install pm2-logrotate >> "$LOG_FILE" 2>&1 || $PM2_PATH install pm2-logrotate >> "$LOG_FILE" 2>&1 || true
    sudo -u $REAL_USER $PM2_PATH set pm2-logrotate:max_size 10M >> "$LOG_FILE" 2>&1 || true
    sudo -u $REAL_USER $PM2_PATH set pm2-logrotate:retain 7 >> "$LOG_FILE" 2>&1 || true
    sudo -u $REAL_USER $PM2_PATH set pm2-logrotate:compress true >> "$LOG_FILE" 2>&1 || true

    # Setup PM2 to start on system boot and ensure daemon is enabled/running
    env PATH=$PATH:/usr/bin $PM2_PATH startup systemd -u $REAL_USER --hp $USER_HOME >> "$LOG_FILE" 2>&1 || true
    
    # Add a sleep delay to prevent systemd from checking PID file before PM2 daemon writes it
    if [ -f "/etc/systemd/system/pm2-$REAL_USER.service" ]; then
        sed -i '/ExecStart=/a ExecStartPost=/bin/sleep 2' "/etc/systemd/system/pm2-$REAL_USER.service" || true
    fi

    systemctl daemon-reload >> "$LOG_FILE" 2>&1 || true
    systemctl enable pm2-$REAL_USER.service >> "$LOG_FILE" 2>&1 || true
    systemctl start pm2-$REAL_USER.service >> "$LOG_FILE" 2>&1 || true

    echo 58; sleep 1
    echo "XXX"
    echo "🔥 Phase 7/11: Configuring Firewall..."
    echo "XXX"
    if command -v ufw &> /dev/null && ufw status | grep -q "active"; then
        ufw allow $N8N_PORT/tcp > /dev/null
        if [ "$ENABLE_PROXY" = "true" ]; then
            ufw allow 80/tcp > /dev/null
            ufw allow 443/tcp > /dev/null
        fi
    elif command -v firewall-cmd &> /dev/null && firewall-cmd --state 2>/dev/null | grep -q "running"; then
        firewall-cmd --permanent --add-port=$N8N_PORT/tcp > /dev/null
        if [ "$ENABLE_PROXY" = "true" ]; then
            firewall-cmd --permanent --add-service=http > /dev/null
            firewall-cmd --permanent --add-service=https > /dev/null
        fi
        firewall-cmd --reload > /dev/null
    elif command -v iptables &> /dev/null; then
        iptables -I INPUT -p tcp --dport $N8N_PORT -j ACCEPT
        if [ "$ENABLE_PROXY" = "true" ]; then
            iptables -I INPUT -p tcp --dport 80 -j ACCEPT
            iptables -I INPUT -p tcp --dport 443 -j ACCEPT
        fi
        if command -v netfilter-persistent &> /dev/null; then netfilter-persistent save > /dev/null; fi
    fi

    echo 68; sleep 1
    echo "XXX"
    echo "🌐 Phase 8/11: Setting Up Reverse Proxy..."
    echo "XXX"
    if [ "$ENABLE_PROXY" = "true" ]; then
        case $PKG_MANAGER in
            apt) apt-get install -y nginx >> "$LOG_FILE" 2>&1 ;;
            dnf|yum) $PKG_MANAGER install -y nginx >> "$LOG_FILE" 2>&1 ;;
            pacman) pacman -Sy --noconfirm nginx >> "$LOG_FILE" 2>&1 ;;
        esac

        # Determine Nginx config path
        if [ -d /etc/nginx/sites-available ]; then
            NGINX_CONF="/etc/nginx/sites-available/n8n"
        else
            NGINX_CONF="/etc/nginx/conf.d/n8n.conf"
        fi

        cat <<NGINXEOF > "$NGINX_CONF"
server {
    listen 80;
    server_name $N8N_DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:$N8N_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
    }
}
NGINXEOF

        # Enable site (Debian/Ubuntu style)
        if [ -d /etc/nginx/sites-enabled ]; then
            ln -sf /etc/nginx/sites-available/n8n /etc/nginx/sites-enabled/n8n >> "$LOG_FILE" 2>&1
            rm -f /etc/nginx/sites-enabled/default >> "$LOG_FILE" 2>&1 || true
        fi

        nginx -t >> "$LOG_FILE" 2>&1
        systemctl enable nginx >> "$LOG_FILE" 2>&1
        systemctl restart nginx >> "$LOG_FILE" 2>&1
    fi

    echo 78; sleep 1
    echo "XXX"
    echo "🔒 Phase 9/11: Configuring SSL..."
    echo "XXX"
    if [ "$ENABLE_SSL" = "true" ]; then
        case $PKG_MANAGER in
            apt) apt-get install -y certbot python3-certbot-nginx >> "$LOG_FILE" 2>&1 ;;
            dnf) dnf install -y certbot python3-certbot-nginx >> "$LOG_FILE" 2>&1 ;;
            yum) yum install -y certbot python3-certbot-nginx >> "$LOG_FILE" 2>&1 ;;
            pacman) pacman -Sy --noconfirm certbot certbot-nginx >> "$LOG_FILE" 2>&1 ;;
        esac
        certbot --nginx -d "$N8N_DOMAIN" --non-interactive --agree-tos -m "$SSL_EMAIL" --redirect >> "$LOG_FILE" 2>&1 || true
    fi

    echo 85; sleep 1
    echo "XXX"
    echo "💾 Phase 10/11: Setting Up Backups & Utilities..."
    echo "XXX"
    # Create backup script
    mkdir -p "$N8N_BACKUP_DIR"
    cat <<BACKUPEOF > /usr/local/bin/n8n_backup.sh
#!/bin/bash
# n8n Automated Backup Script
BACKUP_DIR="$N8N_BACKUP_DIR"
DATA_DIR="$N8N_DATA_DIR"
TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="\$BACKUP_DIR/n8n_backup_\$TIMESTAMP.tar.gz"

mkdir -p "\$BACKUP_DIR"
tar -czf "\$BACKUP_FILE" -C "\$DATA_DIR" . 2>/dev/null

# Keep only last 7 backups
ls -1t "\$BACKUP_DIR"/n8n_backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null
echo "[\$(date)] Backup created: \$BACKUP_FILE"
BACKUPEOF
    chmod +x /usr/local/bin/n8n_backup.sh

    # Setup cron if enabled
    if [ "$ENABLE_BACKUP" = "true" ]; then
        BACKUP_HOUR=$(echo "$BACKUP_CRON" | cut -d: -f1)
        BACKUP_MIN=$(echo "$BACKUP_CRON" | cut -d: -f2)
        (crontab -l 2>/dev/null | grep -v "n8n_backup" || true; echo "$BACKUP_MIN $BACKUP_HOUR * * * /usr/local/bin/n8n_backup.sh >> /var/log/n8n_backup.log 2>&1") | crontab -
    fi

    # Create an update helper script targeting the correct PM2 user context and absolute path
    cat <<UPDATEEOF > /usr/local/bin/n8n_update.sh
#!/bin/bash
# n8n Update Helper
echo "🔄 Stopping n8n..."
sudo -u $REAL_USER $PM2_PATH stop n8n
echo "📦 Updating n8n..."
npm update -g n8n
echo "🚀 Restarting n8n..."
sudo -u $REAL_USER $PM2_PATH restart n8n
echo "✅ n8n updated to \$(n8n --version 2>/dev/null || echo 'latest')!"
UPDATEEOF
    chmod +x /usr/local/bin/n8n_update.sh

    # Create uninstall script targeting the correct PM2 user context and absolute path with non-interactive force option
    cat <<UNINSTALLEOF > /usr/local/bin/n8n_uninstall.sh
#!/bin/bash
if [ "\$EUID" -ne 0 ]; then echo "Please run with sudo."; exit 1; fi
echo "⚠️  This will completely remove n8n from this system."
if [ "\$1" != "-y" ] && [ "\$FORCE" != "true" ]; then
    read -p "Are you sure? (y/N): " confirm
    if [ "\$confirm" != "y" ] && [ "\$confirm" != "Y" ]; then echo "Cancelled."; exit 0; fi
fi
echo "Stopping n8n..."
sudo -u $REAL_USER $PM2_PATH stop n8n 2>/dev/null; sudo -u $REAL_USER $PM2_PATH delete n8n 2>/dev/null; sudo -u $REAL_USER $PM2_PATH save 2>/dev/null
echo "Removing n8n & PM2..."
npm uninstall -g n8n pm2 2>/dev/null
echo "Removing config files..."
rm -f /etc/n8n/.env /usr/local/bin/start_n8n.sh
rm -f /usr/local/bin/n8n_update.sh /usr/local/bin/n8n_backup.sh /usr/local/bin/n8n_uninstall.sh
echo "Removing Nginx config..."
rm -f /etc/nginx/sites-available/n8n /etc/nginx/sites-enabled/n8n /etc/nginx/conf.d/n8n.conf 2>/dev/null
systemctl restart nginx 2>/dev/null || true
echo -e "\n✅ n8n has been removed. Your data remains at ~/.n8n/ and backups at /var/backups/n8n/"
UNINSTALLEOF
    chmod +x /usr/local/bin/n8n_uninstall.sh

    echo 95; sleep 1
    echo "XXX"
    echo "🧹 Phase 11/11: Finalizing..."
    echo "XXX"
    sleep 1

    echo 100; sleep 1
    echo "XXX"
    echo "✅ Setup Complete!"
    echo "XXX"
}

echo -e "${CYAN}ℹ️  Installation logs are being saved in real-time to: ${YELLOW}$LOG_FILE${NC}"
echo -e "${CYAN}ℹ️  To monitor progress live, open a new terminal and run: ${GREEN}tail -f $LOG_FILE${NC}\n"
sleep 2

if [ "$SILENT" = "true" ]; then
    run_installation
else
    run_installation | whiptail --title "b1swa | Installation Progress" --gauge "Initializing..." 10 70 0
fi

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
# Determine access URL
ACCESS_URL="http://$HOST_IP:$N8N_PORT"
if [ "$ENABLE_PROXY" = "true" ]; then
    if [ "$ENABLE_SSL" = "true" ]; then
        ACCESS_URL="https://$N8N_DOMAIN"
    else
        ACCESS_URL="http://$N8N_DOMAIN"
    fi
fi

FINAL_MSG="n8n Server is now LIVE!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ Network ]
  IP Address:   $HOST_IP
  Static IP:    $STATIC_IP_CONFIGURED
  Port:         $N8N_PORT
  Proxy:        $PROXY_STATUS

[ Stack ]
  Engine:       Node.js / n8n
  Database:     $DB_TYPE
  Manager:      PM2 (Auto-start on boot)
  Memory Limit: ${N8N_MEMORY_LIMIT:-None}
  Log Rotation: Enabled (10MB / 7 files)
  Firewall:     Port $N8N_PORT/tcp allowed

[ Security ]
  Basic Auth:   $N8N_BASIC_AUTH_ACTIVE
  SSL:          $ENABLE_SSL
  Env File:     $N8N_ENV_FILE (chmod 600)

[ Maintenance ]
  Backup:       $ENABLE_BACKUP
  Update:       sudo n8n_update.sh
  Backup now:   sudo n8n_backup.sh
  Uninstall:    sudo n8n_uninstall.sh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Access n8n: $ACCESS_URL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$SILENT" != "true" ]; then
    whiptail --title "b1swa | 🎉 Success!" --msgbox "$FINAL_MSG" 30 60
fi

clear
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  n8n Server v3.0 successfully deployed!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${CYAN}Access URL:${NC}    $ACCESS_URL"
echo -e "  ${CYAN}Database:${NC}      $DB_TYPE"
echo -e "  ${CYAN}Static IP:${NC}     $STATIC_IP_CONFIGURED"
echo -e "  ${CYAN}Reverse Proxy:${NC} $PROXY_STATUS"
echo -e "  ${CYAN}Memory Limit:${NC}  ${N8N_MEMORY_LIMIT:-None}"
echo ""
if [ "$N8N_BASIC_AUTH_ACTIVE" = "true" ]; then
    echo -e "  ${YELLOW}Basic Auth:${NC}    Enabled (User: $N8N_BASIC_AUTH_USER)"
    echo ""
fi
echo -e "  ${CYAN}[ Useful Commands ]${NC}"
echo -e "  pm2 status              View process status"
echo -e "  pm2 logs n8n            View live logs"
echo -e "  pm2 restart n8n         Restart n8n"
echo -e "  sudo n8n_update.sh      Update n8n to latest"
echo -e "  sudo n8n_backup.sh      Backup n8n data now"
echo -e "  sudo n8n_uninstall.sh   Remove n8n completely"
echo -e "  sudo nano $N8N_ENV_FILE     Edit config"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
