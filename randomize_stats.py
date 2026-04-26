import json
import random


# --------- CONFIG ---------
RANGES = {
    "priv": (0, 30),
    "small": (30, 120),
    "mid": (200, 800),
    "big": (2000, 8000),
    "hit": (20000, 120000),
}


# --------- HELPERS ---------
def format_number(n):
    if isinstance(n, int) and n >= 1000:
        return f"{n:,}".replace(",", ".")
    return n


def format_stats(stats, is_reply=False):
    if not isinstance(stats, dict):
        return stats

    formatted = {}

    for k, v in stats.items():
        if isinstance(v, int):
            formatted[k] = format_number(v)
        else:
            formatted[k] = v

    return formatted


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def is_full_main_stats(stats):
    return isinstance(stats, dict) and all(
        k in stats for k in ["likes", "retweets", "quote_retweets"]
    )


def is_full_reply_stats(stats):
    return isinstance(stats, dict) and all(
        k in stats for k in ["likes", "retweets", "answers"]
    )


# --------- GENERATION LOGIC ---------
def generate_main_stats_from_var(var):
    if var not in RANGES:
        return None

    low, high = RANGES[var]

    likes = random.randint(low, high)

    # realistic ratios
    retweets = int(likes * random.uniform(0.05, 0.25))
    quote_retweets = int(retweets * random.uniform(0.1, 0.5))

    return {
        "likes": likes,
        "retweets": retweets,
        "quote_retweets": quote_retweets
    }


def generate_reply_stats_from_main(main_likes):
    # replies are MUCH smaller than main tweet
    likes = max(1, int(main_likes * random.uniform(0.005, 0.05)))

    retweets = int(likes * random.uniform(0.05, 0.2))
    answers = int(likes * random.uniform(0.02, 0.15))

    return {
        "likes": likes,
        "retweets": retweets,
        "answers": answers
    }


# --------- PROCESSING ---------
def process_tweet(tweet):
    stats = tweet.get("stats")

    # ---- MAIN TWEET ----
    if stats is None:
        tweet["stats"] = "MISSING"
        main_likes = None

    elif isinstance(stats, str):
        generated = generate_main_stats_from_var(stats)
        if generated:
            tweet["stats"] = format_stats(generated)
            main_likes = generated["likes"]
        else:
            main_likes = None

    elif is_full_main_stats(stats):
        tweet["stats"] = format_stats(stats)
        main_likes = stats["likes"]

    else:
        main_likes = None

    # ---- REPLIES ----
    if "replies" in tweet and main_likes:
        for reply in tweet["replies"]:
            rstats = reply.get("stats")

            if is_full_reply_stats(rstats):
                reply["stats"] = format_stats(rstats)
                continue

            if isinstance(rstats, str):
                gen = generate_main_stats_from_var(rstats)
                if gen:
                    reply["stats"] = format_stats({
                        "likes": gen["likes"],
                        "retweets": gen["retweets"],
                        "answers": int(gen["likes"] * random.uniform(0.02, 0.15))
                    })
                    continue

            reply["stats"] = format_stats(
                generate_reply_stats_from_main(main_likes)
            )

    return tweet


# --------- MAIN ---------
def main():
    data = load_json(INPUT_FILE)

    processed = [process_tweet(t) for t in data]

    save_json(processed, OUTPUT_FILE)

    print(f"Stats generated → {OUTPUT_FILE}")



INPUT_FILE = "lucky_bounce/chp3_twt.json"
OUTPUT_FILE = "timeline_with_stats.json"


if __name__ == "__main__":
    main()