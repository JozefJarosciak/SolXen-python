import requests
import os
import subprocess
import sys

def download_file(url, filename):
    """ Download file from a URL and save it locally """
    r = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(r.content)

def setup_solana_client(eth_address):
    """ Setup Solana client environment and execute commands """
    project_dir = 'solana_rust_client'

    # Navigate to the project directory or create it if it doesn't exist
    if os.path.exists(project_dir):
        # Optional: Clear the existing directory to avoid conflicts
        subprocess.run(["rm", "-rf", project_dir], check=True)
    os.makedirs(project_dir)
    os.chdir(project_dir)

    # Initialize a new binary crate directly
    subprocess.run(["cargo", "init", "--bin"], check=True)

    # Download necessary files
    download_file("https://gist.githubusercontent.com/jacklevin74/a073004c120f45e32d84d8530d613218/raw/fde1c0fe4f77a85324c324366d2b8a85a47eb14d/client.js", "src/main.rs")  # Assuming main.rs content is provided by client.js
    download_file("https://gist.githubusercontent.com/jacklevin74/a669ab619946ed0fde522376cb9948cd/raw/d127e709cb4142530b4ce9aea4d52f4c455fca91/Cargo.toml", "Cargo.toml")

    # Build the project
    subprocess.run(["cargo", "build"], check=True)

    # Configure Solana CLI
    subprocess.run(["solana", "config", "set", "--url", "https://api.devnet.solana.com"], check=True)
    subprocess.run(["solana", "airdrop", "1"], check=True)

    # Execute the program
    while True:
        subprocess.run(["./target/debug/solana_rust_client", "--fee", "5000", "--address", eth_address], check=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 script.py <Ethereum Address>")
        sys.exit(1)
    eth_address = sys.argv[1]
    setup_solana_client(eth_address)
