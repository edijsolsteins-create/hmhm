import requests
import csv
import time

INPUT_FILE = "addresses_with_balance_note.csv"  # your input CSV (one address per line or with column 'address')
OUTPUT_FILE = "btc_balances_results.csv"
API_URL = "https://blockstream.info/api"

def get_address_info(address):
    """Query Blockstream API for balance & transaction details."""
    try:
        r = requests.get(f"{API_URL}/address/{address}", timeout=10)
        r.raise_for_status()
        data = r.json()

        txs = data.get("chain_stats", {})
        mempool = data.get("mempool_stats", {})

        total_tx = txs.get("tx_count", 0) + mempool.get("tx_count", 0)
        received = txs.get("funded_txo_sum", 0) + mempool.get("funded_txo_sum", 0)
        spent = txs.get("spent_txo_sum", 0) + mempool.get("spent_txo_sum", 0)
        balance = data.get("chain_stats", {}).get("funded_txo_sum", 0) - data.get("chain_stats", {}).get("spent_txo_sum", 0)
        return {
            "address": address,
            "tx_count": total_tx,
            "total_received": received / 1e8,
            "total_sent": spent / 1e8,
            "balance": balance / 1e8,
        }

    except requests.RequestException as e:
        return {"address": address, "error": str(e)}

def main():
    addresses = []

    # Read addresses from CSV (support both plain and columned)
    with open(INPUT_FILE, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row:
                continue
            addr = row[0].strip()
            if addr.lower() == "address":
                continue
            addresses.append(addr)

    print(f"Loaded {len(addresses)} addresses from {INPUT_FILE}")

    results = []
    for i, addr in enumerate(addresses, 1):
        print(f"[{i}/{len(addresses)}] Checking {addr} ...")
        info = get_address_info(addr)
        results.append(info)
        time.sleep(0.5)  # polite delay to avoid rate limits

    # Write results
    fieldnames = ["address", "tx_count", "total_received", "total_sent", "balance", "error"]
    with open(OUTPUT_FILE, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Done! Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
