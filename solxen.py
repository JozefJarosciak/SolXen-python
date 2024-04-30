import requests
import os
import subprocess
import sys

def download_file(url, filename):
    """Download file from a URL and save it locally"""
    r = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(r.content)

def create_or_verify_wallet():
    """Create a new Solana wallet or verify existing wallet's balance"""
    keypair_path = '/home/jozef/.config/solana/id.json'
    min_balance = 1.0  # Minimum balance in SOL required to skip creating a new wallet

    # Check if the keypair file exists and get balance
    if os.path.exists(keypair_path):
        result = subprocess.run(['solana', 'balance', keypair_path, '--url', 'https://api.devnet.solana.com'], capture_output=True, text=True)
        balance_output = result.stdout.strip()
        # Extract numeric balance from output like "1 SOL"
        balance = float(balance_output.split()[0])  # Split the string and convert the first part to float
        if balance >= min_balance:
            print(f"Existing wallet has sufficient balance: {balance} SOL")
            return keypair_path

    # If balance is insufficient or wallet does not exist, create a new wallet
    print("Creating new wallet or existing wallet has insufficient balance.")
    subprocess.run(['solana-keygen', 'new', '--outfile', keypair_path], check=True)
    subprocess.run(['solana', 'airdrop', '1', keypair_path, '--url', 'https://api.devnet.solana.com'], check=True)
    return keypair_path

def setup_solana_client(eth_address, keypair_path):
    """Setup Solana client environment and execute commands"""
    project_dir = 'solana_rust_client'

    # Clear existing and create new directory
    if os.path.exists(project_dir):
        subprocess.run(["rm", "-rf", project_dir], check=True)
    os.makedirs(project_dir)
    os.chdir(project_dir)

    # Initialize a new binary crate directly
    subprocess.run(["cargo", "init", "--bin"], check=True)

    # Download necessary files
    download_file("https://gist.githubusercontent.com/jacklevin74/a669ab619946ed0fde522376cb9948cd/raw/d127e709cb4142530b4ce9aea4d52f4c455fca91/Cargo.toml", "Cargo.toml")
    download_file("https://gist.githubusercontent.com/jacklevin74/a073004c120f45e32d84d8530d613218/raw/fde1c0fe4f77a85324c324366d2b8a85a47eb14d/client.js", "src/main.rs")

    # Build the project
    subprocess.run(["cargo", "build"], check=True)

    # Configure Solana CLI
    subprocess.run(["solana", "config", "set", "--url", "https://api.devnet.solana.com"], check=True)
    subprocess.run(["solana", "config", "set", "keypair", keypair_path], check=True)

    # Execute the program in a loop
    while True:
        subprocess.run(["./target/debug/solana_rust_client", "--fee", "5000", "--address", eth_address], check=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 script.py <Ethereum Address>")
        sys.exit(1)
    eth_address = sys.argv[1]
    keypair_path = create_or_verify_wallet()
    setup_solana_client(eth_address, keypair_path)
