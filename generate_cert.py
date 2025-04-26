#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import subprocess
from datetime import datetime, timedelta

# Define certificate paths
cert_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
cert_path = os.path.join(cert_dir, "cert.pem")
key_path = os.path.join(cert_dir, "key.pem")

def generate_self_signed_cert(common_name="smartpi.local"):
    """Generate a self-signed certificate for local HTTPS."""
    print(f"Generating self-signed certificate for {common_name}...")
    
    # Create the certificate directory if it doesn't exist
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
        print(f"Created certificate directory: {cert_dir}")
    
    # Generate validity dates (valid for 1 year)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=365)
    
    # OpenSSL command to generate self-signed certificate
    openssl_cmd = [
        "openssl", "req", "-x509", 
        "-newkey", "rsa:2048", 
        "-keyout", key_path,
        "-out", cert_path,
        "-days", "365",
        "-nodes",  # No passphrase
        "-subj", f"/CN={common_name}",
        "-addext", f"subjectAltName=DNS:{common_name},DNS:localhost,IP:127.0.0.1"
    ]
    
    try:
        subprocess.run(openssl_cmd, check=True)
        print(f"Certificate generated successfully!")
        print(f"Certificate path: {cert_path}")
        print(f"Private key path: {key_path}")
        print("\nIMPORTANT: You will need to add this certificate to your trusted certificates")
        print("in your browser to avoid security warnings.")
        return cert_path, key_path
    except subprocess.CalledProcessError as e:
        print(f"Error generating certificate: {e}")
        return None, None

if __name__ == "__main__":
    generate_self_signed_cert()