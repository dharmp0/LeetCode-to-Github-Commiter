import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import questionary
from questionary import Style

# Import your existing committer logic
from __init__ import formated_name, commiter, LANG_EXTENSIONS

# Matrix-style black/green theme
CLI_STYLE = Style([
    ('qmark', 'fg:#00ff00 bold'),           # Bright green question mark
    ('question', 'fg:#00ff00 bold'),         # Bright green question text
    ('pointer', 'fg:#00ff00 bold'),          # Green arrow pointer
    ('highlighted', 'fg:#00ff00 bold'),      # Highlighted option
    ('selected', 'fg:#00ff00 bold'),         # Selected checkbox
    ('text', 'fg:#00ff00'),                  # Regular text
    ('answer', 'fg:#00ff00 bold'),           # Answer confirmation
    ('instruction', 'fg:#008800'),           # Dimmer green for instructions
])

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

# ── Interactive selection UI ─────────────────────────────────────────────────

def get_submission_preview(sub):
    """Fetch details for a submission to show in the selection UI."""
    detail = get_submission_detail(sub["id"])
    if not detail:
        return None
    return {
        "id": sub["id"],
        "title": sub["title"],
        "titleSlug": sub["titleSlug"],
        "difficulty": detail["question"]["difficulty"],
        "language": detail["lang"]["name"],
        "questionId": detail["question"]["questionId"],
        "code": detail["code"],
    }


def interactive_select_submissions(submissions):
    """Display an interactive checkbox UI for selecting submissions to push."""
    print("\n\033[32mFetching submission details...\033[0m")
    
    # Fetch details for all submissions
    detailed_subs = []
    for sub in submissions:
        preview = get_submission_preview(sub)
        if preview:
            detailed_subs.append(preview)
        else:
            print(f"\033[32m  Could not fetch details for '{sub['title']}', skipping.\033[0m")
    
    if not detailed_subs:
        print("\033[32mNo submissions to display.\033[0m")
        return [], []
    
    # Build choices for the checkbox UI
    # Format: numbered DOS-style menu
    choices = []
    for i, sub in enumerate(detailed_subs, 1):
        diff = sub["difficulty"].upper()
        num = int(sub["questionId"])
        # Pad title for alignment
        title = sub['title'][:35].ljust(35)
        lang = sub['language']
        label = f"{i:2}. #{num:04d}  {title}  [{diff:6}]  {lang}"
        choices.append(questionary.Choice(title=label, value=sub))
    
    # Matrix-style header
    print("\n\033[32m" + "═" * 70)
    print("║" + " " * 20 + "LEETCODE SUBMISSION SELECTOR" + " " * 20 + "║")
    print("═" * 70)
    print("║  ↑/↓ Navigate       SPACE Select/Deselect       ENTER Continue     ║")
    print("═" * 70 + "\033[0m\n")
    
    try:
        selected = questionary.checkbox(
            "Select submissions:",
            choices=choices,
            style=CLI_STYLE,
            instruction="",
        ).ask()
    except KeyboardInterrupt:
        print("\n\033[32mCancelled.\033[0m")
        return [], []
    
    # Handle Ctrl+C or escape
    if selected is None:
        print("\n\033[32mCancelled.\033[0m")
        return [], []
    
    # If nothing selected, ask if they want to quit or continue
    if not selected:
        print("\n\033[32mNo submissions selected.\033[0m")
        try:
            action = questionary.select(
                "What would you like to do?",
                choices=[
                    questionary.Choice("Quit", value="quit"),
                    questionary.Choice("Go back and select", value="retry"),
                ],
                style=CLI_STYLE,
            ).ask()
        except KeyboardInterrupt:
            return [], []
        
        if action == "retry":
            return interactive_select_submissions(submissions)
        return [], []
    
    # Ask what to do with selected submissions
    print(f"\n\033[32m{len(selected)} submission(s) selected.\033[0m")
    try:
        action = questionary.select(
            "Action for selected:",
            choices=[
                questionary.Choice("⬆ PUSH to GitHub", value="push"),
                questionary.Choice("⏭ SKIP FOREVER (already uploaded)", value="skip"),
                questionary.Choice("✖ Cancel", value="cancel"),
            ],
            style=CLI_STYLE,
        ).ask()
    except KeyboardInterrupt:
        print("\n\033[32mCancelled.\033[0m")
        return [], []
    
    if action == "push":
        return selected, []
    elif action == "skip":
        return [], selected
    else:
        print("\n\033[32mCancelled.\033[0m")
        return [], []


def batch_process_submissions(selected_subs, seen):
    """Process and push all selected submissions to GitHub."""
    if not selected_subs:
        print("\033[32mNo submissions selected.\033[0m")
        return
    
    print(f"\n\033[32m{'═' * 70}")
    print(f"  PUSHING {len(selected_subs)} SUBMISSION(S) TO GITHUB...")
    print(f"{'═' * 70}\033[0m\n")
    
    pushed_count = 0
    for i, sub in enumerate(selected_subs, 1):
        difficulty = sub["difficulty"].lower()
        num = int(sub["questionId"])
        name = sub["title"]
        language = sub["language"]
        code = sub["code"]
        
        file_name = formated_name(num, name)
        ext = LANG_EXTENSIONS.get(language.lower(), "py")
        
        print(f"\033[32m[{i}/{len(selected_subs)}] #{num:04d} – {name} ({language})...\033[0m")
        
        result = commiter(difficulty, file_name, code, language)
        
        if "Successfully" in result:
            print(f"\033[32m     ✓ {file_name}.{ext}\033[0m")
            seen.add(sub["id"])
            save_seen(seen)
            pushed_count += 1
        else:
            print(f"\033[31m     ✗ Failed: {result}\033[0m")
    
    print(f"\n\033[32m{'═' * 70}")
    print(f"  COMPLETE: {pushed_count}/{len(selected_subs)} submission(s) pushed successfully")
    print(f"{'═' * 70}\033[0m")


# ── One-shot mode: process recent submissions right now ──────────────────────

def sync_recent(limit=10):
    """One-shot: fetch the last `limit` accepted submissions and offer to push."""
    seen = load_seen()
    submissions = get_recent_submissions(limit)

    if not submissions:
        print("\033[32mNo recent accepted submissions found.\033[0m")
        return

    new_subs = [s for s in submissions if s["id"] not in seen]

    if not new_subs:
        print("\033[32mAll recent submissions already pushed. Nothing to do.\033[0m")
        return

    print(f"\033[32mFound {len(new_subs)} new submission(s) out of {len(submissions)} recent.\033[0m")
    
    # Use interactive selection UI
    selected, skip_forever = interactive_select_submissions(new_subs)
    
    # Mark skipped submissions as seen (won't ask again)
    if skip_forever:
        for sub in skip_forever:
            seen.add(sub["id"])
        save_seen(seen)
        print(f"\033[32m\nMarked {len(skip_forever)} submission(s) as skipped forever.\033[0m")
    
    # Process all selected submissions
    batch_process_submissions(selected, seen)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Quick sanity check
    if not SESSION or not CSRF or not USERNAME:
        print("\033[31mERROR: Missing environment variables.\033[0m")
        print("\033[31mMake sure your .env file has LEETCODE_SESSION, CSRF_TOKEN, and LEETCODE_USERNAME.\033[0m")
        exit(1)

    sync_recent(limit=10)
