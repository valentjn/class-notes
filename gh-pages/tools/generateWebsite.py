#!/usr/bin/python3

import html
import os
import functools
import re
import shutil

def copyFile(srcPath, destPath):
  print(f"Copying '{srcPath}' to '{destPath}'...")
  shutil.copy(srcPath, destPath)

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

def replaceImageUrl(lecture, match):
  attributeName, fileName = match.group(1), match.group(2)

  if fileName.startswith("/class-notes/images") or fileName.endswith(".html"):
    return match.group(0)
  else:
    if attributeName == "src":
      copyFile(os.path.join("..", "build", "lectures", lecture, fileName),
          os.path.join("images", "lectures", lecture))

    return f"{attributeName}=\"/class-notes/images/lectures/{lecture}/{fileName}\""

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

  lectureDirPath = os.path.join("..", "src", "lectures", lecture)
  texFileNames = os.listdir(lectureDirPath)

  with open(os.path.join(lectureDirPath, "metadata.tex")) as f: metadataTex = f.read()

  lectureTitle = re.search(r"\{\\vorlesung\}\{(.*)\}", metadataTex).group(1)
  lectureTitle = lectureTitle.replace("\"-", "").replace("\"|", "")

  match = re.search(r"\{\\dozent\}\{(.*)\\name\{(.*)\}\}", metadataTex)
  lecturerDegree, lecturer = match.group(1), match.group(2)
  if "Jun.-Prof." in lecturerDegree:   lecturer = f"JP&nbsp;{lecturer}"
  elif "Prof." in lecturerDegree:      lecturer = f"Prof.&nbsp;{lecturer}"
  elif "Dr." in lecturerDegree:        lecturer = f"Dr.&nbsp;{lecturer}"
  elif "Dipl.-Ing." in lecturerDegree: lecturer = f"Dipl.-Ing.&nbsp;{lecturer}"

  semester = re.search(r"\{\\semester\}\{(.*)\}", metadataTex).group(1)
  semester = semester.replace("Wintersemester", "WiSe").replace("Sommersemester", "SoSe")

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
    sectionHtml = re.sub(r"(src|href)=\"(.*?)\"",
        functools.partial(replaceImageUrl, lecture), sectionHtml)

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

    texFileName = next(x for x in texFileNames if x.startswith(f"{i+1:02}_"))

    sectionMarkdown = f"""
---
title: "{lectureTitle} \u2013 {title}"
permalink: "/lectures/{lecture}/{slug}.html"
sidebar: "sidebar"
toc: false
tex_path: "src/lectures/{lecture}/{texFileName}"
---

{{% include lectures/{lecture}/{slug}.html %}}""".lstrip()
    writeFile(os.path.join("pages", "lectures", lecture, f"{slug}.md"), sectionMarkdown)

    sidebarYaml += f"""
          - title: "{title}"
            url: "/lectures/{lecture}/{slug}.html"
            output: "web"
""".lstrip("\r\n")

    if i == 0:
      indexMarkdown = f"""
    <tr>
      <td><a href="/class-notes/lectures/{lecture}/{slug}.html">{lectureTitle}</a></td>
      <td>{lecturer}</td>
      <td>{semester}</td>
    </tr>
""".lstrip("\r\n")

  return sidebarYaml, indexMarkdown



def main():
  os.chdir(os.path.join(os.path.dirname(__file__), ".."))

  copyFile(os.path.join("..", "LICENSE.md"), ".")
  copyFile(os.path.join("..", "README.md"), ".")

  deleteDir(os.path.join("_includes", "lectures"))
  createDir(os.path.join("_includes", "lectures"))
  deleteDir(os.path.join("pages", "lectures"))
  createDir(os.path.join("pages", "lectures"))

  lecturesDirPath = os.path.join("..", "src", "lectures")
  lectures = os.listdir(lecturesDirPath)
  lectures = [x for x in lectures if os.path.isdir(os.path.join(lecturesDirPath, x))]

  fields = [
        {
          "title" : "Analysis",
          "lectures" : [
              "analysis-1",
              "analysis-2",
              "analysis-3",
              "analysis-4",
              "functional-analysis-1",
              "functional-analysis-2",
          ],
        },
        {
          "title" : "Algebra",
          "lectures" : [
            "linear-algebra-and-analytical-geometry-1",
            "linear-algebra-and-analytical-geometry-2",
            "algebra",
          ],
        },
        {
          "title" : "Topologie",
            "lectures" : [
            "topology",
          ],
        },
        {
          "title" : "Angewandte Mathematik",
          "lectures" : [
            "probability-theory",
            "mathematical-statistics",
            "linear-control-theory",
          ],
        },
        {
          "title" : "Numerik",
          "lectures" : [
            "numerical-linear-algebra",
            "numerical-analysis-1",
            "numerical-analysis-2",
            "partial-differential-equations",
            "approximation-and-geometric-modeling",
            "finite-elements",
          ],
        },
        {
          "title" : "Informatik",
          "lectures" : [
            "programming-and-software-engineering",
            "data-structures-and-algorithms",
            "formal-languages-and-automata",
            "computability-and-complexity",
            "algorithmic-geometry",
            "discrete-optimization",
            "cryptographic-procedures",
            "visual-computing",
            "modeling-and-simulation",
          ],
        },
        {
          "title" : "Verschiedene andere Gebiete",
          "lectures" : [
            "optical-phenomena",
            "basic-principles-of-geosciences",
            "history-of-wind-energy-use",
          ],
        },
      ]
  lectureOrder = [y for x in fields for y in x["lectures"]]
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

  indexMarkdown = """
---
title: "Vorlesungsmitschriebe"
permalink: "/index.html"
sidebar: "sidebar"
toc: false
---

Diese Vorlesungsmitschriebe entstanden als Hörer in Vorlesungen an der Universität Stuttgart in den Jahren 2009 bis 2014. Sie dienten hauptsächlich als Lernhilfe für mich; aus Zeitgründen fehlen viele Skizzen und mathematische Beweise. Studentische Mitschriebe sind keine offiziellen Skripte; weder die Universität Stuttgart noch ihre Mitarbeiter sind für sie verantwortlich. Fehler können auf [GitHub](https://github.com/valentjn/class-notes) gemeldet werden. Die LaTeX-Umsetzung der Mitschriebe steht unter [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

Folgende Mitschriebe stehen zur Verfügung:

<table>
  <thead>
    <tr>
      <th>Vorlesung</th>
      <th>Dozent</th>
      <th>Semester</th>
    </tr>
  </thead>
  <tbody>
""".lstrip("\r\n")

  prevField = None

  for lecture in lectures:
    imagesDirPath = os.path.join("images", "lectures", lecture)
    deleteDir(imagesDirPath)
    createDir(imagesDirPath)

    imagesSrcDirPath = os.path.join("..", "build", "lectures", lecture, f"{lecture}-images")

    for fileName in os.listdir(imagesSrcDirPath):
      copyFile(os.path.join(imagesSrcDirPath, fileName), imagesDirPath)

    possibleFields = [x["title"] for x in fields if lecture in x["lectures"]]
    field = (possibleFields[0] if len(possibleFields) > 0 else prevField)

    if field != prevField:
      indexMarkdown += f"""
    <tr>
      <td colspan="3"><b>{field}</b></td>
    </tr>
""".lstrip("\r\n")

    curSidebarYaml, curIndexMarkdown = extractSections(lecture)
    sidebarYaml += curSidebarYaml
    indexMarkdown += curIndexMarkdown

    prevField = field

    if len(os.listdir(imagesDirPath)) == 0: deleteDir(imagesDirPath)

  indexMarkdown += """
  </tbody>
</table>
""".lstrip("\r\n")

  writeFile(os.path.join("_data", "sidebars", "sidebar.yml"), sidebarYaml)
  writeFile(os.path.join("pages", "index.md"), indexMarkdown)



if __name__ == "__main__":
  main()
