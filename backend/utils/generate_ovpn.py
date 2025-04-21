import os

def generate_ovpn(common_name):
    base_dir = "/home/prakash/Documents/Secure_VPN_client/openvpn"
    client_dir = f"{base_dir}/client"
    server_dir = f"{base_dir}/server"
    
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
cipher AES-256-CBC
auth SHA256
verb 3

<ca>
{open(f"{server_dir}/ca.crt").read()}
</ca>

<cert>
{open(f"{client_dir}/{common_name}.crt").read()}
</cert>

<key>
{open(f"{client_dir}/{common_name}.key").read()}
</key>

<tls-auth>
{open(f"{server_dir}/ta.key").read()}
</tls-auth>
key-direction 1
"""
    output_path = f"{client_dir}/{common_name}.ovpn"
    with open(output_path, "w") as f:
        f.write(ovpn_content.strip())
    return output_path
