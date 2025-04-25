import subprocess
import os

# def generate_client_cert(common_name):
#     try:
#         command = f"cd /home/prakash/Documents/Secure_VPN_client/openvpn-ca && ./easyrsa build-client-full {common_name} nopass"
#         result = subprocess.run(command, shell=True, capture_output=True, text=True)
#         return result.stdout, result.stderr
#     except Exception as e:
#         return "", str(e)

# def generate_csr(common_name):
#     try:
#         commands = f"""
#             cd /home/prakash/Documents/Secure_VPN_client/openvpn-ca && ./easyrsa gen-req {common_name} nopass
#         """
#         result = subprocess.run(commands, shell=True, capture_output=True, text=True)
#         return result.stdout, result.stderr
#     except Exception as e:
#         return "", str(e)
def generate_csr(common_name):
    try:
        command = [
            "./easyrsa", "gen-req", common_name, "nopass"
        ]
        env = os.environ.copy()
        env["EASYRSA_REQ_CN"] = common_name  # Pass CN as env var

        result = subprocess.run(
            command,
            cwd="/home/prakash/Documents/Secure_VPN_client/openvpn-ca",
            capture_output=True,
            text=True,
            env=env
        )
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)
