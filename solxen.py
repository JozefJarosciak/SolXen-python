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
    keypair_path = '/home/tokai/.config/solana/id.json'
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

def download_and_prepare_rust_source():
    """Download the Rust client file and modify it to use the correct keypair path."""
    url = "https://gist.githubusercontent.com/jacklevin74/a073004c120f45e32d84d8530d613218/raw/fde1c0fe4f77a85324c324366d2b8a85a47eb14d/client.js"
    keypair_path = os.path.expanduser('~/.config/solana/id.json')  # Generic way to get home directory
    response = requests.get(url)
    rust_code = response.text
    modified_rust_code = rust_code.replace('/home/ubuntu/.config/solana/id.json', keypair_path)
    with open('src/main.rs', 'w') as f:  # Ensure this is the correct path within your Rust project
        f.write(modified_rust_code)

def update_cargo_toml():
    """Download and replace the Cargo.toml file from a given URL."""
    cargo_url = "https://gist.githubusercontent.com/jacklevin74/a669ab619946ed0fde522376cb9948cd/raw/d127e709cb4142530b4ce9aea4d52f4c455fca91/Cargo.toml"
    response = requests.get(cargo_url)
    if response.status_code == 200:
        with open('Cargo.toml', 'w') as file:
            file.write(response.text)
    else:
        print("Failed to download the Cargo.toml file")
        sys.exit(1)

def setup_solana_client(eth_address, keypair_path):
    project_dir = 'solana_rust_client'
    if os.path.exists(project_dir):
        subprocess.run(["rm", "-rf", project_dir], check=True)
    os.makedirs(project_dir)
    os.chdir(project_dir)  # Change into the project directory

    subprocess.run(["cargo", "init", "--bin"], check=True)
    update_cargo_toml()  # Ensure this runs in the project directory
    download_and_prepare_rust_source()  # This is called after initializing the Rust project
    subprocess.run(["cargo", "build"], check=True)  # Build the project

    # Configure Solana CLI
    subprocess.run(["solana", "config", "set", "--url", "https://api.devnet.solana.com"], check=True)
    subprocess.run(["solana", "config", "set", "--keypair", keypair_path], check=True)

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
