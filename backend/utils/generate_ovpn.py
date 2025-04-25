import os

def generate_ovpn(common_name):
    base_dir = "/home/prakash/Documents/Secure_VPN_client/openvpn"
    ca_dir = "/home/prakash/Documents/Secure_VPN_client/openvpn-ca/client"
    client_dir = os.path.join(base_dir, "client")
    server_dir = os.path.join(base_dir, "server")

    # Paths to required files
    ca_cert_path = os.path.join(client_dir, "ca.crt")
    ta_key_path = os.path.join(server_dir, "ta.key")
    client_cert_path = os.path.join("/home/prakash/Documents/Secure_VPN_client/openvpn-ca/pki/issued", f"{common_name}.crt")
    client_key_path = os.path.join("/home/prakash/Documents/Secure_VPN_client/openvpn-ca/pki/private", f"{common_name}.key")

    # Read content from certificate and key files
    with open(ca_cert_path, "r") as f:
        ca_cert = f.read().strip()

    with open(client_cert_path, "r") as f:
        client_cert = f.read().strip()

    with open(client_key_path, "r") as f:
        client_key = f.read().strip()

    with open(ta_key_path, "r") as f:
        ta_key = f.read().strip()

    # Compose .ovpn content
    ovpn_content = f"""
client
dev tun
proto udp
remote 127.0.0.1 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-GCM
auth SHA256
verb 3
key-direction 1

<ca>
{ca_cert}
</ca>

<cert>
{client_cert}
</cert>

<key>
{client_key}
</key>

<tls-auth>
{ta_key}
</tls-auth>
"""

    # Write to .ovpn file in client folder
    output_path = os.path.join(client_dir, f"{common_name}.ovpn")
    with open(output_path, "w") as f:
        f.write(ovpn_content.strip())

    return output_path
