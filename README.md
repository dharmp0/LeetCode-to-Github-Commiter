# 🧠 LeetCode-to-GitHub Committer

A Python tool that automatically fetches your accepted **LeetCode** solutions via the LeetCode GraphQL API and pushes them to **GitHub**, organized by difficulty (`easy/`, `medium/`, `hard/`) with clean naming conventions.

---

## ⚙️ Features
- 🔄 Fetches accepted solutions directly from LeetCode — no manual copy-paste
- 🗂️ Organizes files by difficulty: `easy/`, `medium/`, `hard/`
- ✍️ Clean naming: `0001_Two_Sum.py`, `0015_3Sum.java`
- 🌐 Supports 16 languages (Python, Java, C++, JavaScript, Go, Rust, etc.)
- 🧠 Tracks previously pushed submissions so you're never asked twice
- ✅ Prompts before each push — you stay in control
- 📝 Manual CLI mode still available for quick one-off entries

---

## 🧩 Setup

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/LeetCode-to-GitHub-Commiter.git
cd LeetCode-to-GitHub-Commiter
```

### 2. Install dependencies
```bash
pip install python-dotenv requests questionary
```

### 3. Create a `.env` file
```bash
LEETCODE_SESSION=your_session_cookie
CSRF_TOKEN=your_csrf_token
LEETCODE_USERNAME=your_leetcode_username
```

**To get your cookies:**
1. Go to [leetcode.com](https://leetcode.com) and log in
2. Open DevTools (`F12`) → **Application** tab → **Cookies** → `https://leetcode.com`
3. Copy `LEETCODE_SESSION` and `csrftoken` values

> ⚠️ These cookies expire every few weeks — you'll need to re-grab them when that happens.

### 4. Make sure your solutions repo exists
Your GitHub repo (e.g. `leetCodeSolved`) should be cloned locally with a remote set up:
```bash
cd C:\Users\<you>\Downloads\leetCodeSolved
git remote -v   # should show your GitHub remote
```

---

## 🚀 Usage

### Auto-sync from LeetCode (recommended)
```bash
python leetcode_api.py
```
This fetches your recent accepted submissions and shows an **interactive selection UI**:
```
Found 3 new submission(s) out of 10 recent.

Fetching submission details...

────────────────────────────────────────────────────────────
Use ↑/↓ to navigate, SPACE to select/deselect, ENTER to confirm
────────────────────────────────────────────────────────────

? Select submissions to push to GitHub:
  ○ [E] #0001 - Two Sum (python3)
❯ ● [M] #0015 - 3Sum (java)
  ○ [H] #0042 - Trapping Rain Water (cpp)
```

| Key | Action |
|-----|--------|
| `↑`/`↓` | Navigate between submissions |
| `Space` | Toggle selection (●/○) |
| `Enter` | Push all selected to GitHub |
| `Ctrl+C` | Cancel |

### Manual CLI mode
```bash
python __init__.py
```
Enter problem details and paste your solution manually.

---

## 📁 Output Structure
```
leetCodeSolved/
├── easy/
│   ├── 0001_Two_Sum.py
│   └── 0067_Add_Binary.py
├── medium/
│   └── 0015_3Sum.java
└── hard/
    └── 0042_Trapping_Rain_Water.cpp
```

---

## 🗃️ File Overview
| File | Purpose |
|------|---------|
| `__init__.py` | Core logic: name formatting, git commit & push |
| `leetcode_api.py` | LeetCode GraphQL API integration |
| `.env` | Your LeetCode cookies (not committed) |
| `.seen_submissions.json` | Tracks pushed/skipped submission IDs |
