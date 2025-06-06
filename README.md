# CatListen 
### CatListen is a real-time Catcoin transaction visualizer that displays transactions as animated bubbles, connecting to your local Catcoin node via ZMQ and WebSockets.

## 🔮 Features

-  **Animated bubbles** scale with transaction amounts.
-  **Themed light/dark** modes. 
-  **Paw-shaped cursors**.
-  **Sound effects** with volume control.
-  **USD/CAT toggle** with live CoinGecko price with price cahnges. 
-  **Minimum amount** filtering.
-  **Transaction log** download.
-  **Cross-platform support** (Windows, Linux, macOS)


## 📦 Requirements

**Frontend:**
- Modern web browser (Chrome, Firefox, Edge)
- WebSocket support

**Backend:**
- Python 3.7 or higher
- Catcoin node with ZMQ enabled
- Required packages: `pyzmq`, `websockets`, `python-bitcoinrpc`, `tqdm`
- Cat-Ocean.py toolkit (https://github.com/VmVest/Cat-Ocean)


## 🐲 Usage

### Clone this repository:
```bash
sudo git clone https://github.com/VmVest/CatListen.git
cd CatListen
```
Install dependencies with:
```bash
sudo pip install -r requirements.txt --break-system-packages
```

### Run Catcoin Node:
**Windows**
Head to the Catcoind folder then open terminal in that folder (Right-click in blank area in that folder and select Open Terminal).
```bash
./catcoind.exe -conf={paste-catcoin.conf-path}
```
**Linux**
```bash
cd Catcoind
sudo chmod +x ./catcoind
./catcoind -conf={paste-catcoin.conf-path}
```
**MacOS**
```bash
cd Catcoind
sudo chmod +x ./catcoind-osx
./catcoind-osx -conf={paste-catcoin.conf-path}
```
Example: ./catcoind.exe -conf="C:\Users\vmvest\Desktop\Catlisten\Catcoind\catcoin.conf"


### Run Cat-Ocean toolkit:
**Windows**
Back to the Catlisten folder then open terminal in that folder (Right-click in blank area in that folder and select Open Terminal).
```bash
python3 Cat-OceanV0.9.py --bitlisten
```
**Linux**
```bash
cd ..
sudo chmod +x ./Cat-OceanV0.9.py
sudo python3 Cat-OceanV0.9.py --bitlisten
```
**MacOS**
```bash
cd ..
sudo chmod +x ./Cat-OceanV0.9.py
sudo python3 Cat-OceanV0.9.py --bitlisten
```

### Open the index.html file.

### Done! Bubbles will popup now. Enjoy!
### Preview:
![Alt text](Images/Preview.png)


## 🧑‍💻 Author
@vm.vest
vmvest.dev@gmail.com

### 🍧 Donations appreciated!

**CAT:** 9TEAitMMnTCWeHAKrEMZ1wxiJkTQZcbqth

**USDT:** 0xc8a3889fBfA929A79122E20bF5f71eDFBFD3C154

**BTC:** bc1qk72w9az3cdsllvnz6u05wsnzv4fqax93yshrwt

**SOL:** qR9dxTzz6XS4NDJkj3Tvfm8555frTcWgi4qv7SXEirk

**TON:** UQCp5ohQ8iqAwbYAGew06XHct9D3HS52iU2Q2XcR-8SLSu24
