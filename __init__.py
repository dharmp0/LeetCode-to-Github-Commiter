import os
from pathlib import Path
import subprocess

difficulty = input("Difficulty -  ").lower()
num = int(input("Problem Number -  "))
name = input("Problem Name -  ")
solution = input("Solution- ")

def commiter(difficulty, num, name, solution):

    #formating the file name
    formattedName = name.replace(" ", "_").title()
    formattedNum = f"{num:04}"
    fileName = f"{formattedNum}_{formattedName}"

    #open folder leetCodeSolved[difficulty]
    repo_dir = Path(fr"C:\Users\patel\Downloads\leetCodeSolved\{difficulty}")

    #changes directory to the appropriate one
    os.chdir(repo_dir)


    #add file [problemNumber_problemNameParsed(i.e Two_Sum)]
    #opens file and writes solution
    with open(f"{fileName}.py", "w", encoding="utf-8") as fh:
        fh.write(f"{solution}")

    #run 
    #git add .
    #git commit -m "Create [fileName]"
    #git push origin main
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"{fileName}"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
    except subprocess.CalledProcessError as e:
        print("Git command failed!")
        print("Exit code:", e.returncode)

    return

commiter(difficulty, num, name, solution)