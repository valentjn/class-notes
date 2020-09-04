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
  s = s.replace("\\mathbb {C}", "\u2102").replace("\\mathbb {R}", "\u211d").replace("^n", "\u207f")
  s = re.sub(r"\\\((.*?)\\\)", r"\1", s)
  s = s.replace("M ATLAB", "MATLAB")
  return s

def convertTextTitleToSlug(s):
  s = s.lower()
  s = s.replace("\u00e4", "ae").replace("\u00f6", "oe").replace("\u00fc", "ue")
  s = re.sub("([aou])\u0308", r"\1e", s)
  s = s.replace("\u00df", "ss")
  s = s.replace("\u00e9", "e")
  s = s.replace("\u2102", "c").replace("\u211d", "r").replace("\u207f", "n")
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

class ListItemReplacer(object):
  def __init__(self):
    self.css = ""
    self.cssClassCounter = 0

  def replace(self, match):
    cssClass = f"list-item-f{self.cssClassCounter}"
    self.cssClassCounter += 1

    self.css += f".lwarp-contents li.{cssClass}::marker {{\n"

    marker = match.group(2)
    self.css += f"  content:'{marker}\\00a0\\00a0';\n"

    if match.group(1) == "<em>": self.css += "  font-style:italic;\n"
    elif match.group(1) == "<b>": self.css += "  font-weight:bold;\n"

    self.css += "}\n"

    return f"<li class=\"{cssClass}\"><p>"

def extractSections(lecture):
  with open(os.path.join("..", "build", "lectures", lecture, f"{lecture}.html"), "r") as f:
    html_ = f.read()

  createDir(os.path.join("_includes", "lectures", lecture))
  createDir(os.path.join("pages", "lectures", lecture))

  lectureTitle = re.search(r"<p>\s*Vorlesungs(?:mitschrieb|notizen):\s*(.+?)\s*</p>", html_,
      flags=re.DOTALL).group(1)
  lectureTitle = re.sub(r"<br */>", " ", lectureTitle)
  lectureTitle = lectureTitle.replace("\n", " ")
  lectureTitle = re.sub(r"  +", " ", lectureTitle)
  lectureTitle = convertHtmlTitleToTextTitle(lectureTitle.strip())

  sidebarYaml = f"""
      - title: "{lectureTitle}"
        output: "web"
        folderitems:
""".lstrip("\r\n")

  mathJaxDefinitions = re.search(r"<div\s+class=\"hidden\"\s*>.*?</\s*div\s*>", html_,
      flags=re.DOTALL).group()
  matches = list(re.finditer(r"<p>\s*[0-9]+(?:&#x2002;|&#x2003;)(.+?)\n\s*", html_))

  for i in range(len(matches)):
    match = matches[i]
    title = convertHtmlTitleToTextTitle(match.group(1))
    slug = convertTextTitleToSlug(title)

    sectionEndPos = (matches[i+1].start() if i < len(matches) - 1 else
        re.search(r"-autofile-last\"></a>", html_).end())
    sectionHtml = html_[match.end():sectionEndPos]

    sectionHtml = re.sub(r"<p>\s*[0-9]+\.[0-9]+(?:&#x2002;|&#x2003;)+(.+?)\n\s*",
        replaceSubsectionHeading, sectionHtml)
    sectionHtml = re.sub(r"<p>\s*[0-9]+\.[0-9]+\.[0-9]+(?:&#x2002;|&#x2003;)+(.+?)\n\s*",
        replaceSubsubsectionHeading, sectionHtml)

    sectionHtml = sectionHtml.replace(f"{lecture}-images/",
        f"/class-notes/images/lectures/{lecture}/")

    #sectionHtml = re.sub(r"<br */>", " ", sectionHtml)

    listItemReplacer = ListItemReplacer()
    sectionHtml = re.sub(r"<li>\s*<p>\s*(<em>|<b>)?(\u2022|\u2013|\*|\(\S*?\)|\S*?\.|\S*?\))"
        r"(</em>|</b>)? ", listItemReplacer.replace, sectionHtml)

    if listItemReplacer.css != "":
      sectionHtml = f"<style type=\"text/css\">\n{listItemReplacer.css}</style>\n{sectionHtml}"

    sectionHtml = re.sub(r"<p>\s*(?:&#x2003;)+[\s\u0083]*\Z", "", sectionHtml)

    sectionHtml = f"""
{{::nomarkdown}}
<div class="lwarp-contents">
{{% raw %}}
{mathJaxDefinitions}

{sectionHtml}
{{% endraw %}}
</div>
{{:/nomarkdown}}
"""
    writeFile(os.path.join("_includes", "lectures", lecture, f"{slug}.html"), sectionHtml)

    sectionMarkdown = f"""
---
title: "{title}"
permalink: "/lectures/{lecture}/{slug}.html"
sidebar: "sidebar"
toc: false
---

{{% include lectures/{lecture}/{slug}.html %}}""".lstrip()
    writeFile(os.path.join("pages", "lectures", lecture, f"{slug}.md"), sectionMarkdown)

    sidebarYaml += f"""
          - title: "{title}"
            url: "/lectures/{lecture}/{slug}.html"
            output: "web"
""".lstrip("\r\n")

  return sidebarYaml



def main():
  os.chdir(os.path.join(os.path.dirname(__file__), ".."))

  copyFile(os.path.join("..", "LICENSE.md"), ".")
  copyFile(os.path.join("..", "README.md"), ".")

  deleteDir(os.path.join("_includes", "lectures"))
  createDir(os.path.join("_includes", "lectures"))
  deleteDir(os.path.join("pages", "lectures"))
  createDir(os.path.join("pages", "lectures"))

  lectures = os.listdir(os.path.join("..", "src", "lectures"))
  lectures = [x for x in lectures if os.path.isdir(os.path.join("..", "src", "lectures", x))]

  lectureOrder = [
      "analysis-1",
      "analysis-2",
      "analysis-3",
      "analysis-4",
      "functional-analysis-1",
      "functional-analysis-2",
      "linear-algebra-and-analytical-geometry-1",
      "linear-algebra-and-analytical-geometry-2",
      "algebra",
      "topology",
      "probability-theory",
      "mathematical-statistics",
      "linear-control-theory",
      "numerical-linear-algebra",
      "numerical-analysis-1",
      "numerical-analysis-2",
      "partial-differential-equations",
      "approximation-and-geometric-modeling",
      "finite-elements",
      "programming-and-software-engineering",
      "data-structures-and-algorithms",
      "formal-languages-and-automata",
      "computability-and-complexity",
      "algorithmic-geometry",
      "discrete-optimization",
      "cryptographic-procedures",
      "visual-computing",
      "modeling-and-simulation",
      "optical-phenomena",
      "basic-principles-of-geosciences",
      "history-of-wind-energy-use",
    ]
  lectures.sort(key=lambda x: ((lectureOrder.index(x), 0) if x in lectureOrder else
      (len(lectureOrder), x)))

  sidebarYaml = """
entries:
  - title: "sidebar"
    product: "Vorlesungsmitschriebe"
    version: ""
    folders:
      - title: "Über diese Mitschriebe"
        output: "web"
        folderitems:
          - title: "Startseite"
            url: "/index.html"
            type: "homepage"
            output: "web"
""".lstrip("\r\n")

  lectures = ["analysis-1"]

  for lecture in lectures:
    imagesDirPath = os.path.join("images", "lectures", lecture)
    deleteDir(imagesDirPath)
    imagesSrcDirPath = os.path.join("..", "build", "lectures", lecture, f"{lecture}-images")
    if len(os.listdir(imagesSrcDirPath)) > 0: copyDir(imagesSrcDirPath, imagesDirPath)

    sidebarYaml += extractSections(lecture)

  writeFile(os.path.join("_data", "sidebars", "sidebar.yml"), sidebarYaml)



if __name__ == "__main__":
  main()
