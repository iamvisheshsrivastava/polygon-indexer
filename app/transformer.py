from app.db import SessionLocal, Transaction, NetFlow
import datetime

BINANCE_ADDRESSES = {
    "0xF977814e90dA44bFA03b6295A0616a897441aceC",
    "0xe7804c37c13166fF0b37F5aE0BB07A3aEbb6e245",
    "0x505e71695E9bc45943c58adEC1650577BcA68fD9",
    "0x290275e3db66394C52272398959845170E4DCb88",
    "0xD5C08681719445A5Fdce2Bda98b341A49050d821",
    "0x082489A616aB4D46d1947eE3F912e080815b08DA",
}

def update_net_flows():
    db = SessionLocal()

    inflow = db.query(Transaction).filter(Transaction.to_address.in_(BINANCE_ADDRESSES)).all()
    outflow = db.query(Transaction).filter(Transaction.from_address.in_(BINANCE_ADDRESSES)).all()

    inflow_sum = sum([tx.amount for tx in inflow])
    outflow_sum = sum([tx.amount for tx in outflow])

    net = inflow_sum - outflow_sum

    nf = NetFlow(
        exchange="Binance",
        cumulative_inflow=inflow_sum,
        cumulative_outflow=outflow_sum,
        net_flow=net,
        last_updated=datetime.datetime.utcnow(),
    )
    db.add(nf)
    db.commit()

    print(f"📊 Updated Net Flow: {net}")
