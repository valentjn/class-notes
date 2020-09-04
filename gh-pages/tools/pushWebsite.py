#!/usr/bin/python3

import os
import subprocess

def main():
  os.chdir(os.path.join(os.path.dirname(__file__), ".."))
  if os.path.isdir(".git"): shutil.rmdir(".git")

  subprocess.run(["git", "init", "-b", "gh-pages"])
  subprocess.run(["git", "add", "."])
  subprocess.run(["git", "add", "-f", "_data/sidebars/sidebar.yml"])
  subprocess.run(["git", "add", "-f", "_includes/lectures"])
  subprocess.run(["git", "add", "-f", "images/lectures"])
  subprocess.run(["git", "add", "-f", "pages/index.md", "pages/lectures"])
  subprocess.run(["git", "commit", "-m", "Update gh-pages"])
  subprocess.run(["git", "remote", "add", "origin", "git@github.com:valentjn/class-notes.git"])
  subprocess.run(["git", "push", "-f", "origin", "gh-pages"])

  shutil.rmdir(".git")



if __name__ == "__main__":
  main()
