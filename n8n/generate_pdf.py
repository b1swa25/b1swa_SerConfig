import os
from fpdf import FPDF

class N8NDocPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_y(7)
            self.set_x(10)
            self.set_font("helvetica", "B", 8)
            self.set_text_color(100, 110, 120)
            self.cell(170, 7, "NATIVE n8n SERVER: BEGINNER-TO-EXPERT DEPLOYMENT & MAINTENANCE GUIDE", new_x="RIGHT", new_y="TOP", align="L")
            if os.path.exists("logo.png"):
                self.image("logo.png", x=185, y=7, h=7)
            self.set_draw_color(200, 200, 200)
            self.line(10, 16, 200, 16)
            self.set_y(self.t_margin)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(100, 10, f"Page {self.page_no()}", new_x="RIGHT", new_y="TOP", align="L")
            self.cell(0, 10, "v3.0 | Release: 2026-05-30", new_x="LMARGIN", new_y="NEXT", align="R")

    def chapter_title(self, num, title):
        self.set_font("helvetica", "B", 14)
        self.set_text_color(0, 119, 182) # Primary blue
        self.cell(0, 10, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def add_bullet(self, bold_prefix, text):
        self.set_font("helvetica", "B", 10)
        self.set_text_color(50, 50, 50)
        self.write(6, " -  " + bold_prefix + ": ")
        self.set_font("helvetica", "", 10)
        self.write(6, text + "\n")
        self.ln(2)

    def add_paragraph(self, text, bold=False):
        self.set_font("helvetica", "B" if bold else "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT", align="J")
        self.ln(2)

    def add_figure(self, img_path, fig_num, caption, w=110, h=52):
        if os.path.exists(img_path):
            self.ln(2)
            x = (210 - w) / 2
            img_y = self.get_y()
            if img_y + h + 15 > 297:
                self.add_page()
                img_y = self.get_y()
            self.image(img_path, x=x, y=img_y, w=w, h=h)
            self.set_y(img_y + h + 1)
            self.set_font("helvetica", "I", 8.5)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, f"Fig. {fig_num}: {caption}", align="C", new_x="LMARGIN", new_y="NEXT")
            self.ln(4)

    def add_code_block(self, code_lines):
        self.set_font("courier", "", 9)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(30, 30, 30)
        for line in code_lines:
            self.cell(0, 5, line, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def add_callout(self, title, text_lines, type="note"):
        if type == "trick":
            self.set_fill_color(255, 253, 230) # Yellowish
            self.set_draw_color(217, 180, 0)
            text_color = (150, 110, 0)
        elif type == "did_you_know":
            self.set_fill_color(230, 245, 255) # Bluish
            self.set_draw_color(0, 180, 216)
            text_color = (0, 100, 150)
        else: # Note
            self.set_fill_color(240, 240, 240) # Gray
            self.set_draw_color(150, 150, 150)
            text_color = (80, 80, 80)
            
        start_y = self.get_y()
        self.ln(2)
        self.set_font("helvetica", "B", 10)
        self.set_text_color(*text_color)
        self.cell(0, 6, f"  {title.upper()}", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 9.5)
        self.set_text_color(50, 50, 50)
        for line in text_lines:
            self.multi_cell(0, 5, f"  {line}", new_x="LMARGIN", new_y="NEXT", align="J")
        end_y = self.get_y()
        self.rect(10, start_y, 190, end_y - start_y + 2, "D")
        self.ln(4)

# Initialize PDF
pdf = N8NDocPDF()
pdf.set_margins(10, 22, 10)
pdf.set_auto_page_break(auto=True, margin=15)

# ==============================================================================
# PAGE 1: COVER PAGE
# ==============================================================================
pdf.add_page()
pdf.set_fill_color(24, 28, 36) # Cyberpunk dark background
pdf.rect(0, 0, 210, 297, "F")

# Centered Logo on cover page (above title)
logo_path = "logo.png"
if not os.path.exists(logo_path):
    logo_path = "/home/b1swa/Documents/n8n/logo.png"

if os.path.exists(logo_path):
    pdf.image(logo_path, x=82.5, y=25, w=45)

# Title Accents
pdf.set_fill_color(0, 180, 216) # Neon blue accent bar
pdf.rect(0, 95, 210, 16, "F")

# Main Titles
pdf.set_font("helvetica", "B", 26)
pdf.set_text_color(255, 255, 255)
pdf.set_y(60)
pdf.cell(0, 15, "NATIVE n8n AUTOMATION SERVER", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_font("helvetica", "", 18)
pdf.cell(0, 10, "Complete Production Sizing, Deployment & Operations Manual", new_x="LMARGIN", new_y="NEXT", align="C")

# Sub-bar Info
pdf.set_y(98)
pdf.set_font("helvetica", "B", 11)
pdf.set_text_color(24, 28, 36)
pdf.cell(0, 10, "ENTERPRISE SPECIFICATION - LINUX SYSTEMS (CROSS-DISTRO)", new_x="LMARGIN", new_y="NEXT", align="C")

# Metadata details
pdf.set_y(155)
pdf.set_font("helvetica", "", 12)
pdf.set_text_color(200, 200, 200)

metadata = [
    ("Target Platform", "Ubuntu / Debian / RHEL / Fedora / Arch Linux"),
    ("Document Type", "System Configuration & Verification Guide"),
    ("Script Version", "v3.0 (Production-Ready Edition)"),
    ("Author", "b1swa (sandipbiswa10@gmail.com)"),
    ("Created Date", "May 30, 2026"),
    ("Classification", "Internal Technical Reference")
]

for label, val in metadata:
    pdf.set_x(35)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(45, 8, f"{label}:", new_x="RIGHT", new_y="TOP")
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 8, val, new_x="LMARGIN", new_y="NEXT")

# Bottom strip
pdf.set_fill_color(114, 9, 183) # Cyberpunk purple accent
pdf.rect(0, 278, 210, 19, "F")

# ==============================================================================
# PAGE 2: TABLE OF CONTENTS & VERSION EVOLUTION
# ==============================================================================
pdf.add_page()
pdf.set_text_color(0, 0, 0)
pdf.set_font("helvetica", "B", 20)
pdf.cell(0, 15, "Table of Contents & Version Evolution", new_x="LMARGIN", new_y="NEXT", align="L")
pdf.ln(3)

toc_items = [
    ("1. Table of Contents & Version Evolution", "Page 2"),
    ("2. Concept Dictionary & Plain English Analogies", "Page 3"),
    ("3. Architecture Overview & Prerequisites", "Page 4"),
    ("4. Step-by-Step Installation Guide", "Page 5"),
    ("5. Interactive Configuration Wizard Walkthrough", "Page 6"),
    ("6. Configuration Reference & Static IP Details", "Page 8"),
    ("7. Database Backends & PM2 Process Management", "Page 9"),
    ("8. Reverse Proxy, SSL & Security Best Practices", "Page 10"),
    ("9. Backup, Recovery & Firewall Configuration", "Page 11"),
    ("10. System Debugging & Service Operations", "Page 12"),
    ("11. Web UI Onboarding & Initial Configuration", "Page 13"),
    ("12. FAQ, File Reference, & Uninstallation", "Page 15")
]

for title, page in toc_items:
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(140, 7, title, new_x="RIGHT", new_y="TOP")
    pdf.set_font("helvetica", "I", 11)
    pdf.cell(0, 7, page, new_x="LMARGIN", new_y="NEXT", align="R")
pdf.ln(8)

pdf.chapter_title("1", "Version History & Script Evolution")
pdf.add_paragraph("The Native n8n Setup Suite has evolved through three iterations to address security, networking, and production reliability concerns.")

pdf.add_bullet("Version 1.0", "Baseline setup. Captured parameters (port, webhook) via whiptail, installed Node.js, and started n8n under PM2. Included no support for custom databases or secure credentials keys.")
pdf.add_bullet("Version 2.0", "Introduced custom network configuration (Static IP via Netplan/nmcli), secure .env management at /etc/n8n/.env with 600 permissions, automated daily backups with retention, and helper scripts.")
pdf.add_bullet("Version 3.0", "Added automated Nginx reverse proxy configurations with WebSocket headers, Certbot SSL automation, PM2 Log Rotation (pm2-logrotate), custom Node memory limits, and a clean uninstall script.")

# ==============================================================================
# PAGE 3: CONCEPT DICTIONARY (PLAIN ENGLISH ANALOGIES)
# ==============================================================================
pdf.add_page()
pdf.chapter_title("2", "Concept Dictionary (Plain English Analogies)")
pdf.add_paragraph("To make this deployment manual accessible to everyone, we explain core technical concepts using everyday analogies:")

pdf.add_bullet("Server Port (e.g. 5678)", "Imagine your server computer is a large apartment building. The 'Port' is like an individual apartment number. n8n lives inside apartment number 5678, waiting to receive visitors.")
pdf.add_bullet("Nginx Proxy", "Think of Nginx as a friendly receptionist sitting in the building's lobby. When external users visit your domain, Nginx greets them at the main entrance (Port 80/443) and safely guides them back to n8n's apartment (Port 5678).")
pdf.add_bullet("Database Backend", "This is n8n's digital filing cabinet. SQLite is a small cabinet in the room (good for small test files), whereas PostgreSQL is a secure filing room down in the basement (great for millions of files).")
pdf.add_bullet("PM2 Daemon Manager", "Think of PM2 as a security guard who watches n8n 24 hours a day. If n8n trips and falls down (crashes), the guard immediately dusts it off and helps it stand back up (restarts it).")
pdf.add_bullet("Let's Encrypt SSL", "This is like a lockable security envelope. Instead of sending messages on post-cards that anyone can read, SSL wraps all network traffic inside encrypted envelopes.")

# ==============================================================================
# PAGE 4: ARCHITECTURE & PREREQUISITES
# ==============================================================================
pdf.add_page()
pdf.chapter_title("3", "Architecture Overview & System Prerequisites")

pdf.add_paragraph("A 'Native' installation executes n8n directly on your server's Linux operating system without virtual barriers. This reduces RAM and CPU overhead, allowing files and workflow webhooks to run faster.")

# Visual Architecture Diagram (Dynamic Y Position)
start_y = pdf.get_y() + 5
pdf.set_fill_color(240, 240, 240)
pdf.set_draw_color(100, 100, 100)

# 1. External Clients
pdf.rect(15, start_y, 45, 20, "DF")
pdf.set_font("helvetica", "B", 8)
pdf.text(20, start_y + 9, "External Clients")
pdf.text(20, start_y + 14, "& Webhooks")

# Arrow 1
pdf.line(60, start_y + 10, 75, start_y + 10)
pdf.line(72, start_y + 7, 75, start_y + 10)
pdf.line(72, start_y + 13, 75, start_y + 10)

# 2. Nginx
pdf.rect(75, start_y, 45, 20, "DF")
pdf.text(80, start_y + 9, "Nginx Reverse Proxy")
pdf.text(80, start_y + 14, "Ports: 80 / 443")

# Arrow 2
pdf.line(120, start_y + 10, 135, start_y + 10)
pdf.line(132, start_y + 7, 135, start_y + 10)
pdf.line(132, start_y + 13, 135, start_y + 10)

# 3. n8n Node Server
pdf.rect(135, start_y, 55, 20, "DF")
pdf.text(140, start_y + 9, "n8n Node.js Engine")
pdf.text(140, start_y + 14, "Port: 5678 (Internal)")

# Arrow 3 (Down to DB)
pdf.line(162, start_y + 20, 162, start_y + 33)
pdf.line(159, start_y + 30, 162, start_y + 33)
pdf.line(165, start_y + 30, 162, start_y + 33)

# 4. Database Layer
pdf.rect(135, start_y + 33, 55, 20, "DF")
pdf.text(140, start_y + 42, "Database Backend")
pdf.text(140, start_y + 47, "SQLite / PostgreSQL")

pdf.set_y(start_y + 58)
pdf.ln(5)

pdf.set_font("helvetica", "B", 12)
pdf.set_text_color(50, 50, 50)
pdf.cell(0, 8, "Minimum Hardware & System Requirements", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "", 10)

pdf.add_bullet("CPU (Processor)", "Minimum 1 processor core. Like a brain, more cores allow n8n to think about and run multiple automation tasks at the same time.")
pdf.add_bullet("RAM (Memory)", "Minimum 1 Gigabyte (GB) of RAM. If you choose a PostgreSQL database, 2 GB is highly recommended so both programs have plenty of room to work.")
pdf.add_bullet("Linux Distributions", "Works on Ubuntu 20.04+, Debian 11+, Fedora 38+, CentOS Stream 9, Red Hat Enterprise Linux 8/9, or Arch Linux.")
pdf.add_bullet("Root Access", "Administrator rights (sudo privileges) are required because the setup script installs core components and adjusts server security gates.")

pdf.add_callout("Did You Know?", [
    "Container software (like Docker) adds translation layers that can delay incoming network webhooks by up to 5 milliseconds.",
    "Native Linux deployments remove these layers, making n8n react instantly to external automation signals."
], "did_you_know")

# ==============================================================================
# PAGE 5: DETAILED STEP-BY-STEP INSTALLATION GUIDE
# ==============================================================================
pdf.add_page()
pdf.chapter_title("4", "Step-by-Step Installation Guide")

pdf.add_paragraph("Deploying n8n natively is a highly orchestrated procedure split across 11 discrete phases, managed by our automated installer script. Below is the operational sequence:")

pdf.add_bullet("Phase 1 - System Checks", "Inspects package managers (apt, dnf, yum, pacman) and installs baseline networking utilities (curl, wget, gnupg2, and whiptail).")
pdf.add_bullet("Phase 2 - Node.js Install", "Checks for Node.js. If missing or older than v18, automatically registers NodeSource v20 repositories and installs Node.js and NPM globally.")
pdf.add_bullet("Phase 3 - Database Config", "If PostgreSQL is chosen, it installs packages, sets up database storage folders, creates a database named 'n8n', and assigns users secure passwords.")
pdf.add_bullet("Phase 4 - NPM Install", "Installs PM2 process manager and the n8n application core globally on the machine via Node Package Manager (NPM).")
pdf.add_bullet("Phase 5 - Config Environment", "Creates the configuration folder at /etc/n8n/ and writes the .env file. Generates a secure, random 64-character encryption key.")
pdf.add_bullet("Phase 6 - PM2 Daemon setup", "Configures startup scripts, sets up the PM2 service, limits Node process memory, and activates automatic daily log rotation.")
pdf.add_bullet("Phase 7 - Firewall configuration", "Finds the active security firewall (UFW, Firewalld, iptables) and opens the n8n port, HTTP port, and HTTPS port.")
pdf.add_bullet("Phase 8 - Reverse Proxy Setup", "Installs Nginx, creates configuration files mapping web traffic, and starts the service.")
pdf.add_bullet("Phase 9 - SSL Certbot", "Installs Let's Encrypt Certbot, verifies domain ownership, installs certificates, and configures secure HTTPS redirection.")
pdf.add_bullet("Phase 10 - Helper scripts", "Creates helper scripts under /usr/local/bin for automated updates, daily backups, and clean uninstallation.")
pdf.add_bullet("Phase 11 - Completion", "Purges installer temp files, validates that the PM2 daemon is running, and prints details.")

# ==============================================================================
# PAGES 6-13: CHAPTER 5 - INTERACTIVE CONFIGURATION WIZARD WALKTHROUGH
# ==============================================================================
pdf.add_page()
pdf.chapter_title("5", "Interactive Configuration Wizard Walkthrough")

pdf.add_paragraph("The installation script setup_n8n_native.sh uses whiptail, a console-based GUI dialog box system. It queries the administrator through graphical terminal dialog screens to collect and validate setup parameters. Below is the step-by-step walkthrough of the configuration wizard:")

wizard_steps = [
    ("1", "Welcome & System Information", "Displays the installer version, copyright/branding details, and detects key server metadata (hostname, IP address, active network interface, and detected Linux distribution)."),
    ("2", "Static IP: Selection Box", "Asks whether you want to set a Static IP for the server. A static IP ensures your webhook URLs and server access path never change."),
    ("3", "Configuration: Listener Port", "Allows setting a custom port for the n8n application to listen on. Defaults to 5678."),
    ("4", "Configuration: Webhook URL", "Allows configuring the public-facing URL where external service webhooks (e.g. GitHub, Slack) will send trigger events."),
    ("5", "PostgreSQL: Install Option", "Asks whether the script should install and configure a local PostgreSQL database server, or connect to an external one."),
    ("6", "PostgreSQL: Database Host", "Specifies the hostname or IP address of the PostgreSQL database server (defaults to localhost)."),
    ("7", "PostgreSQL: Database Port", "Specifies the network port for connecting to the PostgreSQL server (defaults to 5432)."),
    ("8", "PostgreSQL: Database Name", "Specifies the database name that n8n will create and use (defaults to n8n)."),
    ("9", "PostgreSQL: Database Username", "Specifies the database username used to connect to PostgreSQL (defaults to n8n)."),
    ("10", "PostgreSQL: Database Password", "Secure password input field to set or specify the password for the database user."),
    ("11", "Security: Basic Authentication", "Asks whether you want to enable Basic Authentication, prompting users for a username/password before loading the n8n dashboard."),
    ("12", "Basic Auth: Username", "Input field to define the basic authentication username (defaults to admin)."),
    ("13", "Basic Auth: Password Box", "Secure password input field to set the password for basic authentication."),
    ("14", "Backup: Auto-Backup option", "Prompts to enable automated daily backups of n8n configurations and data folders to /var/backups/n8n/."),
    ("15", "Backup: Cron Schedule", "Specifies the daily backup time in 24-hour format (defaults to 02:00 for 2 AM)."),
    ("16", "Reverse Proxy: Nginx Option", "Asks whether you want to install and configure Nginx as a reverse proxy, mapping public traffic (ports 80/443) to n8n's backend port."),
    ("17", "Reverse Proxy: Domain name", "Input field for the domain or subdomain name (e.g. n8n.yourdomain.com) or fallback IP address."),
    ("18", "SSL: Let's Encrypt Option", "Asks whether to run Certbot to retrieve a free Let's Encrypt SSL certificate and configure HTTPS redirect."),
    ("19", "SSL: Administrator Email", "Input field for your email address to receive renewal notifications and alerts from Let's Encrypt."),
    ("20", "Performance: Memory Limit", "Sets a memory guard limit (e.g. 1G) after which PM2 will automatically restart the n8n daemon to prevent leaks."),
    ("21", "Configuration Review Summary", "Displays a complete summary of all collected network, database, security, and backup configurations for final validation."),
    ("22", "Installation Success Screen", "Displays the completion message with server status, access URLs, and maintenance helper commands.")
]

# Step 1
pdf.set_font("helvetica", "B", 10.5)
pdf.set_text_color(0, 119, 182)
pdf.cell(0, 6, "Step 1: Welcome & Environment Detection", new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.5)
pdf.add_paragraph("The installer detects baseline server metadata including hostname, IP, and Linux distribution. [Tip: Verify the detected network interface is correct before proceeding.]")

# Fig 1
pdf.add_figure("/home/b1swa/Documents/n8n/Image/1.png", 1, "Terminal Welcome & Environment Detection Dialog.", w=110, h=46)

steps_page6 = [
    ("2", "Static IP Choice", "Asks if you want to configure a Static IP for the server. Recommended to ensure permanent webhook access."),
    ("3", "Listener Port", "Sets a custom port for the n8n application (defaults to 5678)."),
    ("4", "Webhook URL", "Configures the public-facing domain or IP used by external services to send webhook triggers."),
    ("5", "PostgreSQL Option", "Option to configure a local PostgreSQL database server, or link to an external instance."),
    ("6", "DB Host", "Hostname/IP of the database server (defaults to localhost)."),
    ("7", "DB Port", "Network port for database connection (defaults to 5432)."),
    ("8", "DB Name", "The PostgreSQL database name for n8n (defaults to n8n)."),
    ("9", "DB Username", "Database username used to log in (defaults to n8n)."),
    ("10", "DB Password", "Password input to authenticate with the database.")
]

for num, title, desc in steps_page6:
    pdf.set_font("helvetica", "B", 10.5)
    pdf.set_text_color(0, 119, 182)
    pdf.cell(0, 6, f"Step {num}: {title}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.5)
    pdf.add_paragraph(desc)

steps_page7 = [
    ("11", "Security: Basic Authentication", "Asks whether you want to enable Basic Authentication, prompting users for a username/password before loading the n8n dashboard."),
    ("12", "Basic Auth: Username", "Input field to define the basic authentication username (defaults to admin)."),
    ("13", "Basic Auth: Password Box", "Secure password input field to set the password for basic authentication."),
    ("14", "Backup: Auto-Backup option", "Prompts to enable automated daily backups of n8n configurations and data folders to /var/backups/n8n/."),
    ("15", "Backup: Cron Schedule", "Specifies the daily backup time in 24-hour format (defaults to 02:00 for 2 AM)."),
    ("16", "Reverse Proxy: Nginx Option", "Asks whether you want to install and configure Nginx as a reverse proxy, mapping public traffic (ports 80/443) to n8n's backend port."),
    ("17", "Reverse Proxy: Domain name", "Input field for the domain or subdomain name (e.g. n8n.yourdomain.com) or fallback IP address."),
    ("18", "SSL: Let's Encrypt Option", "Asks whether to run Certbot to retrieve a free Let's Encrypt SSL certificate and configure HTTPS redirect."),
    ("19", "SSL: Administrator Email", "Input field for your email address to receive renewal notifications and alerts from Let's Encrypt."),
    ("20", "Performance: Memory Limit", "Sets a memory guard limit (e.g. 1G) after which PM2 will automatically restart the n8n daemon to prevent leaks.")
]

for num, title, desc in steps_page7:
    pdf.set_font("helvetica", "B", 10.5)
    pdf.set_text_color(0, 119, 182)
    pdf.cell(0, 6, f"Step {num}: {title}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.5)
    pdf.add_paragraph(desc)

# Step 21 & Fig 2
pdf.set_font("helvetica", "B", 10.5)
pdf.set_text_color(0, 119, 182)
pdf.cell(0, 6, "Step 21: Configuration Review Summary", new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.5)
pdf.add_paragraph("Displays a complete summary of all collected network, database, security, and backup configurations for final validation before starting the installation.")
pdf.add_figure("/home/b1swa/Documents/n8n/Image/21.png", 2, "Installation Parameter Summary & Review.", w=110, h=46)

# Step 22 & Fig 3
pdf.set_font("helvetica", "B", 10.5)
pdf.set_text_color(0, 119, 182)
pdf.cell(0, 6, "Step 22: Installation Success Screen", new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.5)
pdf.add_paragraph("Displays the completion message with server status, access URLs, and maintenance helper commands.")
pdf.add_figure("/home/b1swa/Documents/n8n/Image/22.png", 3, "Completion Output and Access Details.", w=110, h=46)

# ==============================================================================
# PAGE 7: CONFIGURATION REFERENCE & STATIC IP SPECIFICATIONS
# ==============================================================================
pdf.add_page()
pdf.chapter_title("6", "Configuration Reference & Static IP Details")

pdf.add_paragraph("All configuration parameters for the native service are written inside a consolidated environment file at /etc/n8n/.env. This keeps database logins, encryption passwords, and custom ports secure.")

# Config Table
pdf.set_font("helvetica", "B", 10)
pdf.cell(60, 6, "Variable Name", border=1, align="L", new_x="RIGHT", new_y="TOP")
pdf.cell(130, 6, "Purpose & Context", border=1, align="L", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "", 9)

config_vars = [
    ("N8N_PORT", "Internal port where n8n listens (Default: 5678)."),
    ("N8N_HOST", "Listening IP. Set to 0.0.0.0 to accept traffic from all interfaces."),
    ("WEBHOOK_URL", "Public URL used by external APIs (e.g. Slack) to trigger workflows."),
    ("N8N_ENCRYPTION_KEY", "Generated key used to encrypt workflow credentials in the DB."),
    ("N8N_BASIC_AUTH_ACTIVE", "Set to true to prompt users for credentials before loading n8n."),
    ("DB_TYPE", "Database engine. Set to 'postgresdb' or defaults to SQLite.")
]

for var, desc in config_vars:
    pdf.cell(60, 6, var, border=1, align="L", new_x="RIGHT", new_y="TOP")
    pdf.cell(130, 6, desc, border=1, align="L", new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)

pdf.set_font("helvetica", "B", 12)
pdf.cell(0, 8, "Static IP Configuration Details", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "", 10)
pdf.add_paragraph("A Static IP address is an address that never changes. If your server's IP keeps changing (Dynamic IP), webhook integrations will break. The installer automates configuration across three platforms:")

pdf.add_bullet("Debian/Ubuntu (Netplan)", "Creates a configuration file at /etc/netplan/01-n8n-static.yaml, assigning static addresses, gateway, and nameservers. Runs 'netplan apply'.")
pdf.add_bullet("RHEL/Fedora (NetworkManager)", "Uses nmcli commands to adjust properties of the active network profile, setting IPv4 address, DNS, and manual IP assignment method.")
pdf.add_bullet("Arch/Generic Fallback", "Uses direct 'ip addr' and 'ip route' commands to apply configurations immediately to the interface.")

pdf.add_callout("Pro Tip", [
    "If Netplan setup fails or you want to review configuration issues, you can run:",
    "  netplan --debug try"
], "trick")

# ==============================================================================
# PAGE 8: DATABASE BACKENDS & PM2 MANAGEMENT
# ==============================================================================
pdf.add_page()
pdf.chapter_title("7", "Database Backends & PM2 Process Management")

pdf.add_paragraph("Choosing the right database backend depends on how many workflows you plan to run. SQLite is simple and stores everything in a single file on disk. PostgreSQL runs as a standalone engine, perfect for high concurrency and heavy workflows.")

# Database Table
pdf.set_font("helvetica", "B", 10)
pdf.cell(40, 6, "Feature", border=1, align="C", new_x="RIGHT", new_y="TOP")
pdf.cell(75, 6, "SQLite Backend", border=1, align="C", new_x="RIGHT", new_y="TOP")
pdf.cell(75, 6, "PostgreSQL Backend", border=1, align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "", 9)

db_comp = [
    ("Storage Pattern", "Single flat file (~/.n8n/database.sqlite)", "Server process with access permissions"),
    ("Concurrency", "Locks database on write operations", "Supports high concurrent query traffic"),
    ("Performance", "Fast for low-volume testing", "Optimized for large workflow history logs"),
    ("Configuration", "Zero config, automated file creation", "Requires host, port, DB user, & password")
]

for feat, sql, pg in db_comp:
    pdf.cell(40, 6, feat, border=1, align="L", new_x="RIGHT", new_y="TOP")
    pdf.cell(75, 6, sql, border=1, align="L", new_x="RIGHT", new_y="TOP")
    pdf.cell(75, 6, pg, border=1, align="L", new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)

pdf.set_font("helvetica", "B", 12)
pdf.cell(0, 8, "PM2 Process Daemon Configuration", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "", 10)
pdf.add_paragraph("PM2 is a process manager that runs in the background. It keeps n8n active constantly, restarting it if it experiences a memory issue or system restart.")

pdf.add_bullet("Memory Limit Guard", "Configured via '--max-memory-restart 1G'. If n8n consumes more than 1GB of memory, PM2 will automatically restart it to keep the system healthy.")
pdf.add_bullet("PM2 Log Rotation", "The setup configures 'pm2-logrotate' to keep server logs under 10 Megabytes (MB) per file, saving up to 7 historical logs to prevent filling up the system drive.")
pdf.add_bullet("Boot Persistence", "Registers n8n as a systemd service so it boots automatically when the computer turns on.")

# ==============================================================================
# PAGE 9: REVERSE PROXY, SSL & SECURITY BEST PRACTICES
# ==============================================================================
pdf.add_page()
pdf.chapter_title("8", "Reverse Proxy, SSL & Security Best Practices")

pdf.add_paragraph("An Nginx reverse proxy routes incoming public requests from standard ports (80/443) to n8n's internal port (5678). This approach hides backend application ports, enables SSL encryption, and manages connections efficiently.")

pdf.set_font("helvetica", "B", 12)
pdf.cell(0, 8, "Nginx Proxy Configuration Block Details", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "", 10)
pdf.add_paragraph("Because n8n relies on WebSockets for real-time dashboard updates, the Nginx configuration must include specific proxy headers. Below is the Nginx server block template generated by the installer:")

code_ex = [
    "server {",
    "    listen 80;",
    "    server_name n8n.yourdomain.com;",
    "    location / {",
    "        proxy_pass http://127.0.0.1:5678;",
    "        proxy_http_version 1.1;",
    "        proxy_set_header Upgrade $http_upgrade;",
    "        proxy_set_header Connection \"upgrade\";",
    "        proxy_set_header Host $host;",
    "        proxy_set_header X-Real-IP $remote_addr;",
    "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
    "        proxy_set_header X-Forwarded-Proto $scheme;",
    "        proxy_buffering off;",
    "    }",
    "}"
]
pdf.add_code_block(code_ex)

pdf.set_font("helvetica", "B", 12)
pdf.cell(0, 8, "Let's Encrypt SSL Integration", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "", 10)
pdf.add_paragraph("The installer script automatically downloads certbot and its Nginx plugin. Certbot validates the domain ownership, retrieves the TLS/SSL certificates, configures redirection blocks to force HTTPS, and schedules a systemd timer for automatic renewals.")

pdf.set_font("helvetica", "B", 12)
pdf.cell(0, 8, "Security Best Practices", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "", 10)
pdf.add_bullet("Configuration Security", "Ensure /etc/n8n/.env is set to 'chmod 600' so only root or sudo users can read database credentials and encryption keys.")
pdf.add_bullet("PM2 Execution Identity", "Run PM2 under a dedicated standard user account (using the SUDO_USER variable) rather than root, limiting potential damage in case of a vulnerability.")

# ==============================================================================
# PAGE 10: BACKUP, RECOVERY, & FIREWALL CONFIGURATION
# ==============================================================================
pdf.add_page()
pdf.chapter_title("9", "Backup, Recovery & Firewall Configuration")

pdf.add_paragraph("n8n stores workflow credentials, execution histories, custom workflows, and active tokens in its data directory (~/.n8n). The v3.0 installer sets up a backup system to prevent data loss.")

pdf.set_font("helvetica", "B", 12)
pdf.cell(0, 8, "Backup Mechanics & Retention Policies", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "", 10)
pdf.add_bullet("Scheduled Execution", "Installs a script at /usr/local/bin/n8n_backup.sh that runs daily via cron (configured to run at 2 AM or your custom schedule).")
pdf.add_bullet("Retention Management", "Archives the entire n8n database folder into a tar.gz file. It keeps only the last 7 daily archives, automatically deleting older files to manage disk space.")
pdf.add_bullet("Restore Execution Workflow", "To restore a backup, stop the n8n daemon, extract the archive back to ~/.n8n, and restart PM2:")

restore_cmd = [
    "pm2 stop n8n",
    "tar -xzf /var/backups/n8n/n8n_backup_[timestamp].tar.gz -C ~/.n8n/",
    "pm2 start n8n"
]
pdf.add_code_block(restore_cmd)

pdf.set_font("helvetica", "B", 12)
pdf.cell(0, 8, "Firewall Configuration", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "", 10)
pdf.add_paragraph("The installer detects the active firewall utility and opens the necessary ports:")
pdf.add_bullet("UFW (Ubuntu/Debian)", "Allows n8n port (e.g. 5678) and web ports 80/443 (HTTP/HTTPS) if proxy is enabled.")
pdf.add_bullet("Firewalld (Fedora/RHEL)", "Adds runtime and permanent rules for port 5678, HTTP, and HTTPS services, then reloads the configuration.")
pdf.add_bullet("iptables (Arch Linux)", "Injects filter rules into the INPUT chain and uses netfilter-persistent to save configuration states.")

# ==============================================================================
# PAGE 11: COMPREHENSIVE DEBUGGING & SERVICE OPERATIONS
# ==============================================================================
pdf.add_page()
pdf.chapter_title("10", "System Debugging & Service Operations")
pdf.add_paragraph("This chapter lists critical operational commands for troubleshooting, process tracking, and database querying within the native environment:")

pdf.add_paragraph("PM2 Monitoring & Logging:")
pdf.add_bullet("pm2 status / restart n8n", "Lists active Node.js processes or restarts the n8n core daemon process.")
pdf.add_bullet("pm2 logs n8n / flush n8n", "Streams real-time server console output or flushes trailing service logs.")
pdf.add_bullet("pm2 info n8n", "Exposes uptime, install directories, log locations, and active env variables.")

pdf.add_paragraph("Network & Database Diagnostics:")
pdf.add_bullet("ss -tulpn | grep 5678", "Checks if n8n is listening on the expected port (or use netstat).")
pdf.add_bullet("curl -I http://localhost:5678", "Tests the local n8n HTTP interface connection response directly.")
pdf.add_bullet("systemctl status postgresql", "Validates that the database backend daemon is running.")
pdf.add_bullet("sudo -u postgres psql -d n8n -c '\\dt'", "Exposes n8n table structures to verify database connectivity.")

pdf.add_paragraph("System Troubleshooting Actions:")
pdf.add_bullet("Error EADDRINUSE", "Port conflict. Run 'fuser -k 5678/tcp' to kill blocking processes, or edit N8N_PORT in /etc/n8n/.env.")
pdf.add_bullet("Node Environment Info", "Confirm baseline language dependencies via 'n8n --version' and 'node -v'.")
pdf.add_bullet("DB Connection Refused", "Ensure the DB service is active and check the DB host/user credentials in /etc/n8n/.env.")

# ==============================================================================
# CHAPTER 11 - WEB UI ONBOARDING & INITIAL CONFIGURATION
# ==============================================================================
pdf.add_page()
pdf.chapter_title("11", "Web UI Onboarding & Initial Configuration")
pdf.add_paragraph("Once the server installation is complete, the remaining configuration is performed via the web browser. Below is the step-by-step onboarding walkthrough:")

# Step 23 & Fig 4
pdf.set_font("helvetica", "B", 10.5)
pdf.set_text_color(0, 119, 182)
pdf.cell(0, 6, "Step 23: Owner Account Creation", new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.5)
pdf.add_paragraph("Upon first visiting your n8n URL, you will be prompted to create the primary administrator/owner account. Provide your email, name, and a strong password. This credential set is stored securely in the local database.")
pdf.add_figure("/home/b1swa/Documents/n8n/Image/23.png", 4, "Web Browser Initial Admin User Registration.", w=70, h=80)

# Steps 24, 25
pdf.set_font("helvetica", "B", 10.5)
pdf.set_text_color(0, 119, 182)
pdf.cell(0, 6, "Step 24: Personalization Questionnaire", new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.5)
pdf.add_paragraph("n8n asks a series of optional onboarding questions regarding your automation role, department, and company size to customize template recommendations.")

pdf.set_font("helvetica", "B", 10.5)
pdf.set_text_color(0, 119, 182)
pdf.cell(0, 6, "Step 25: Community/Free License Key Modal", new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.5)
pdf.add_paragraph("A modal popup offers to activate a free license key. This unlocks advanced node features and triggers. You can register your email to retrieve this key instantly.")

# Step 26 & Fig 5
pdf.set_font("helvetica", "B", 10.5)
pdf.set_text_color(0, 119, 182)
pdf.cell(0, 6, "Step 26: Main Dashboard & Workspace", new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.5)
pdf.add_paragraph("The primary n8n canvas. Here you can start building, importing, or testing workflow automations and integrations.")
pdf.add_figure("/home/b1swa/Documents/n8n/Image/26.png", 5, "Loaded n8n Visual Automation Canvas.", w=80, h=80)

# Step 27
pdf.set_font("helvetica", "B", 10.5)
pdf.set_text_color(0, 119, 182)
pdf.cell(0, 6, "Step 27: License Key Verification Email", new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.5)
pdf.add_paragraph("An automated confirmation email containing your personal activation link and registration verification is sent to the registered address.")

# ==============================================================================
# PAGE 22: CHAPTER 12 - FAQ, FILE REFERENCE, & UNINSTALLATION
# ==============================================================================
pdf.add_page()
pdf.chapter_title("12", "FAQ, File Reference, & Uninstallation")

pdf.set_font("helvetica", "B", 12)
pdf.cell(0, 8, "Frequently Asked Questions (FAQ)", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "", 9.5)
pdf.add_bullet("Q: Can I change database backends?", "Yes. Export workflows via the admin panel, change DB parameters in /etc/n8n/.env, and re-import.")
pdf.add_bullet("Q: How do I upgrade n8n version?", "Execute 'sudo n8n_update.sh'. The script automatically stops the daemon, downloads the latest npm package, and restarts the engine.")
pdf.add_bullet("Q: Why does Certbot fail or show a warning with my server's IP address?", "Let's Encrypt only issues SSL certificates for registered domain names (e.g. n8n.domain.com). It does not issue certificates for bare IP addresses (e.g. 10.225.157.51). In this case, Nginx will fallback to serving n8n over standard HTTP on port 80.")
pdf.add_bullet("Q: How do I verify n8n and Nginx are fully online?", "You can test the HTTP response codes directly using curl: 'curl -I http://localhost:5678' (n8n port) and 'curl -I http://localhost' (Nginx port). Both should return an 'HTTP/1.1 200 OK' response code.")

pdf.set_font("helvetica", "B", 12)
pdf.cell(0, 8, "Uninstalling the native setup", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "", 10)
pdf.add_paragraph("To cleanly remove the n8n application, dependencies, backup scripts, and cron logs, execute the uninstall script. Note that your user configuration directory (~/.n8n) containing workflow files is preserved to avoid data loss:")
pdf.add_bullet("Uninstall Helper", "Execute 'sudo n8n_uninstall.sh' and follow the interactive prompt to purge the system configuration.")

pdf.set_font("helvetica", "B", 12)
pdf.cell(0, 8, "System File Reference Map", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("helvetica", "", 9)

# File Reference Table
pdf.cell(70, 6, "File / Path Location", border=1, align="L", new_x="RIGHT", new_y="TOP")
pdf.cell(120, 6, "Description & Purpose", border=1, align="L", new_x="LMARGIN", new_y="NEXT")
file_refs = [
    ("/etc/n8n/.env", "Central environment file containing ports and database credentials."),
    ("/usr/local/bin/start_n8n.sh", "Startup script loaded by PM2 to export configuration variables."),
    ("/usr/local/bin/n8n_backup.sh", "Daily archiving utility that backs up ~/.n8n/ to /var/backups/n8n/."),
    ("/usr/local/bin/n8n_update.sh", "Helper script to update n8n to the latest version via NPM."),
    ("/usr/local/bin/n8n_uninstall.sh", "Uninstallation script that cleans up configurations and Nginx blocks.")
]
for fpath, fdesc in file_refs:
    pdf.cell(70, 6, fpath, border=1, align="L", new_x="RIGHT", new_y="TOP")
    pdf.cell(120, 6, fdesc, border=1, align="L", new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)

# Save the PDF output
pdf.output("/home/b1swa/b1swa_SerConfig/8n8 /n8n_deployment_guide.pdf")
pdf.output("/home/b1swa/Documents/n8n/n8n_deployment_guide.pdf")
print("PDF COMPLETED AND SAVED")
