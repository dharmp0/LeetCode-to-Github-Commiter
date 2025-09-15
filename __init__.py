import os
from pathlib import Path
import subprocess

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
    formattedName = name.replace(" ", "_").title()
    formattedNum = f"{num:04}"
    fileName = f"{formattedNum}_{formattedName}"
    return fileName

def commiter(difficulty, fileName, solution):

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

    return "Committed Successfully"

def main():
    difficulty, num, name = inputs()
    fileName = formated_name(num, name)
    solution = solution_input()
    result = commiter(difficulty, fileName, solution)
    print(result)

if __name__ == "__main__":
    main()