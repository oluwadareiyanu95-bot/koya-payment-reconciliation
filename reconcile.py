
"""Payment reconciliation."""

import json
from datetime import datetime
from decimal import Decimal

latest_events = {}

with open("payments.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if not isinstance(event, dict) or not event.get("txn_id"):
            continue

        txn_id = event["txn_id"]

        timestamp = datetime.fromisoformat(
            event["ts"].replace("Z", "+00:00")
        )

        if (
            txn_id not in latest_events
            or timestamp >= latest_events[txn_id]["timestamp"]
        ):
            latest_events[txn_id] = {
                "timestamp": timestamp,
                "event": event
            }

total = Decimal("0")
count = 0

for record in latest_events.values():
    event = record["event"]

    if event["status"] == "success":
        amount = Decimal(str(event["amount"]).replace(",", ""))
        total += amount
        count += 1

with open("expected.txt", "r", encoding="utf-8") as f:
    expected = int(f.read().strip())

if count != expected:
    print(
        f"Check failed: counted {count} successful payments, "
        f"expected {expected}."
    )
    print("Something in the data isn't being handled correctly.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
