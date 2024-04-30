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
        try:
            balance = float(balance_output.split()[0])  # Extract the numeric balance
            if balance >= min_balance:
                print(f"Existing wallet has sufficient balance: {balance} SOL")
                return keypair_path
        except (IndexError, ValueError):
            print("Failed to parse balance. Proceeding with new wallet creation.")

    print("Creating new wallet or existing wallet has insufficient balance.")
    subprocess.run(['solana-keygen', 'new', '--outfile', keypair_path], check=True)
    subprocess.run(['solana', 'airdrop', '1', keypair_path, '--url', 'https://api.devnet.solana.com'], check=True)
    return keypair_path

def run_command(command):
    """Run a command through subprocess and print the output."""
    print("Running command:", ' '.join(command))
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error:", result.stderr)
        raise subprocess.CalledProcessError(result.returncode, command)
    print("Output:", result.stdout)
    return result.stdout

def setup_solana_client(eth_address, keypair_path):
    project_dir = 'solana_rust_client'
    if os.path.exists(project_dir):
        subprocess.run(["rm", "-rf", project_dir], check=True)
    os.makedirs(project_dir)
    os.chdir(project_dir)

    subprocess.run(["cargo", "init", "--bin"], check=True)
    # Assuming downloading and file setup is correct here
    run_command(["cargo", "build"])

    # Configure Solana CLI correctly
    run_command(["solana", "config", "set", "--url", "https://api.devnet.solana.com"])
    run_command(["solana", "config", "set", "--keypair", keypair_path])

    # Execute the program in a loop
    while True:
        run_command(["./target/debug/solana_rust_client", "--fee", "5000", "--address", eth_address])

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 script.py <Ethereum Address>")
        sys.exit(1)
    eth_address = sys.argv[1]
    keypair_path = create_or_verify_wallet()
    setup_solana_client(eth_address, keypair_path)
