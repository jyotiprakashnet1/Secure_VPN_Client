import subprocess

def get_revoked_clients():
    crl_path = "/etc/openvpn/server/crl.pem"
    result = subprocess.run(["openssl", "crl", "-in", crl_path, "-text", "-noout"], capture_output=True, text=True)
    output = result.stdout

    revoked_serials = []
    lines = output.splitlines()
    for line in lines:
        if "Serial Number:" in line:
            serial = line.split("Serial Number:")[1].strip()
            revoked_serials.append(serial)

    # Optional: map serial to CN using issued certs (via Easy-RSA index.txt)
    index_path = "/home/prakash/Documents/Secure_VPN_client/openv-ca/pki/index.txt"
    revoked_cns = []
    with open(index_path) as f:
        for line in f:
            if any(serial in line for serial in revoked_serials):
                parts = line.strip().split("\t")
                for part in parts:
                    if part.startswith("/CN="):
                        revoked_cns.append(part.split("=")[1])

    return revoked_cns
