from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
import subprocess
import os
from utils.generate_ovpn import generate_ovpn

admin_bp = Blueprint("admin", __name__)

@admin_bp.route('/')
def admin_page():
    return render_template("admin.html")

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


@admin_bp.route('/revoke', methods=['POST'])
def revoke_cert():
    common_name = request.form.get("common_name")
    try:
        cmd = f"cd /home/prakash/Documents/Secure_VPN_client/openvpn-ca && echo yes | ./easyrsa revoke {common_name} && ./easyrsa gen-crl"
        subprocess.run(cmd, shell=True, check=True)

        # Move updated CRL to OpenVPN server directory
        subprocess.run("cp /home/prakash/Documents/Secure_VPN_client/openvpn-ca/pki/crl.pem /etc/openvpn/server/", shell=True, check=True)

        flash(f"Revoked and CRL updated for {common_name}", "success")
    except subprocess.CalledProcessError as e:
        flash(f"Revocation failed: {str(e)}", "error")
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


from utils.log_parser import parse_openvpn_status

@admin_bp.route('/tls-sessions', methods=['GET'])
def view_tls_sessions():
    sessions = parse_openvpn_status()
    return render_template("tls_sessions.html", sessions=sessions)

@admin_bp.route('/admin/clients', methods=['GET'])
def admin_clients():
    sessions = parse_openvpn_status()
    return render_template('admin.html', sessions=sessions)

@admin_bp.route("/tls-sessions")
def tls_sessions():
    sessions = parse_openvpn_status()
    return render_template("tls-sessions.html", sessions=sessions)

@admin_bp.route('/issued', methods=['GET'])
def view_issued_certificates():
    issued_dir = "/home/prakash/Documents/Secure_VPN_client/openvpn-ca/pki/issued"
    try:
        # Get all .crt files in the 'issued' directory (issued certificates)
        issued_certs = [f for f in os.listdir(issued_dir) if f.endswith(".crt")]
        # Extract common names (remove the .crt extension)
        issued_clients = [os.path.splitext(f)[0] for f in issued_certs]
        
        return render_template("admin.html", issued_clients=issued_clients)
    except Exception as e:
        flash(f"Error reading issued certificates directory: {e}", "error")
        return redirect(url_for("admin.admin_page"))

@admin_bp.route('/revoked', methods=['GET'])
def view_revoked_certs():
    revoked_dir = "/home/prakash/Documents/Secure_VPN_client/openvpn-ca/pki/revoked/certs_by_serial"  # Path where revoked certs are stored

    try:
        # Get the list of revoked certificates (with .crl extension, or your format)
        revoked_certs = [f for f in os.listdir(revoked_dir) if f.endswith(".crt")]  # Adjust this based on your CRL extension
        revoked_clients = [os.path.splitext(f)[0] for f in revoked_certs]  # Strip .crl extension for client names
        revoked_clients_count = len(revoked_clients)

        # Fetch other data (e.g., connected clients, issued clients count, etc.)
        # connected_clients = get_connected_clients()  # Your function to fetch connected clients
        # connected_clients_count = len(connected_clients)

        # Pass data to the template
        return render_template(
            "admin.html", 
            revoked_clients=revoked_clients,  # List of revoked clients
            revoked_clients_count=revoked_clients_count,  # Count of revoked clients
            # clients=connected_clients,  # Any other data you want to show
            # clients_count=connected_clients_count
        )
    except Exception as e:
        flash(f"Error reading revoked certificate directory: {e}", "error")
        return redirect(url_for("admin.admin_page"))

#snort route for log
from utils.snort_log_parser import read_snort_alerts

@admin_bp.route("/snort-alerts")
def snort_alerts():
    alerts = read_snort_alerts()
    return render_template("admin_alerts.html", alerts=alerts)

