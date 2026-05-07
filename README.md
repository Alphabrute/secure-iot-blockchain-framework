# Secure IoT Framework using Raspberry Pi, Blockchain and Isolation Forest

This project is a secure IoT framework that uses Raspberry Pi as an edge node to monitor sensor data, control a relay-connected bulb, detect anomalies using an Isolation Forest machine learning model, and store verified data/action hashes on an Ethereum blockchain using Ganache and Solidity smart contracts.

## Features

- Raspberry Pi based IoT edge node
- DHT11 temperature and humidity monitoring
- Relay module control through web UI
- Isolation Forest based anomaly detection
- Ethereum Ganache blockchain integration
- Solidity smart contract for tamper-proof logging
- Flask web dashboard
- Global access support using ngrok or Cloudflare Tunnel

## System Architecture

```text
DHT11 Sensor + Relay/Bulb
        ↓
Raspberry Pi Edge Node
        ↓
Flask Web Dashboard
        ↓
Isolation Forest ML Model
        ↓
Ethereum Ganache Blockchain
        ↓
Cloudflare Tunnel / ngrok for Global Access
```

## Project Flow
Raspberry Pi reads temperature and humidity from the DHT11 sensor.
The Flask dashboard displays sensor values and relay status.
Isolation Forest checks temperature and humidity for anomalies.
Relay ON/OFF actions are controlled through the web UI.
If the sensor data is normal, a SHA-256 hash is generated.
The hash, device ID, and ML status are stored on Ganache blockchain using a Solidity smart contract.
If anomaly is detected, the action/data is not treated as trusted.

## Technologies Used
Raspberry Pi OS
Python
Flask
GPIOZero
Adafruit DHT library
Scikit-learn
Isolation Forest
Solidity
Truffle
Ganache
Web3.py
HTML/CSS
ngrok / Cloudflare Tunnel
Hardware Used
Raspberry Pi
DHT11 temperature and humidity sensor
Relay module
LED bulb/load
Jumper wires
Smart Contract

## The smart contract stores:

Device ID
Data hash
ML status
Blockchain timestamp

## Security Concept
The blockchain layer provides tamper-proof logging and traceability. 
The ML layer detects abnormal sensor readings before data/action logging. 
The Raspberry Pi works as an edge security gateway for IoT devices.

## Author
Aditya Siwach
