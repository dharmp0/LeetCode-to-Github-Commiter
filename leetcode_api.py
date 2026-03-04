import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Import your existing committer logic
from __init__ import formated_name, commiter, LANG_EXTENSIONS

load_dotenv()

SESSION = os.getenv("LEETCODE_SESSION")
CSRF = os.getenv("CSRF_TOKEN")
USERNAME = os.getenv("LEETCODE_USERNAME")

HEADERS = {
    "Cookie": f"LEETCODE_SESSION={SESSION}; csrftoken={CSRF}",
    "x-csrftoken": CSRF,
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
}

# File to persist already-pushed submission IDs across restarts
SEEN_FILE = Path(__file__).parent / ".seen_submissions.json"


def load_seen():
    """Load the set of submission IDs we've already processed."""
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen: set):
    """Persist the seen set to disk."""
    SEEN_FILE.write_text(json.dumps(list(seen)))


# ── LeetCode GraphQL helpers ────────────────────────────────────────────────

def get_recent_submissions(limit=10):
    """Fetch the most recent accepted submissions for the configured user."""
    query = """
    query recentAcSubmissions($username: String!, $limit: Int!) {
        recentAcSubmissionList(username: $username, limit: $limit) {
            id
            title
            titleSlug
            timestamp
        }
    }
    """
    resp = requests.post(
        "https://leetcode.com/graphql",
        json={"query": query, "variables": {"username": USERNAME, "limit": limit}},
        headers=HEADERS,
    )
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        print("GraphQL errors:", data["errors"])
        return []

    return data["data"]["recentAcSubmissionList"]


def get_submission_detail(submission_id):
    """Fetch code, language, and problem metadata for a single submission."""
    query = """
    query submissionDetails($submissionId: Int!) {
        submissionDetails(submissionId: $submissionId) {
            code
            lang {
                name
            }
            question {
                questionId
                title
                difficulty
            }
        }
    }
    """
    resp = requests.post(
        "https://leetcode.com/graphql",
        json={
            "query": query,
            "variables": {"submissionId": int(submission_id)},
        },
        headers=HEADERS,
    )
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        print("GraphQL errors:", data["errors"])
        return None

    return data["data"]["submissionDetails"]


# ── Process a single submission ──────────────────────────────────────────────

def process_submission(sub):
    """Fetch full details for a submission and push it to GitHub."""
    detail = get_submission_detail(sub["id"])
    if not detail:
        print(f"  Could not fetch details for submission {sub['id']}, skipping.")
        return False

    question = detail["question"]
    difficulty = question["difficulty"].lower()   # easy / medium / hard
    num = int(question["questionId"])
    name = question["title"]
    language = detail["lang"]["name"]             # e.g. "python3", "java"
    code = detail["code"]

    file_name = formated_name(num, name)
    ext = LANG_EXTENSIONS.get(language.lower(), "py")

    print(f"\n  Problem:    #{num} – {name}")
    print(f"  Difficulty: {difficulty}")
    print(f"  Language:   {language}")
    print(f"  File:       {file_name}.{ext}")

    choice = input("  Push to GitHub? (y/s/n)\n  y = push, s = skip forever, n = skip for now: ").strip().lower()
    if choice == "y":
        result = commiter(difficulty, file_name, code, language)
        print(f"  \u2192 {result}")
        return "pushed"
    elif choice == "s":
        print("  Skipped permanently.")
        return "skipped"
    else:
        print("  Skipped for now (will ask again next run).")
        return "later"

# ── One-shot mode: process recent submissions right now ──────────────────────

def sync_recent(limit=10):
    """One-shot: fetch the last `limit` accepted submissions and offer to push."""
    seen = load_seen()
    submissions = get_recent_submissions(limit)

    if not submissions:
        print("No recent accepted submissions found.")
        return

    new_subs = [s for s in submissions if s["id"] not in seen]

    if not new_subs:
        print("All recent submissions already pushed. Nothing to do.")
        return

    print(f"Found {len(new_subs)} new submission(s) out of {len(submissions)} recent.\n")

    for sub in new_subs:
        print(f"  • {sub['title']}")

    for sub in new_subs:
        print(f"\n── {sub['title']} (id {sub['id']}) ──")
        result = process_submission(sub)

        # Only mark as seen if pushed or explicitly skipped forever
        if result in ("pushed", "skipped"):
            seen.add(sub["id"])
            save_seen(seen)

    print("\nDone.")


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Quick sanity check
    if not SESSION or not CSRF or not USERNAME:
        print("ERROR: Missing environment variables.")
        print("Make sure your .env file has LEETCODE_SESSION, CSRF_TOKEN, and LEETCODE_USERNAME.")
        exit(1)

    sync_recent(limit=10)
