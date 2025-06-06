#!/usr/bin/env python3
import hashlib
import os
import zipfile
import tarfile
import time
import subprocess
import sys
import argparse
import re
import glob
import shutil
import platform
import json
import base64
import binascii
import decimal
import threading
import asyncio
from typing import Dict, List, Set, Optional

# Cross-platform imports with fallbacks
try:
    import zmq
except ImportError:
    zmq = None

try:
    import websockets
except ImportError:
    websockets = None

try:
    from bitcoinrpc.authproxy import AuthServiceProxy
except ImportError:
    AuthServiceProxy = None

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

# Function to install pip if it is missing
def install_pip():
    try:
        print("Pip not found. Attempting to install...")
        if platform.system() == 'Windows':
            subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
        else:
            get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
            get_pip_script = os.path.join(os.path.expanduser("~"), "get-pip.py")
            if platform.system() == 'Linux':
                subprocess.check_call(["wget", get_pip_url, "-O", get_pip_script], shell=False)
            else:  # macOS
                subprocess.check_call(["curl", get_pip_url, "-o", get_pip_script], shell=False)
            subprocess.check_call([sys.executable, get_pip_script], shell=False)
        print("Pip installation successful!")
    except Exception as e:
        print(f"Error installing pip: {e}")
        sys.exit(1)

# Automatically install required packages if missing
def ensure_packages():
    required_packages = {
        'tqdm': 'tqdm',
        'zmq': 'pyzmq',
        'websockets': 'websockets',
        'bitcoinrpc': 'python-bitcoinrpc'
    }
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            try:
                print(f"Installing '{package_name}'...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name], shell=False)
            except Exception as e:
                print(f"❌ Failed to install {package_name}: {e}")
                if import_name in ['zmq', 'websockets']:
                    print(f"Note: {package_name} may require system dependencies on some platforms")
                sys.exit(1)

ensure_packages()

from tqdm import tqdm

# ANSI escape codes for colors (with Windows compatibility)
if platform.system() == 'Windows':
    try:
        import colorama
        colorama.init()
        COLOR_RESET = colorama.Style.RESET_ALL
        COLOR_PINK = colorama.Fore.LIGHTMAGENTA_EX
        COLOR_GREEN = colorama.Fore.LIGHTGREEN_EX
        COLOR_RED = colorama.Fore.LIGHTRED_EX
        COLOR_CYAN = colorama.Fore.LIGHTCYAN_EX
        COLOR_YELLOW = colorama.Fore.LIGHTYELLOW_EX
        COLOR_PASTEL_YELLOW = colorama.Fore.YELLOW
        COLOR_ORANGE = colorama.Fore.LIGHTRED_EX
        COLOR_ORAN_ = colorama.Fore.YELLOW
        SEPARATOR_COLOR = colorama.Fore.YELLOW
        SEPARATOR = f"{SEPARATOR_COLOR}{'-' * 70}{COLOR_RESET}"
    except ImportError:
        # Fallback for Windows without colorama
        COLOR_RESET = ""
        COLOR_PINK = ""
        COLOR_GREEN = ""
        COLOR_RED = ""
        COLOR_CYAN = ""
        COLOR_YELLOW = ""
        COLOR_PASTEL_YELLOW = ""
        COLOR_ORANGE = ""
        COLOR_ORAN_ = ""
        SEPARATOR_COLOR = ""
        SEPARATOR = '-' * 70
else:
    # Unix-like systems
    COLOR_RESET = "\033[0m"
    COLOR_PINK = "\033[38;5;211m"
    COLOR_GREEN = "\033[38;5;119m"
    COLOR_RED = "\033[38;5;197m"
    COLOR_CYAN = "\033[38;5;51m"
    COLOR_YELLOW = "\033[38;5;226m"
    COLOR_PASTEL_YELLOW = "\033[38;5;229m"
    COLOR_ORANGE = "\033[38;5;214m"
    COLOR_ORAN_ = "\033[38;5;229m"
    SEPARATOR_COLOR = "\033[38;5;229m"
    SEPARATOR = f"{SEPARATOR_COLOR}{'-' * 70}{COLOR_RESET}"

# ASCII Art
ascii_art = rf"""{COLOR_ORAN_}
                                   
            ]          ]           
          ]]]]       ]]]]          
         ]]]]]]]]]]]]]]]]]          
        ]]]]]]]]]]]]]]]]           
        ]]]]]]]]]]]]]]]]]]]    
       ]]]]]]]]]]]]]]]]]]]]] 
       ]]]]]]]]]]]]]]]]]]]]]]
       ]]]]]]]             ]]]     
       ]]]]    ]]]]]]]]]]]         
       []   ]]]]]]]]]]]]]]]]    
          ]]]]]]]]]]]]]]]]]]]]]    
         ]]]]]]]]]]]]]]]]]]]]]]]   
        ]]]]]]]]]]      ]]]]]]]]]              ______     ______     ______               ______     ______     ______     ______     __   __    
        ]]]]]]]]    ]]]]]]]]]]]]]             /\  ___\   /\  __ \   /\__  _\             /\  __ \   /\  ___\   /\  ___\   /\  __ \   /\ "-.\ \   
        ]]]]]]]    ]]]]]]]]]]]]]]]            \ \ \____  \ \  __ \  \/_/\ \/             \ \ \/\ \  \ \ \____  \ \  __\   \ \  __ \  \ \ \-.  \  
        ]]]]]]]]   ]]]   ]]]]]]]]]             \ \_____\  \ \_\ \_\    \ \_\              \ \_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_\  \_\ 
   ]]   ]]]]]]]]]       ]]]]]]]]]]              \/_____/   \/_/\/_/     \/_/     ______    \/_____/   \/_____/   \/_____/   \/_/\/_/   \/_/ \/_/ 
 ]]]]]] ]]]]]]]]]   ]]]]]]]]]]]]]                                              /\______\                
 ]]]]]]]] ]]]]]]]]  ]]]]]]]]]]]]                                               \/______/ 
  ]]]]]]]]] ]]]]]]]]]]]]]]]]]]]    
    ]]]]]]]]]] ]]]]]]]]]]]]]]      
       ]]]]]]]]]]]]]]]]]]]]        
           ]]]]]]]]]]]]            
     

   **********************************************
   *                                            *
   *  Welcome to Your Cat_Ocean V0.9            *
   *                                            *
   *  Author: @vm.vest vmvest.dev@gmail.com     *
   *                                            *
   **********************************************

 {COLOR_RESET}"""

# Cross-platform path handling
def get_home_dir() -> str:
    """Get the appropriate home directory cross-platform"""
    if platform.system() == 'Windows':
        return os.path.expanduser("~")
    else:
        return os.path.expanduser("~" if os.geteuid() != 0 else f"/home/{os.getenv('SUDO_USER')}")

HOME = get_home_dir()
BASE_DIR = os.path.join(HOME, "cat-release-builder")
BINARIES_ROOT = os.path.join(BASE_DIR, "catcoin-binaries")
READY_TO_USE_DIR = os.path.join(BASE_DIR, "Ready-To-Use")

# BitListen Configuration
ZMQ_TX_ADDRESS = "tcp://127.0.0.1:28332"
WEBSOCKET_PORT = 8765
RPC_USER = "yourrpcuser"
RPC_PASSWORD = "yourrpcpass"
RPC_PORT = 39393  # Default Catcoin RPC port

# BitListen Global Variables
bitlisten_main_loop = None
bitlisten_clients = set()

# BitListen Helper Functions
def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

async def bitlisten_websocket_handler(websocket):
    print(f"{COLOR_GREEN}[+] WebSocket client connected: {websocket.remote_address}{COLOR_RESET}")
    bitlisten_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        print(f"{COLOR_RED}[-] WebSocket client disconnected: {websocket.remote_address}{COLOR_RESET}")
        bitlisten_clients.remove(websocket)

def bitlisten_to_zmq():
    global RPC_USER, RPC_PASSWORD, RPC_PORT
    rpc_connection = AuthServiceProxy(f"http://{RPC_USER}:{RPC_PASSWORD}@127.0.0.1:{RPC_PORT}")
    
    print(f"{COLOR_CYAN}[*] Connecting to ZMQ...{COLOR_RESET}")
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(ZMQ_TX_ADDRESS)
    socket.setsockopt_string(zmq.SUBSCRIBE, 'rawtx')

    print(f"{COLOR_CYAN}[*] Listening for Catcoin transactions on ZMQ...{COLOR_RESET}")

    while True:
        parts = socket.recv_multipart()
        topic = parts[0].decode()
        raw_tx = parts[1]

        if topic != "rawtx":
            continue

        raw_tx_hex = binascii.hexlify(raw_tx).decode('utf-8')
        print(f"{COLOR_PINK}[>] Received raw TX: {raw_tx_hex}{COLOR_RESET}")

        # Retry loop for RPC decoding
        while True:
            try:
                decoded_tx = rpc_connection.decoderawtransaction(raw_tx_hex)
                print(f"{COLOR_RESET}[>] Decoded TX: {json.dumps(decoded_tx, indent=2, default=decimal_default)}{COLOR_RESET}")
                break  # Success, exit retry loop
            except Exception as e:
                print(f"{COLOR_RED}[!] RPC decode error: {e}{COLOR_RESET}")
                print(f"{COLOR_YELLOW}[*] Attempting to reconnect RPC client in 5 seconds...{COLOR_RESET}")
                time.sleep(5)
                try:
                    rpc_connection = AuthServiceProxy(f"http://{RPC_USER}:{RPC_PASSWORD}@127.0.0.1:{RPC_PORT}")
                    print(f"{COLOR_GREEN}[*] Reconnected to RPC server successfully{COLOR_RESET}")
                except Exception as rpc_e:
                    print(f"{COLOR_RED}[!] Failed to reconnect RPC client: {rpc_e}{COLOR_RESET}")

        total_amount = sum(float(vout.get("value", 0)) for vout in decoded_tx["vout"])
        print(f"{COLOR_GREEN}[>] Total amount in TX: {total_amount} CAT{COLOR_RESET}")

        if bitlisten_clients:
            message = json.dumps({"amount": total_amount})
            print(f"{COLOR_CYAN}[>] Sending message to {len(bitlisten_clients)} clients: {message}{COLOR_RESET}")
            for client in bitlisten_clients.copy():
                try:
                    asyncio.run_coroutine_threadsafe(client.send(message), bitlisten_main_loop)
                except Exception as e:
                    print(f"{COLOR_RED}[!] Error sending message to client: {e}{COLOR_RESET}")
                    bitlisten_clients.remove(client)
        else:
            print(f"{COLOR_YELLOW}[!] No WebSocket clients connected. Skipping send.{COLOR_RESET}")

async def bitlisten_main():
    global bitlisten_main_loop
    print(f"{COLOR_CYAN}[*] Starting WebSocket server...{COLOR_RESET}")
    bitlisten_main_loop = asyncio.get_running_loop()

    start_server = websockets.serve(bitlisten_websocket_handler, "0.0.0.0", WEBSOCKET_PORT)
    await start_server

    # Run ZMQ listener in background thread
    zmq_thread = threading.Thread(target=bitlisten_to_zmq, daemon=True)
    zmq_thread.start()

    print(f"{COLOR_GREEN}[*] BitListen is running. Waiting for transactions...{COLOR_RESET}")
    await asyncio.Future()  # run forever

# Ensure directories exist
def ensure_directories():
    """Create required directories if they don't exist"""
    for directory in [BASE_DIR, BINARIES_ROOT, READY_TO_USE_DIR]:
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            print(f"{COLOR_RED}Failed to create directory {directory}: {e}{COLOR_RESET}")
            sys.exit(1)

ensure_directories()

# Discover versions
def discover_versions(binaries_root):
    version_pattern = re.compile(r"^\d+\.\d+\.\d+$")
    try:
        subdirs = os.listdir(binaries_root)
        versions = [d for d in subdirs if version_pattern.match(d) and os.path.isdir(os.path.join(binaries_root, d))]
        return sorted(versions, key=lambda s: list(map(int, s.split('.'))), reverse=True)
    except Exception as e:
        print(f"{COLOR_RED}Error discovering versions:{COLOR_RESET} {e}")
        return []

def select_version(versions):
    if not versions:
        print(f"{COLOR_RED}❌ No valid version directories found!{COLOR_RESET}")
        sys.exit(1)
    elif len(versions) == 1:
        print(f"{COLOR_GREEN}✔ Using version:{COLOR_RESET} {versions[0]}")
        return versions[0]
    else:
        print(f"{COLOR_YELLOW}Multiple versions found:{COLOR_RESET}")
        for i, v in enumerate(versions):
            print(f"  [{i+1}] {v}")
        default = versions[0]
        choice = input(f"\nSelect a version [1-{len(versions)}] or press Enter for default ({default}): ").strip()
        if choice == "":
            return default
        try:
            index = int(choice) - 1
            if 0 <= index < len(versions):
                return versions[index]
            else:
                raise ValueError
        except ValueError:
            print(f"{COLOR_RED}Invalid selection. Exiting...{COLOR_RESET}")
            sys.exit(1)

# SHA256 Calculation
def sha256_hash(file_path):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        return f"{COLOR_RED}Error: {e}{COLOR_RESET}"

# Extract Archive (cross-platform)
def extract_archive(label, archive_path, output_dir, delay=0.05):
    if not os.path.exists(archive_path):
        return f"{COLOR_RED}⚠️ Archive not found:{COLOR_RESET} {archive_path}"
    os.makedirs(output_dir, exist_ok=True)
    try:
        if archive_path.endswith(".zip"):
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                files = zip_ref.namelist()
                with tqdm(total=len(files), desc=f"Extracting {label}", unit="file", ncols=100, leave=False) as pbar:
                    for file in files:
                        if "/bin/" in file or file.startswith("bin/"):
                            if not file.endswith("/"):
                                output_path = os.path.join(output_dir, os.path.basename(file))
                                with open(output_path, "wb") as f:
                                    f.write(zip_ref.read(file))
                                # Set executable permission on Unix-like systems
                                if platform.system() != 'Windows':
                                    os.chmod(output_path, 0o755)
                        pbar.update(1)
                        time.sleep(delay)
        elif archive_path.endswith(".tar.gz") or archive_path.endswith(".tgz"):
            with tarfile.open(archive_path, "r:gz") as tar_ref:
                members = tar_ref.getmembers()
                with tqdm(total=len(members), desc=f"Extracting {label}", unit="file", ncols=100, leave=False) as pbar:
                    for member in members:
                        if ("/bin/" in member.name or member.name.startswith("bin/")) and member.isfile():
                            member.name = os.path.basename(member.name)
                            output_path = os.path.join(output_dir, member.name)
                            tar_ref.extract(member, output_dir)
                            # Set executable permission on Unix-like systems
                            if platform.system() != 'Windows':
                                os.chmod(output_path, 0o755)
                        pbar.update(1)
                        time.sleep(delay)
        return ""
    except Exception as e:
        return f"{COLOR_RED}❌ Failed to extract {label}!:{COLOR_RESET} {e}"

# Signing Instructions
def show_signing_instructions():
    print(f"\n{COLOR_YELLOW}🔏 Signing Instructions:{COLOR_RESET}")
    print("\n1. Prepare your GPG environment if not already set up:")
    if platform.system() == 'Windows':
        print(f"   {COLOR_PINK}gpg --full-generate-key{COLOR_RESET} (using Gpg4win)")
    else:
        print(f"   {COLOR_PINK}gpg --full-generate-key{COLOR_RESET}")
    
    print("\n2. Export your public key and share it if needed:")
    print(f"   {COLOR_PINK}gpg --armor --export YOUR_EMAIL@EXAMPLE.COM{COLOR_RESET}")
    
    print("\n3. Sign any binary or hash file using:")
    print(f"   {COLOR_PINK}gpg --detach-sign --armor <file>{COLOR_RESET}")
    
    print("\n4. To verify a signature:")
    print(f"   {COLOR_PINK}gpg --verify <file>.asc <file>{COLOR_RESET}")
    
    print(f"\n{COLOR_ORANGE}📌 Note: This script does not perform signing automatically.")
    print("Please use GPG manually following the steps above.{COLOR_RESET}\n")

# Main Entry
def main():
    parser = argparse.ArgumentParser(description="Cat_Ocean V0.9 - Verify, Extract, Sign Catcoin Binaries, or Run BitListen")
    parser.add_argument("--verify", action="store_true", help="Verify SHA256 hashes of binary archives")
    parser.add_argument("--extract", action="store_true", help="Copy Linux binaries (extract), or copy Mac/Windows archives to folders")
    parser.add_argument("--sign", action="store_true", help="Show instructions for signing with GPG")
    parser.add_argument("--bitlisten", action="store_true", help="Run BitListen service for real-time transaction monitoring")
    args = parser.parse_args()

    if not any([args.verify, args.extract, args.sign, args.bitlisten]):
        parser.print_help()
        return

    print(ascii_art)

    if args.bitlisten:
        if zmq is None or websockets is None or AuthServiceProxy is None:
            print(f"{COLOR_RED}Error: Required packages for BitListen not available{COLOR_RESET}")
            sys.exit(1)
        print(f"{COLOR_GREEN}🚀 Starting BitListen service...{COLOR_RESET}")
        try:
            asyncio.run(bitlisten_main())
        except KeyboardInterrupt:
            print(f"\n{COLOR_RED}🛑 BitListen service stopped by user{COLOR_RESET}")
        return

    versions = discover_versions(BINARIES_ROOT)
    selected_version = select_version(versions)
    BINARIES_DIR = os.path.join(BINARIES_ROOT, selected_version)

    PATTERNS = {
        "Source file": "catcoin-*.tar.gz",
        "Linux Build": "catcoin-*-x86_64-linux-gnu.tar.gz",
        "Windows Build": "catcoin-*-win64-setup-unsigned.exe",
        "Mac Build": "catcoin-*-osx-unsigned.dmg"
    }

    PLATFORM_MAP = {
        "Linux Build": "Linux",
        "Windows Build": "Windows",
        "Mac Build": "Mac"
    }

    TARGETS = []
    LABELS = []

    for label, pattern in PATTERNS.items():
        matches = glob.glob(os.path.join(BINARIES_DIR, pattern))

        if label == "Source file":
            matches = [
                m for m in matches
                if not re.search(r'-(x86_64|aarch64|arm64|riscv64|win64|osx|debug)', os.path.basename(m))
            ]

        if matches:
            TARGETS.append(matches[0])
            LABELS.append(label)
        else:
            print(f"{COLOR_RED}⚠️ No file matched for pattern:{COLOR_RESET} {pattern}")

    if args.verify and args.extract:
        print(f"{COLOR_ORANGE}📦 Starting SHA256 hash scan & extraction/copy process...{COLOR_RESET}\n")
    elif args.verify:
        print(f"{COLOR_ORANGE}📦 Starting SHA256 hash scan...{COLOR_RESET}\n")
    elif args.extract:
        print(f"{COLOR_ORANGE}📦 Starting extraction/copy process...{COLOR_RESET}\n")

    if args.verify or args.extract:
        for index, path in enumerate(TARGETS):
            label = LABELS[index] if index < len(LABELS) else "File"
            if os.path.isfile(path):
                print(f"{COLOR_CYAN}{label}:{COLOR_RESET} {os.path.basename(path)}")
                if args.verify:
                    print(f"{COLOR_PINK}SHA256:{COLOR_RESET} {sha256_hash(path)}")
                if args.extract and label in PLATFORM_MAP:
                    platform = PLATFORM_MAP[label]
                    target_dir = os.path.join(READY_TO_USE_DIR, platform)
                    os.makedirs(target_dir, exist_ok=True)

                    if platform == "Linux":
                        result = extract_archive(platform, path, target_dir)
                        if result:
                            print(result)
                    else:
                        try:
                            dest_path = os.path.join(target_dir, os.path.basename(path))
                            shutil.copy2(path, dest_path)
                        except Exception as e:
                            print(f"{COLOR_RED}❌ Failed to copy {label}:{COLOR_RESET} {e}")
                print(SEPARATOR)
            else:
                print(f"{COLOR_RED}⚠️ Path not found or inaccessible:{COLOR_RESET} {path}")
                print(SEPARATOR)

    if args.sign:
        show_signing_instructions()

    print(f"\n{COLOR_GREEN}🎉 Task(s) completed!{COLOR_RESET}")
    if args.extract:
        print(f"{COLOR_PASTEL_YELLOW}📁 All binaries placed in:{COLOR_RESET} {READY_TO_USE_DIR}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{COLOR_RED}🛑 Operation cancelled by user{COLOR_RESET}")
        sys.exit(1)