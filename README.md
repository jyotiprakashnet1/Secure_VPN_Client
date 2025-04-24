# 🔐 Secure VPN Client with Certificate-Based Authentication & Threat Monitoring

This project provides a secure VPN client-server solution built using **OpenVPN**, **Easy-RSA**, and a **Flask-based UI**. Clients can generate certificate requests, download VPN config files, and connect securely. The Admin can manage CSRs, monitor connections, and revoke certificates.

---

## 🛠️ Dependencies & Prerequisites

Ensure you're using **Ubuntu 22.04+** or equivalent.

### 🔧 System Packages
Install required packages:
```bash
sudo apt update
sudo apt install openvpn easy-rsa python3 python3-venv python3-pip net-tools

Project structure
.
├── backend/           # Flask backend
│   ├── routes/        # Flask routes for client/admin
│   ├── templates/     # HTML UI pages
│   ├── utils/         # Scripts: CSR, signing, revoke, ovpn
│   └── venv/          # Python virtual environment
├── openvpn/
│   ├── client/        # Stores .ovpn files and client certs
│   └── server/        # Contains ca.crt, server.crt, dh.pem, ta.key
├── openvpn-ca/        # Easy-RSA PKI CA setup
│   └── pki/           # Keys, certs, requests
Certificate Authority (CA) Setup:
    Step 1: Initialize Easy-RSA
VPN Server Setup:
    Step 2: Build Server Cert + Keys
    Step 3: Configure Server
    Step 4: Start the Server
Flask UI Setup:
    Step 5: Create and Activate Virtual Environment
    Step 6: Run Flask App
###################################################################
👤 Client UI Usage:
    Navigate to /client
    Enter Common Name
    Click Request Certificate (generates CSR)
    Wait for Admin to sign CSR
    After approval, Download .ovpn
    Connect using: sudo openvpn --config client1.ovpn (Which will run in backend from UI)
################################################################
🛡️ Admin UI Usage

    Navigate to /admin
    View and sign pending requests
    Monitor:
        Connected clients
        TLS version, Cipher
        IP assigned
        Session start/disconnect
    Revoke certificates when needed

#############################################
🛠️ Utility Commands:
    Sign Client CSR: 
        cd openvpn-ca
        $./easyrsa sign-req client <common_name>
    Revoke Certificate:
        ./easyrsa revoke <common_name>
        ./easyrsa gen-crl

🧪 Debugging & Monitoring:
    Log file: /run/openvpn/server.status
    Use tcpdump or netstat to view port 1194
    sudo journalctl -u openvpn@server #---- for logs

