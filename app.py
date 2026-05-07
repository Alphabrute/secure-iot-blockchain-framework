from flask import Flask, render_template_string, request
from gpiozero import OutputDevice
import adafruit_dht
import board
import joblib
import hashlib
import json
from web3 import Web3

app = Flask(__name__)

# =========================
# HARDWARE SETUP
# =========================

# Relay connected to GPIO17
# active_high=False means relay turns ON when GPIO output is LOW
relay = OutputDevice(17, active_high=False, initial_value=False)

# DHT11 data pin connected to GPIO4
dht = adafruit_dht.DHT11(board.D4)

relay_state = 0  # 0 = OFF, 1 = ON


# =========================
# MACHINE LEARNING SETUP
# =========================

model = joblib.load("isolation_model.pkl")


# =========================
# BLOCKCHAIN SETUP
# =========================

# Since Ganache is running on your PC, use PC IP address here
# Your PC IP from screenshot: 192.168.29.25
GANACHE_URL = "http://192.168.29.25:7545"

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

# Paste your deployed contract address here
contract_address = "0x9a500865514401818924A9E28C625C1578f9297C"
contract_address = Web3.to_checksum_address(contract_address)

# Load ABI from abi.txt
with open("abi.txt", "r") as f:
    contract_abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Use first Ganache account
account = w3.eth.accounts[0] if w3.is_connected() else None


# =========================
# FUNCTIONS
# =========================

def read_sensor():
    try:
        temp = dht.temperature
        hum = dht.humidity

        if temp is None or hum is None:
            return 0.0, 0.0

        return float(temp), float(hum)

    except Exception:
        return 0.0, 0.0


def ml_check(temp, hum):
    """
    Isolation Forest output:
    1  = normal
    -1 = anomaly
    """
    prediction = model.predict([[temp, hum]])[0]

    if prediction == 1:
        return "NORMAL"
    else:
        return "ANOMALY"


def generate_hash(payload):
    text = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(text.encode()).hexdigest()


def store_blockchain(data_hash, ml_status):
    """
    Your Solidity contract function:
    storeRecord(string deviceId, string dataHash, string status)
    """

    if not w3.is_connected():
        return "Blockchain error: Ganache not connected"

    tx_hash = contract.functions.storeRecord(
        "pi-node-1",
        data_hash,
        ml_status
    ).transact({"from": account})

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return receipt.transactionHash.hex()


# =========================
# HTML UI
# =========================

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Secure IoT Blockchain Dashboard</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111827;
            color: white;
            text-align: center;
            padding: 30px;
        }

        h1 {
            color: #60a5fa;
        }

        .card {
            background: #1f2937;
            padding: 20px;
            margin: 15px auto;
            width: 85%;
            border-radius: 15px;
            box-shadow: 0 0 15px rgba(0,0,0,0.3);
        }

        button {
            padding: 15px 30px;
            margin: 10px;
            font-size: 18px;
            border-radius: 10px;
            border: 0;
            cursor: pointer;
        }

        .on {
            background: #22c55e;
            color: black;
        }

        .off {
            background: #ef4444;
            color: white;
        }

        .log {
            background: #3b82f6;
            color: white;
        }

        .hash {
            word-break: break-all;
            font-size: 14px;
            color: #93c5fd;
        }

        .normal {
            color: #22c55e;
            font-weight: bold;
        }

        .anomaly {
            color: #ef4444;
            font-weight: bold;
        }

        .small {
            font-size: 14px;
            color: #d1d5db;
        }
    </style>
</head>

<body>

    <h1>Secure IoT Framework</h1>
    <h3>Raspberry Pi + DHT11 + Relay + Isolation Forest + Ethereum Ganache</h3>

    <div class="card">
        <h2>Temperature: {{ temp }} °C</h2>
        <h2>Humidity: {{ hum }} %</h2>
        <h2>Relay/Bulb: {{ relay_text }}</h2>

        <h2>
            ML Status:
            <span class="{{ 'normal' if ml_status == 'NORMAL' else 'anomaly' }}">
                {{ ml_status }}
            </span>
        </h2>

        <p class="small">Blockchain Connected: {{ blockchain_status }}</p>
        <p class="small">Ganache URL: {{ ganache_url }}</p>
    </div>

    <div class="card">
        <form method="POST" action="/relay">
            <button class="on" name="state" value="ON">Turn Bulb ON</button>
            <button class="off" name="state" value="OFF">Turn Bulb OFF</button>
        </form>

    </div>

    <div class="card">
        <h3>Generated Data Hash</h3>
        <p class="hash">{{ data_hash }}</p>

        <h3>Blockchain Transaction</h3>
        <p class="hash">{{ tx_id }}</p>
    </div>

</body>
</html>
"""


def dashboard(tx_id="Not stored yet"):
    temp, hum = read_sensor()

    relay_text = "ON" if relay_state == 1 else "OFF"

    payload = {
        "deviceId": "pi-node-1",
        "temperature": temp,
        "humidity": hum,
        "relay": relay_text
    }

    ml_status = ml_check(temp, hum)
    data_hash = generate_hash(payload)

    blockchain_status = "YES" if w3.is_connected() else "NO"

    return render_template_string(
        HTML,
        temp=temp,
        hum=hum,
        relay_text=relay_text,
        ml_status=ml_status,
        data_hash=data_hash,
        tx_id=tx_id,
        blockchain_status=blockchain_status,
        ganache_url=GANACHE_URL
    )


# =========================
# ROUTES
# =========================

@app.route("/")
def index():
    return dashboard()

@app.route("/relay", methods=["POST"])
def control_relay():
    global relay_state

    state = request.form["state"]

    if state == "ON":
        relay.on()
        relay_state = 1
    else:
        relay.off()
        relay_state = 0

    temp, hum = read_sensor()
    relay_text = "ON" if relay_state == 1 else "OFF"

    payload = {
        "deviceId": "pi-node-1",
        "temperature": temp,
        "humidity": hum,
        "relay": relay_text,
        "action": "relay_" + relay_text
    }

    ml_status = ml_check(temp, hum)
    data_hash = generate_hash(payload)

    if ml_status == "NORMAL":
        tx_id = store_blockchain(data_hash, ml_status)
    else:
        tx_id = "Relay changed, but blockchain storage blocked due to anomaly"

    return dashboard(tx_id)

# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
