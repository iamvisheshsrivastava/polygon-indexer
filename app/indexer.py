import os
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
from app.db import SessionLocal, Transaction, init_db
from app.transformer import update_net_flows  # update dashboard automatically

# Polygon RPC
POLYGON_RPC = os.getenv("POLYGON_RPC", "https://polygon-rpc.com")
w3 = Web3(Web3.HTTPProvider(POLYGON_RPC))

# Inject PoA middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Token contracts (you can track multiple tokens here)
TOKENS = {
    "POL": "0x0000000000000000000000000000000000001010",   # POL / MATIC
    "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", # USDT (for testing, high activity)
}

# ERC20 Transfer event signature
TRANSFER_EVENT_SIG = w3.keccak(text="Transfer(address,address,uint256)").hex()

def listen_blocks():
    init_db()
    db = SessionLocal()

    if not w3.is_connected():
        print("❌ Could not connect to Polygon RPC")
        return
    print("✅ Connected to Polygon")

    latest_block = w3.eth.block_number
    print(f"⛓ Starting at block {latest_block}")

    while True:
        try:
            block = w3.eth.get_block("latest", full_transactions=True)

            for tx in block.transactions:
                if not tx["to"]:
                    continue  # skip if no destination address

                # Only check tokens we care about
                if tx["to"].lower() in [addr.lower() for addr in TOKENS.values()]:
                    receipt = w3.eth.get_transaction_receipt(tx["hash"])

                    for log in receipt["logs"]:
                        try:
                            if log["topics"][0].hex() == TRANSFER_EVENT_SIG:
                                from_addr = "0x" + log["topics"][1].hex()[-40:]
                                to_addr = "0x" + log["topics"][2].hex()[-40:]

                                # Ensure valid numeric value
                                raw_value = log["data"]
                                if isinstance(raw_value, (bytes, bytearray)):
                                    raw_value = raw_value.hex()
                                if isinstance(raw_value, str) and raw_value.startswith("0x"):
                                    value = int(raw_value, 16) / (10**18)
                                else:
                                    continue  # skip if malformed

                                new_tx = Transaction(
                                    block_number=tx["blockNumber"],
                                    tx_hash=tx["hash"].hex(),
                                    from_address=from_addr,
                                    to_address=to_addr,
                                    amount=value,
                                )

                                db.add(new_tx)
                                db.commit()
                                print(f"💸 {value:.4f} token from {from_addr} → {to_addr}")

                                # update Binance net flows
                                update_net_flows()

                        except Exception as log_err:
                            print("⚠️ Log decode error:", log_err)
                            continue

            time.sleep(5)

        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(5)

if __name__ == "__main__":
    listen_blocks()
