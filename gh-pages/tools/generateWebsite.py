#!/usr/bin/python3

import html
import os
import re
import shutil

def copyFile(srcPath, destPath):
  print(f"Copying '{srcPath}' to '{destPath}'...")
  shutil.copy(srcPath, destPath)

def copyDir(srcPath, destPath):
  print(f"Copying '{srcPath}' to '{destPath}'...")
  shutil.copytree(srcPath, destPath)

def deleteDir(dirPath):
  if os.path.isdir(dirPath):
    print(f"Deleting '{dirPath}'...")
    shutil.rmtree(dirPath)

def createDir(dirPath):
  print(f"Creating directory '{dirPath}'...")
  os.mkdir(dirPath)

def writeFile(filePath, s):
  print(f"Writing file '{filePath}'...")
  with open(filePath, "w") as f: f.write(s)

def convertHtmlTitleToTextTitle(s):
  s = html.unescape(s)
  s = re.sub(r"<span class=\"textsc\" >(.*?)</span>", r"\1", s)
  s = re.sub(r"<em>(.*?)</em>", r"\1", s)
  s = re.sub(r"<kbd>(.*?)</kbd>", r"\1", s)
  s = s.replace("\\(\\mathbb {C}\\)", "\u2102")
  s = s.replace("\\(\\mathbb {R}\\)", "\u211d")
  s = re.sub(r"\\\((.*?)\\\)", r"\1", s)
  s = s.replace("M ATLAB", "MATLAB")
  return s

def convertTextTitleToSlug(s):
  s = s.lower()
  s = s.replace("\u00e4", "ae").replace("\u00f6", "oe").replace("\u00fc", "ue")
  s = re.sub("([aou])\u0308", r"\1e", s)
  s = s.replace("\u00df", "ss")
  s = s.replace("\u00e9", "e")
  s = s.replace(" ", "-")
  s = re.sub(r"[^a-z0-9\-]", "", s)
  s = re.sub(r"--+", "-", s)
  return s

def replaceSubsectionHeading(match):
  htmlTitle = match.group(1)
  slug = convertTextTitleToSlug(convertHtmlTitleToTextTitle(htmlTitle))
  return f"<h2 id=\"{slug}\">{htmlTitle}</h2>"

def replaceSubsubsectionHeading(match):
  htmlTitle = match.group(1)
  slug = convertTextTitleToSlug(convertHtmlTitleToTextTitle(htmlTitle))
  return f"<h3 id=\"{slug}\">{htmlTitle}</h3>"

def extractSections(lecture):
  with open(os.path.join("..", "build", "lectures", lecture, f"{lecture}.html"), "r") as f:
    html_ = f.read()

  createDir(os.path.join("_includes", "lectures", lecture))
  createDir(os.path.join("pages", "lectures", lecture))

  mathJaxDefinitions = re.search(r"<div\s+class=\"hidden\"\s*>.*?</\s*div\s*>", html_,
      flags=re.DOTALL).group()
  matches = list(re.finditer(r"<p>\s*[0-9]+(?:\s|&#x2002;|&#x2003;)+(.+?)\s*<p>\s*</p>", html_))

  for i in range(len(matches)):
    match = matches[i]
    title = convertHtmlTitleToTextTitle(match.group(1))
    slug = convertTextTitleToSlug(title)

    sectionEndPos = (matches[i+1].start() if i < len(matches) - 1 else
        re.search(r"-autofile-last\"></a>", html_).end())
    sectionHtml = html_[match.end():sectionEndPos]

    sectionHtml = re.sub(r"<p>\s*[0-9]+\.[0-9]+(?:\s|&#x2002;|&#x2003;)+(.+?)\s*<p>\s*</p>",
        replaceSubsectionHeading, sectionHtml)
    sectionHtml = re.sub(r"<p>\s*[0-9]+\.[0-9]+\.[0-9]+(?:\s|&#x2002;|&#x2003;)+(.+?)\s*<p>\s*</p>",
        replaceSubsubsectionHeading, sectionHtml)
    sectionHtml = sectionHtml.replace(f"{lecture}-images/",
        f"/class-notes/images/lectures/{lecture}/")
    sectionHtml = f"""
{{% raw %}}
{mathJaxDefinitions}

<div class="lwarp-contents">
{sectionHtml}
</div>
{{% endraw %}}"""
    writeFile(os.path.join("_includes", "lectures", lecture, f"{slug}.html"), sectionHtml)

    sectionMarkdown = f"""
---
title: "{title}"
permalink: "/{lecture}/{slug}.html"
sidebar: "sidebar"
toc: false
---

{{% include lectures/{lecture}/{slug}.html %}}""".lstrip()
    writeFile(os.path.join("pages", "lectures", lecture, f"{slug}.md"), sectionMarkdown)

def main():
  os.chdir(os.path.join(os.path.dirname(__file__), ".."))

  copyFile(os.path.join("..", "LICENSE.md"), ".")
  copyFile(os.path.join("..", "README.md"), ".")

  deleteDir(os.path.join("_includes", "lectures"))
  createDir(os.path.join("_includes", "lectures"))
  deleteDir(os.path.join("pages", "lectures"))
  createDir(os.path.join("pages", "lectures"))

  lectures = sorted(os.listdir(os.path.join("..", "src", "lectures")))
  lectures = [x for x in lectures if os.path.isdir(os.path.join("..", "src", "lectures", x))]

  for lecture in lectures:
    imagesDirPath = os.path.join("images", "lectures", lecture)
    deleteDir(imagesDirPath)
    imagesSrcDirPath = os.path.join("..", "build", "lectures", lecture, f"{lecture}-images")
    if len(os.listdir(imagesSrcDirPath)) > 0: copyDir(imagesSrcDirPath, imagesDirPath)

    extractSections(lecture)



if __name__ == "__main__":
  main()
