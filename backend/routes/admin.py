from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
import subprocess
import os
from utils.generate_ovpn import generate_ovpn

admin_bp = Blueprint("admin", __name__)

@admin_bp.route('/')
def admin_page():
    return render_template("admin.html")

def admin_page():
    issued_dir = "/home/prakash/Documents/Secure_VPN_client/openvpn-ca/pki/issued"
    try:
        certs = [f for f in os.listdir(issued_dir) if f.endswith(".crt")]
        issued_clients = [os.path.splitext(f)[0] for f in certs]
    except Exception:
        issued_clients = []

    return render_template("admin.html", issued_clients=issued_clients)

@admin_bp.route('/sign', methods=['POST'])
def sign_cert():
    common_name = request.form.get('common_name')
    try:
        cmd = f"cd /home/prakash/Documents/Secure_VPN_client/openvpn-ca && echo yes | ./easyrsa sign-req client {common_name}"
        subprocess.run(cmd, shell=True, check=True)
        flash(f"Certificate signed for {common_name}", "success")
    except subprocess.CalledProcessError as e:
        flash(f"Error signing cert: {str(e)}", "error")
    return redirect(url_for('admin.admin_page'))

@admin_bp.route('/clients', methods=['GET'])
@admin_bp.route('/connected', methods=['GET'])
def view_connected_clients():
    status_file = "/run/openvpn/server.status"
    clients = []

    try:
        with open(status_file, "r") as f:
            lines = f.readlines()

        start = False
        for line in lines:
            if "Common Name,Real Address" in line:
                start = True
                continue
            if start:
                if line.strip() == "ROUTING TABLE":
                    break  # stop after client list
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    clients.append(parts[0])  # Common Name

        flash(f"Connected clients: {', '.join(clients) if clients else 'None'}", "info")
    except Exception as e:
        flash(f"Error reading status: {e}", "error")

    return redirect(url_for("admin.admin_page"))


@admin_bp.route('/revoke', methods=['POST'])
def revoke_cert():
    common_name = request.form.get("common_name")
    try:
        cmd = f"cd /home/prakash/Documents/Secure_VPN_client/openv-ca && ./easyrsa revoke {common_name} && ./easyrsa gen-crl"
        subprocess.run(cmd, shell=True, check=True)

        # Move updated CRL to OpenVPN server directory
        subprocess.run("cp /home/prakash/Documents/Secure_VPN_client/openv-ca/pki/crl.pem /etc/openvpn/server/", shell=True, check=True)

        flash(f"Revoked and CRL updated for {common_name}", "success")
    except subprocess.CalledProcessError as e:
        flash(f"Revocation failed: {str(e)}", "error")
    return redirect(url_for('admin.admin_page'))

# from flask import send_file


@admin_bp.route('/generate-ovpn/<common_name>', methods=['GET'])
def download_ovpn(common_name):
    try:
        ovpn_path = generate_ovpn(common_name)
        return send_file(ovpn_path, as_attachment=True)
    except Exception as e:
        flash(f"Failed to generate config: {e}", "error")
        return redirect(url_for('admin.admin_page'))

@admin_bp.route('/pending', methods=['GET'])
def view_pending_csrs():
    req_dir = "/home/prakash/Documents/Secure_VPN_client/openvpn-ca/pki/reqs"
    try:
        csrs = [f for f in os.listdir(req_dir) if f.endswith(".req")]
        # Strip .req extension to get common names
        pending_clients = [os.path.splitext(f)[0] for f in csrs]
        return render_template("admin.html", pending_clients=pending_clients)
    except Exception as e:
        flash(f"Error reading CSR directory: {e}", "error")
        return redirect(url_for("admin.admin_page"))

@admin_bp.route('/disconnect', methods=['POST'])
def disconnect_vpn():
    try:
        # Attempt to kill any running OpenVPN processes
        subprocess.run("sudo pkill openvpn", shell=True, check=True)
        flash("VPN connection terminated.", "success")
    except subprocess.CalledProcessError as e:
        flash(f"Failed to disconnect: {e}", "error")
    return redirect(url_for('admin.admin_page'))

@admin_bp.route('/start', methods=['POST'])
def start_vpn():
    try:
        # Attempt to kill any running OpenVPN processes
        subprocess.run("sudo systemctl start openvpn@server", shell=True, check=True)
        flash("VPN server started.", "success")
    except subprocess.CalledProcessError as e:
        flash(f"Failed to start: {e}", "error")
    return redirect(url_for('admin.admin_page'))