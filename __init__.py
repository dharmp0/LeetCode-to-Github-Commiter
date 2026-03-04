import os
from pathlib import Path
import subprocess

# Map LeetCode language names to file extensions
LANG_EXTENSIONS = {
    "python":      "py",
    "python3":     "py",
    "java":        "java",
    "javascript":  "js",
    "typescript":  "ts",
    "cpp":         "cpp",
    "c":           "c",
    "go":          "go",
    "rust":        "rs",
    "ruby":        "rb",
    "swift":       "swift",
    "kotlin":      "kt",
    "scala":       "scala",
    "csharp":      "cs",
    "php":         "php",
    "dart":        "dart",
}

def inputs():
    difficulty = input("Difficulty -  ").lower()
    num = int(input("Problem Number -  "))
    name = input("Problem Name -  ")
    return difficulty, num, name

def solution_input():
    print("Solution (type 'end' in a new line when finished): ")
    
    solution = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "end":
            break
        solution.append(line)

    solution = '\n'.join(solution) + '\n'
    return solution

def formated_name(num, name):
    #formating the file name
    import re
    # Remove everything that isn't alphanumeric or a space, then convert
    cleaned = re.sub(r"[^a-zA-Z0-9 ]", "", name)
    # Collapse multiple spaces left behind by removed characters
    cleaned = re.sub(r" +", " ", cleaned).strip()
    formattedName = cleaned.replace(" ", "_").title()
    formattedNum = f"{num:04}"
    fileName = f"{formattedNum}_{formattedName}"
    return fileName

def commiter(difficulty, fileName, solution, language="python3"):
    # Determine file extension from language
    ext = LANG_EXTENSIONS.get(language.lower(), "py")

    # Navigate to the repo root
    repo_dir = Path(fr"C:\Users\patel\Downloads\leetCodeSolved")
    os.chdir(repo_dir)

    # Ensure the difficulty subfolder exists
    diff_dir = repo_dir / difficulty
    diff_dir.mkdir(parents=True, exist_ok=True)

    # Write the solution file inside the difficulty folder
    file_path = diff_dir / f"{fileName}.{ext}"
    with open(file_path, "w", encoding="utf-8") as fh:
        fh.write(solution if solution.endswith('\n') else solution + '\n')

    # git add, commit (if there are changes), pull (to sync), then push
    try:
        subprocess.run(["git", "add", "."], check=True)

        # Commit — but don't fail if there's nothing new to commit
        commit_result = subprocess.run(
            ["git", "commit", "-m", f"Add {fileName}"],
            capture_output=True, text=True
        )
        if commit_result.returncode != 0 and "nothing to commit" not in commit_result.stdout:
            print("Git commit failed!")
            print(commit_result.stderr)
            return f"Git commit failed! Exit code: {commit_result.returncode}"

        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
    except subprocess.CalledProcessError as e:
        print("Git command failed!")
        print("Exit code:", e.returncode)
        return f"Git command failed! Exit code: {e.returncode}"

    return "Committed Successfully"

def main():
    difficulty, num, name = inputs()
    fileName = formated_name(num, name)
    solution = solution_input()
    result = commiter(difficulty, fileName, solution)
    print(result)

if __name__ == "__main__":
    main()