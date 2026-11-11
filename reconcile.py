
#!/usr/bin/env python3
"""Payment reconciliation."""

import json
from datetime import datetime
from decimal import Decimal

# Store the latest event for each transaction ID
latest_events = {}

with open("payments.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            # Ignore unreadable lines
            continue

        # Ignore events without a transaction ID
        if not isinstance(event, dict) or not event.get("txn_id"):
            continue

        txn_id = event["txn_id"]

        # Convert the timestamp into a comparable datetime
        timestamp = datetime.fromisoformat(
            event["ts"].replace("Z", "+00:00")
        )

        # Keep only the latest attempt for each transaction
        if (
            txn_id not in latest_events
            or timestamp >= latest_events[txn_id]["timestamp"]
        ):
            latest_events[txn_id] = {
                "timestamp": timestamp,
                "event": event
            }

# Calculate successful payments using only the latest attempts
total = Decimal("0")
count = 0

for record in latest_events.values():
    event = record["event"]

    if event["status"] == "success":
        amount = Decimal(str(event["amount"]).replace(",", ""))
        total += amount
        count += 1

# Compare with the expected payment count
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
