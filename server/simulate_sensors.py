"""
simulate_sensors.py — keeps CitySense fed with fresh readings forever

Replaces the one-shot generate_data.py workflow. Writes new rows on a
fixed cadence (default 15 minutes, deliberately matching CPCB's CAAQMS
transmission protocol: stations transmit 15-minute averages at
:00 / :15 / :30 / :45) and backfills whatever gap exists between the
newest stored reading and now, so dashboards never go stale.

Run ONE instance only (there is no cross-instance lock).

Usage (from server/, in its own terminal alongside uvicorn):
    python simulate_sensors.py                  # backfill + live loop
    python simulate_sensors.py --once           # one transmission, exit
    python simulate_sensors.py --interval 300   # PurpleAir-style 5 min
"""

import argparse
import random
import sys
import time
from datetime import datetime, timedelta

from database import SessionLocal
from generate_data import (
    generate_realistic_humidity,
    generate_realistic_pm25,
    generate_realistic_temperature,
)
from models import Reading, Sensor

BATCH_SIZE = 5000


def make_reading(sensor: Sensor, when: datetime) -> Reading:
    """One synthetic measurement using the SAME formulas as generate_data.py,
    so patterns stay consistent with what the ML model learned."""
    temp = generate_realistic_temperature(when.hour)
    humidity = generate_realistic_humidity(temp)
    pm25 = generate_realistic_pm25(when.hour, when.weekday() >= 5)
    return Reading(
        sensor_id=sensor.id,
        temperature=temp,
        humidity=humidity,
        pm25=pm25,
        pm10=round(pm25 * random.uniform(1.5, 2.0), 2),
        timestamp=when,
    )


def latest_timestamp(db):
    row = db.query(Reading.timestamp).order_by(Reading.timestamp.desc()).first()
    return row[0] if row else None


def next_boundary(epoch_seconds: float, interval: int) -> float:
    """Next interval-aligned instant (CPCB style: :00 :15 :30 :45)."""
    return (int(epoch_seconds) // interval + 1) * interval


def backfill(db, sensors, interval: int) -> int:
    """Generate readings from just after the newest stored timestamp up to
    the current interval boundary. Returns number of rows inserted."""
    latest = latest_timestamp(db)
    if latest is None:
        sys.exit("No readings found. Run 'python generate_data.py' first.")

    now_epoch = time.time()
    first_slot = next_boundary(latest.timestamp(), interval)

    if first_slot > now_epoch:
        return 0

    slot_dt = timedelta(seconds=interval)
    buffered, total, slots = [], 0, 0
    slot = datetime.fromtimestamp(first_slot)

    while slot.timestamp() <= now_epoch:
        for sensor in sensors:
            buffered.append(make_reading(sensor, slot))
        total += len(sensors)
        slots += 1
        if len(buffered) >= BATCH_SIZE:
            db.add_all(buffered)
            db.commit()
            print(f"  backfilled up to {slot:%Y-%m-%d %H:%M} ({total} rows)")
            buffered = []
        slot += slot_dt

    if buffered:
        db.add_all(buffered)
        db.commit()

    print(f"Backfilled {slots} slots x {len(sensors)} sensors = {total} readings "
          f"(gap covered: {latest:%Y-%m-%d %H:%M} -> now)")
    return total


def write_cycle(db, sensors, when: datetime) -> int:
    """One transmission round. Skips if this exact slot already has rows
    (protects against accidental double-starts)."""
    if db.query(Reading.id).filter(Reading.timestamp == when).first():
        return 0
    db.add_all(make_reading(sensor, when) for sensor in sensors)
    db.commit()
    return len(sensors)


def main():
    parser = argparse.ArgumentParser(description="CitySense sensor simulator")
    parser.add_argument("--interval", type=int, default=900,
                        help="seconds between transmissions (default 900 = 15 min, CPCB CAAQMS)")
    parser.add_argument("--once", action="store_true",
                        help="run one transmission cycle and exit (good for cron)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        sensors = db.query(Sensor).all()
        if not sensors:
            sys.exit("No sensors found. Run 'python generate_data.py' first.")

        print(f"CitySense simulator | {len(sensors)} sensors | "
              f"interval {args.interval}s ({args.interval // 60} min)")

        if backfill(db, sensors, args.interval) == 0:
            print("No gap to backfill - data is current.")

        if args.once:
            # Cron-style: stamp the CURRENT interval slot (floor), not a future one
            epoch = int(time.time())
            target = datetime.fromtimestamp(epoch - (epoch % args.interval))
            print(f"--once: wrote {write_cycle(db, sensors, target)} rows @ {target:%H:%M}")
            return

        print("Live mode started. Ctrl+C to stop.")
        while True:
            target_epoch = next_boundary(time.time(), args.interval)
            target_dt = datetime.fromtimestamp(target_epoch)
            delay = max(target_epoch - time.time(), 0) + 0.5
            print(f"next transmission {target_dt:%H:%M:%S} (sleeping {delay:.0f}s)")
            time.sleep(delay)

            written = write_cycle(db, sensors, target_dt)
            state = f"wrote {written} readings" if written else "slot already filled, skipped"
            print(f"[{datetime.now():%H:%M:%S}] {target_dt:%H:%M} -> {state}")

    except KeyboardInterrupt:
        print("\nSimulator stopped.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
