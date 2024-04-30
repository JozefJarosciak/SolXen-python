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
    # Create a directory for the Solana client if it doesn't exist
    if not os.path.exists('solana_rust_client'):
        os.makedirs('solana_rust_client')

    os.chdir('solana_rust_client')

    # Download required files
    download_file("https://gist.githubusercontent.com/jacklevin74/a073004c120f45e32d84d8530d613218/raw/fde1c0fe4f77a85324c324366d2b8a85a47eb14d/client.js", "client.js")
    download_file("https://gist.githubusercontent.com/jacklevin74/a669ab619946ed0fde522376cb9948cd/raw/d127e709cb4142530b4ce9aea4d52f4c455fca91/Cargo.toml", "Cargo.toml")

    # Initialize cargo project
    subprocess.run(["cargo", "new", "solana_rust_client"], check=True)
    os.chdir('solana_rust_client')

    # Build the project
    subprocess.run(["cargo", "build"], check=True)

    # Configure Solana CLI
    subprocess.run(["solana", "config", "set", "--url", "https://api.devnet.solana.com"], check=True)
    subprocess.run(["solana", "airdrop", "1"], check=True)

    # Execute the program in a loop
    command = f"while true; do ./target/debug/solana_rust_client --fee 5000 --address {eth_address}; done"
    subprocess.run(command, shell=True, check=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 script.py <Ethereum Address>")
        sys.exit(1)
    eth_address = sys.argv[1]
    setup_solana_client(eth_address)
