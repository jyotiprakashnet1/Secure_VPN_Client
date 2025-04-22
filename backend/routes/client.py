from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
# from utils.cert_ops import generate_client_cert
from utils.cert_ops import generate_csr
import os
import subprocess
# from flask import 

client_bp = Blueprint("client", __name__)

@client_bp.route('/')
def client_page():
    return render_template("client.html")

# @client_bp.route('/request-cert', methods=['POST'])
# def request_cert():
#     common_name = request.form.get('common_name')
#     if not common_name:
#         flash("Common Name is required", "error")
#         return redirect(url_for('client.client_page'))

#     out, err = generate_client_cert(common_name)
#     if err:
#         flash(f"Error: {err}", "error")
#     else:
#         flash(f"Certificate generated for: {common_name}", "success")

#     return redirect(url_for('client.client_page'))
@client_bp.route('/request-cert', methods=['POST'])
def request_cert():
    common_name = request.form.get('common_name')
    if not common_name:
        flash("Common Name is required", "error")
        return redirect(url_for('client.client_page'))

    out, err = generate_csr(common_name)
    if err:
        flash(f"Error: {err}", "error")
    else:
        flash(f"CSR generated for {common_name}. Waiting for admin approval.", "success")

    return redirect(url_for('client.client_page'))

UPLOAD_FOLDER = '/home/prakash/Documents/Secure_VPN_client/openvpn/client'
@client_bp.route('/upload-cert', methods=['POST'])
def upload_cert():
    crt_file = request.files.get('crt_file')
    key_file = request.files.get('key_file')
    common_name = request.form.get('common_name')

    if not (crt_file and key_file and common_name):
        flash("All fields are required", "error")
        return redirect(url_for('client.client_page'))

    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        crt_path = os.path.join(UPLOAD_FOLDER, f"{common_name}.crt")
        key_path = os.path.join(UPLOAD_FOLDER, f"{common_name}.key")

        crt_file.save(crt_path)
        key_file.save(key_path)

        flash("Certificate and key uploaded successfully!", "success")
    except Exception as e:
        flash(f"Upload failed: {str(e)}", "error")

    return redirect(url_for('client.client_page'))

@client_bp.route('/connect-vpn', methods=['POST'])
def connect_vpn():
    common_name = request.form.get("common_name")
    config_path = f"/home/prakash/Documents/Secure_VPN_client/openvpn/client/{common_name}.ovpn"
    pid_file = "/tmp/client_vpn.pid"

    try:
        proc = subprocess.Popen(
            ["sudo", "openvpn", "--config", config_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Save PID for later disconnect
        with open(pid_file, "w") as f:
            f.write(str(proc.pid))
        flash("VPN connection started.", "success")
    except Exception as e:
        flash(f"Failed to start VPN: {e}", "error")

    return redirect(url_for("client.client_page"))
    # if not os.path.exists(config_path):
    #     flash("Config file not found. Please upload your cert or check name.", "error")
    #     return redirect(url_for("client.client_page"))

    # try:
    #     cmd = f"sudo openvpn --config {config_path} --daemon"
    #     subprocess.run(cmd, shell=True, check=True)
    #     flash(f"VPN connection initiated for {common_name}", "success")
    # except subprocess.CalledProcessError as e:
    #     flash(f"Error starting VPN: {e}", "error")

    # return redirect(url_for("client.client_page"))

@client_bp.route('/status', methods=['GET'])
def vpn_status():
    try:
        result = subprocess.run("ifconfig", shell=True, capture_output=True, text=True)
        if "tun" in result.stdout:
            flash("VPN is connected ✅", "success")
        else:
            flash("VPN not connected ❌", "error")
    except Exception as e:
        flash(f"Status check failed: {e}", "error")

    return redirect(url_for("client.client_page"))

from utils.generate_ovpn import generate_ovpn

@client_bp.route('/generate-ovpn', methods=['GET'])
def client_generate_ovpn():
    common_name = request.args.get("common_name")
    if not common_name:
        flash("Common name is required", "error")
        return redirect(url_for("client.client_page"))
    try:
        ovpn_path = generate_ovpn(common_name)
        flash(f"OVPN file successfully generated and saved at: {ovpn_path}", "success")
        return redirect(url_for("client.client_page"))
    except Exception as e:
        flash(f"Could not generate config: {str(e)}", "error")
        return redirect(url_for("client.client_page"))


# @client_bp.route('/disconnect', methods=['POST'])
# def disconnect_vpn():
#     try:
#         # Attempt to kill any running OpenVPN processes
#         subprocess.run("sudo pkill openvpn", shell=True, check=True)
#         flash("VPN connection terminated.", "success")
#     except subprocess.CalledProcessError as e:
#         flash(f"Failed to disconnect: {e}", "error")
#     return redirect(url_for('client.client_page'))

@client_bp.route('/disconnect', methods=['POST'])
def disconnect_vpn():
    pid_file = "/tmp/client_vpn.pid"
    try:
        if os.path.exists(pid_file):
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            subprocess.run(["sudo", "kill", str(pid)], check=True)
            os.remove(pid_file)
            flash("Disconnected from VPN.", "success")
        else:
            flash("No active VPN session found.", "info")
    except Exception as e:
        flash(f"Failed to disconnect: {e}", "error")

    return redirect(url_for("client.client_page"))

