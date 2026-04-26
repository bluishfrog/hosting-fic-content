import randomize_stats
import randomize_time
import timeline_builder


# --------- CONFIG (ONLY EDIT HERE) ---------
ACCOUNTS_FILE = "twitter_accounts/lucky_bounce_lib.json"
TIMELINE_FILE = "lucky_bounce/chp3_twt.json"
OUTPUT_FILE = "output.html"

# temp files between steps
STATS_FILE = "timeline_with_stats.json"
TIME_FILE = "timeline_out.json"


# --------- RUN PIPELINE ---------
def main():
    print("Step 1: Generating stats...")
    randomize_stats.INPUT_FILE = TIMELINE_FILE
    randomize_stats.OUTPUT_FILE = STATS_FILE
    randomize_stats.main()

    print("Step 2: Assigning timestamps...")
    randomize_time.INPUT_FILE = STATS_FILE
    randomize_time.OUTPUT_FILE = TIME_FILE
    randomize_time.main()

    print("Step 3: Building HTML...")
    timeline_builder.ACCOUNTS_FILE = ACCOUNTS_FILE
    timeline_builder.TIMELINE_FILE = TIME_FILE
    timeline_builder.OUTPUT_FILE = OUTPUT_FILE
    timeline_builder.main()

    print(f"\nAll done → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()