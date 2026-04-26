import json
from datetime import datetime
import re

# --------- HELPERS ---------

def cleanup_html(html):
    # 1. Remove empty lines
    lines = [line.strip() for line in html.splitlines() if line.strip()]

    cleaned = "\n".join(lines)

    # 2. Remove empty <p></p> INSIDE .twt blocks only
    def clean_twt_block(match):
        block = match.group(0)
        # remove empty <p> or <p> </p> inside tweet
        block = re.sub(r"<p>\s*</p>", "", block)
        return block

    cleaned = re.sub(r'<div class="twt">.*?</div>', clean_twt_block, cleaned, flags=re.DOTALL)

    # 3. Pretty format (basic indentation)
    indent = 0
    pretty_lines = []

    for line in cleaned.splitlines():
        # decrease indent on closing tags
        if re.match(r"</", line):
            indent -= 1

        pretty_lines.append("    " * max(indent, 0) + line)

        # increase indent on opening tags (but not self-closing or inline)
        if re.match(r"<[^/!][^>]*[^/]>", line) and not re.search(r"</", line):
            indent += 1

    return "\n".join(pretty_lines)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_timestamp(ts):
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))

    hour = dt.strftime("%I").lstrip("0") or "0"
    day = dt.strftime("%d").lstrip("0") or "0"

    return f"{hour}:{dt.strftime('%M %p')} · {dt.strftime('%b')} {day}, {dt.strftime('%Y')}"


def format_timestamp_quote_and_reply(ts):
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))

    hour = dt.strftime("%I").lstrip("0") or "0"
    day = dt.strftime("%d").lstrip("0") or "0"

    return f"{dt.strftime('%b')} {day}, {dt.strftime('%Y')}"


def build_account_lookup(accounts):
    lookup = {}
    for acc in accounts:
        if "handle" in acc:
            lookup[acc["handle"]] = acc
    return lookup


def render_tags(tags):
    if not tags:
        return ""
    return " ".join([f'<span class="twt-hl">#{t}</span>' for t in tags])


def render_stats(stats):
    return f"""
    <div class="twt-stat1">
        <p><strong>{stats.get("retweets",0)}</strong> Retweets 
        <strong>{stats.get("quote_retweets",0)}</strong> Quote Tweets 
        <strong>{stats.get("likes",0)}</strong> Likes</p>
    </div>
    """


def render_reply_stats(stats):
    return f"""
    <div class="twt-stat2">
        <div class="twt-social">
            <p><img class="twt-socialimg" src="https://i.imgur.com/dJg9v1v.png">{stats.get("answers",0)}</p>
        </div>
        <div class="twt-social">
            <p><img class="twt-socialimg" src="https://i.imgur.com/UeOnwXk.png">{stats.get("retweets",0)}</p>
        </div>
        <div class="twt-social">
            <p><img class="twt-socialimg" src="https://i.imgur.com/eM56CN2.png">{stats.get("likes",0)}</p>
        </div>
    </div>
    """


def render_media(media):
    if not media:
        return ""

    if media.startswith("http://") or media.startswith("https://"):
        src = media
    else:
        src = MEDIA_PREFIX + media + "?raw=true"

    return src


def render_header(account):

    link_icon = render_media(account.get("icon"))

    return f"""
    <div class="twt-header">
        <div class="twt-icon-container">
            <p><img class="twt-icon" src="{link_icon}"></p>
        </div>
        <div class="twt-id">
            <p><span class="twt-name">{account.get("name","")}</span><br />
            <span class="twt-handle">@{account.get("handle","")}</span></p>
        </div>
    </div>
    """


def render_quote(quote, accounts):
    acc = accounts.get(quote["author"], {})
    if "media" in quote["content"]:
            media_html = f'<img class="twt-image" src="{render_media(quote["content"].get("media"))}">'

    return f"""
    <div class="twt-quotebox">
        <div class="twt-header">
            <div class="twt-icon-container">
                <p><img class="twt-iconquote" src="{acc.get("icon","")}"></p>
            </div>
            <div class="twt-id">
                <p><span class="twt-name">{acc.get("name","")}</span> 
                <span class="twt-handle">@{acc.get("handle","")} · {format_timestamp_quote_and_reply(quote["timestamp"])}</span></p>
            </div>
        </div>
        <div class="twt-contentquote">
            <p>{quote["content"].get("text","")}</p>
        </div>
        <p>{media_html}</p>
    </div>
    """


def render_replies(replies, accounts):
    html = ""
    for r in replies:
        fromacc = accounts.get(r["author"], {})
        toacc = accounts.get(r["replyingto"], {})

        media_html = ""
        if "media" in r["content"]:
            media_html = f'<img class="twt-image" src="{render_media(r["content"].get("media"))}">'

        html += f"""
        <hr class="twt-sep-reply">
        <div class="twt-replybox">
            <div class="twt-icon-replycontainer">
                <p><img class="twt-icon" src="{render_media(fromacc.get("icon",""))}"></p>
            </div>
            <div class="twt-replycontainer">
                <p><span class="twt-name">{fromacc.get("name","")}</span> 
                <span class="twt-handle">@{fromacc.get("handle","")} · {format_timestamp_quote_and_reply(r["timestamp"])}</span><br />
                <span class="twt-handle">Replying to</span> 
                <span class="twt-hl">@{toacc.get("handle","")}</span>
                </p>
                <div class="twt-replycontent">
                    <p>{r["content"].get("text","")}</p>
                    
                </div>
                <p>{media_html}</p>
                {render_reply_stats(r.get("stats", {}))}
            </div>
        </div>
        """
    return html


# --------- MAIN RENDER ---------
def render_tweet(tweet, accounts):
    acc = accounts.get(tweet["author"], {})
    content = tweet["content"]

    quote_html = ""
    if "quoted" in content:
        quote_html = render_quote(content["quoted"], accounts)

    tags_html = ""
    if "tags" in content: 
        tags_html = render_tags(content.get("tags", []))

    media_html = ""
    if "media" in content:
        media_html = f'<img class="twt-image" src="{render_media(content.get("media"))}">'

    return f"""
    <div class="twt">
        {render_header(acc)}
        <div class="twt-content">
            <p>{content.get("text","")}</p>
            
        </div>
        <p>{media_html}</p>
        <p>{tags_html}</p>

        {quote_html}

        <div class="twt-timestamp">
            <p>{format_timestamp(tweet["timestamp"])}</p>
        </div>

        <hr class="twt-sep">

        {render_stats(tweet.get("stats", {}))}

        {render_replies(tweet.get("replies", []), accounts)}
    </div>
    <p> </p>
    """


# --------- RUN ---------
def main():
    accounts = load_json(ACCOUNTS_FILE)
    timeline = load_json(TIMELINE_FILE)

    account_lookup = build_account_lookup(accounts)

    html_output = ""
    for tweet in timeline:
        html_output += render_tweet(tweet, account_lookup)

    html_output = cleanup_html(html_output)  # <-- ADD THIS

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_output)

    print(f"HTML generated → {OUTPUT_FILE}")



# --------- CONFIG ---------
ACCOUNTS_FILE = "twitter_accounts/lucky_bounce_lib.json"
TIMELINE_FILE = "lucky_bounce/chp3_twt.json"
OUTPUT_FILE = "output.html"
MEDIA_PREFIX = "https://github.com/bluishfrog/hosting-fic-content/blob/main/"


if __name__ == "__main__":
    main()