import json
import random
from datetime import datetime, timedelta


# --------- HELPERS ---------

def parse_ts(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def format_ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def random_time(start, end):
    delta = int((end - start).total_seconds())
    rand_seconds = random.randint(0, delta)
    return start + timedelta(seconds=rand_seconds)


def is_real_timestamp(ts):
    return isinstance(ts, str) and "T" in ts


# --------- CORE LOGIC ---------

def resolve_variable(ts):
    """Turn 'ch3' into a random timestamp"""
    if ts in TIME_RANGES:
        start, end = TIME_RANGES[ts]
        start_dt = parse_ts(start)
        end_dt = parse_ts(end)
        return random_time(start_dt, end_dt)
    return None


def process_tweet(tweet):
    # --- MAIN TIMESTAMP HANDLING ---

    if "timestamp" not in tweet:
        # main tweet missing → mark as MISSING and STOP processing children
        tweet["timestamp"] = "MISSING"
        return tweet

    ts = tweet["timestamp"]

    if not is_real_timestamp(ts):
        # variable → resolve
        resolved = resolve_variable(ts)
        if resolved:
            tweet_dt = resolved
            tweet["timestamp"] = format_ts(tweet_dt)
        else:
            tweet["timestamp"] = "MISSING"
            return tweet
    else:
        tweet_dt = parse_ts(ts)

    # --- QUOTE HANDLING ---
    if "quoted" in tweet.get("content", {}):
        quote = tweet["content"]["quoted"]

        if "timestamp" not in quote:
            # must be BEFORE main tweet
            quote_dt = tweet_dt - timedelta(minutes=random.randint(1, 60))
            quote["timestamp"] = format_ts(quote_dt)

        elif not is_real_timestamp(quote["timestamp"]):
            resolved = resolve_variable(quote["timestamp"])
            if resolved:
                # force it BEFORE main tweet
                if resolved >= tweet_dt:
                    resolved = tweet_dt - timedelta(minutes=random.randint(1, 60))
                quote["timestamp"] = format_ts(resolved)

    # --- REPLIES HANDLING ---
    if "replies" in tweet:
        current_time = tweet_dt

        for reply in tweet["replies"]:
            if "timestamp" not in reply:
                # must be AFTER previous
                current_time += timedelta(minutes=random.randint(1, 5))
                reply["timestamp"] = format_ts(current_time)

            elif not is_real_timestamp(reply["timestamp"]):
                resolved = resolve_variable(reply["timestamp"])
                if resolved:
                    if resolved <= current_time:
                        resolved = current_time + timedelta(minutes=random.randint(1, 5))
                    current_time = resolved
                    reply["timestamp"] = format_ts(current_time)
            else:
                reply_dt = parse_ts(reply["timestamp"])

                # enforce ordering
                if reply_dt <= current_time:
                    reply_dt = current_time + timedelta(minutes=random.randint(1, 3))
                    reply["timestamp"] = format_ts(reply_dt)

                current_time = reply_dt

    return tweet

# --------- CONFIG ---------

INPUT_FILE = "timeline_with_stats.json"
OUTPUT_FILE = "timeline_out.json"

# define ranges for variables
# you can add more like "ch1", "ch2", etc.
TIME_RANGES = {
    "ch3": (
        "2026-11-10T02:00:00Z",  # earliest
        "2026-11-10T14:30:00Z",  # latest
    )
}


# --------- RUN ---------

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    output = []
    for tweet in data:
        output.append(process_tweet(tweet))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    print(f"Done → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()