# 🧠 LeetCode-to-GitHub Committer

A Python script that automatically pushes your **LeetCode** solutions to **GitHub**, organized by difficulty inside a `LeetCodeSolved` folder (`easy/`, `medium/`, `hard/`).

---

## ⚙️ Features
- ✍️ Saves files as `0000_Problem_Name.py`
- 💬 Interactive CLI for problem info and solution input
- 🚀 Automatically commits and pushes to your GitHub repo

---

## 🧩 Setup
```bash
git clone https://github.com/<your-username>/LeetCode-to-GitHub-Commiter.git
cd LeetCode-to-GitHub-Commiter
```
- Initialize Git and set remote
  
```bash
git init
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
```

## 🚀 Usage
```bash
python main.py
```

The file will be saved and pushed to:
```bash
LeetCodeSolved/<difficulty>/<formatted_file>.py
```
