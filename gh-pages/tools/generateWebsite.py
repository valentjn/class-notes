#!/usr/bin/python3

import html
import os
import functools
import re
import shutil

verbose = False



def copyFile(srcPath, destPath):
  if verbose: print(f"Copying '{srcPath}' to '{destPath}'...")
  shutil.copy(srcPath, destPath)

def deleteDir(dirPath):
  if os.path.isdir(dirPath):
    if verbose: print(f"Deleting '{dirPath}'...")
    shutil.rmtree(dirPath)

def createDir(dirPath):
  if verbose: print(f"Creating directory '{dirPath}'...")
  os.mkdir(dirPath)

def writeFile(filePath, s):
  if verbose: print(f"Writing file '{filePath}'...")
  with open(filePath, "w") as f: f.write(s)



def convertHtmlTitleToTextTitle(s):
  s = html.unescape(s)
  s = re.sub(r"<span class=\"textsc\"\s*>(.*?)</span>",
      r"<span style=\"font-variant: small-caps;\">\1</span>", s)
  s = re.sub(r"<em>(.*?)</em>", r"\1", s)
  s = re.sub(r"<kbd>(.*?)</kbd>", r"\1", s)
  s = s.replace("\\alpha", "\u03b1").replace("\\mu", "\u03bc").replace("\\xi", "\u03be")
  s = s.replace("\\rho", "\u03c1").replace("\\varrho", "\u03f1")
  s = s.replace("\\mathbb {C}", "\u2102").replace("\\mathbb {R}", "\u211d")
  s = s.replace("\\complex", "\u2102").replace("\\real", "\u211d")
  s = s.replace("^2", "\u00b2").replace("^n", "\u207f")
  s = s.replace("_0", "\u2080").replace("_2", "\u2082")
  s = s.replace("\\to", "\u2192").replace("\\infty ", "\u221e")
  s = s.replace("\\O (", "O(").replace("n\\log", "n log")
  s = s.replace(" ^\\ast", "*")
  s = re.sub(r"\\lim _\{(.*?)\}", r"\1", s)
  s = re.sub(r"\\\((.*?)\\\)", r"\1", s)
  s = re.sub(r" ([\)\-\^\}_\u2019\u207f\u2080])", r"\1", s)
  s = s.replace("\\", "")
  s = s.replace("M ATLAB", "MATLAB")
  s = s.replace("Wahrscheinlichkeitstheorie", "Wahrscheinlichkeits&shy;theorie")
  s = re.sub(r"  +", " ", s).strip()
  return s

def convertTextTitleToSlug(s):
  s = re.sub(r"<span style=\"font-variant: small-caps;\">(.*?)</span>", r"\1", s)
  s = s.lower()
  s = s.replace("\u00e4", "ae").replace("\u00f6", "oe").replace("\u00fc", "ue")
  s = re.sub("([aou])\u0308", r"\1e", s)
  s = s.replace("\u00df", "ss")
  s = s.replace("\u00e9", "e")
  s = s.replace("\u03b1", "alpha").replace("\u03bc", "mu").replace("\u03be", "xi")
  s = s.replace("\u03c1", "rho").replace("\u03f1", "rho")
  s = s.replace("\u2102", "c").replace("\u211d", "r")
  s = s.replace("\u00b2", "2").replace("\u207f", "n")
  s = s.replace("\u2080", "0").replace("\u2082", "2")
  s = s.replace("\u221e", "infty")
  s = s.replace(" ", "-")
  s = re.sub(r"[^a-z0-9\-]", "", s)
  s = re.sub(r"--+", "-", s)
  return s



class HeadingReplacer(object):
  def __init__(self, lecture, chapterSlug):
    self.lecture = lecture
    self.chapterSlug = chapterSlug
    self.tableOfContentsMarkdown = ""

  def replace(self, match):
    if match.group(1) is None:
      tag = "h2"
      indent = 2
    else:
      tag = "h3"
      indent = 4

    sectionHtmlTitle = match.group(2).strip()
    sectionTitle = convertHtmlTitleToTextTitle(sectionHtmlTitle)
    sectionSlug = convertTextTitleToSlug(sectionTitle)

    self.tableOfContentsMarkdown += (f"{indent * ' '}* [{sectionTitle}]("
        f"/class-notes/lectures/{self.lecture}/{self.chapterSlug}.html#{sectionSlug})\n")

    return f"<{tag} id=\"{sectionSlug}\">{sectionTitle}</{tag}>"



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

    for tag, fontStyle in [("em", "italic"), ("b", "bold")]:
      tagMatch = re.match(rf"^\(<{tag}>(.*?)</{tag}>\)$", marker)

      if (match.group(1) == f"<{tag}>") or (tagMatch is not None):
        self.css += f"  font-style:{fontStyle};\n"
        if tagMatch is not None: marker = f"({tagMatch.group(1)})"

    self.css += f"  content:'{marker}\\00a0\\00a0';\n}}\n"
    return f"<li class=\"{cssClass}\"><p>"



def processLecture(lecture):
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

  sidebarYaml = f"""
      - title: "{lectureTitle}"
        output: "web"
        folderitems:
          - title: "Inhaltsverzeichnis"
            url: "/lectures/{lecture}/index.html"
            output: "web"
""".lstrip("\r\n")

  indexMarkdown = f"""
    <tr>
      <td><a href="/class-notes/lectures/{lecture}/index.html">{lectureTitle}</a></td>
      <td>{lecturer}</td>
      <td>{semester}</td>
    </tr>
""".lstrip("\r\n")

  tableOfContentsMarkdown = f"\n## {lectureTitle}\n\n"
  lectureTableOfContentsMarkdown = f"""
---
title: "{lectureTitle} \u2013 Inhaltsverzeichnis"
permalink: "/lectures/{lecture}/index.html"
sidebar: "sidebar"
toc: false
---

""".lstrip("\r\n")

  html_ = html_.replace("\u00c3\u00a7", "\u00df")
  html_ = html_.replace("\u00c3\u010f", "\u00e4")
  html_ = html_.replace("\u00c3\u0171", "\u00f6")
  html_ = html_.replace("\u00c3\u0133", "\u00fc")
  html_ = html_.replace("&quot;|", "")
  html_ = html_.replace("&quot;\u2018", "\u201e")
  html_ = html_.replace("&quot;\u2019", "\u201c")

  html_ = re.sub(r"\\mathbbm\s*\{b\}", "\U0001d553", html_)
  html_ = re.sub(r"\\mathbbm\s*\{c\}", "\U0001d554", html_)
  html_ = re.sub(r"\\mathbbm\s*\{f\}", "\U0001d557", html_)
  html_ = re.sub(r"\\mathbbm\s*\{h\}", "\U0001d559", html_)
  html_ = re.sub(r"\\mathbbm\s*\{v\}", "\U0001d567", html_)
  html_ = re.sub(r"\\mathbbm\s*\{x([\u2019\u201d]?)\}", "\U0001d569\\1", html_)
  html_ = re.sub(r"\\mathbbm\s*\{y\}", "\U0001d56a", html_)
  html_ = re.sub(r"\\mathbbm\s*\{1\}", "\U0001d7d9", html_)

  html_ = re.sub(r"(Gau|Weierstra)(?:$|ss|([^\u00df]))", "\\1\u00df\\2", html_, flags=re.MULTILINE)

  # workaround for https://github.com/mathjax/MathJax/issues/2511
  html_ = re.sub(r"\\boldsymbol\s*\{", r"\\boldsymbol{", html_)

  mathJaxDefinitions = re.search(r"<div\s+class=\"hidden\"\s*>.*?</\s*div\s*>", html_,
      flags=re.DOTALL).group()
  mathJaxDefinitions = mathJaxDefinitions.replace(
      "\\(\\newcommand {\\pm }{\\pico \\metre }\)\n\n", "")

  matches = list(re.finditer(r"<p>\s*[0-9]+(?:&#x2002;|&#x2003;)(.+?)\n\s*", html_))

  for i in range(len(matches)):
    match = matches[i]
    chapterTitle = convertHtmlTitleToTextTitle(match.group(1))
    chapterSlug = convertTextTitleToSlug(chapterTitle)
    escapedChapterTitle = chapterTitle.replace("\"", "\\\"")

    chapterEndPos = (matches[i+1].start() if i < len(matches) - 1 else
        re.search(r"-autofile-last\"></a>", html_).end())
    chapterHtml = html_[match.end():chapterEndPos]

    headingReplacer = HeadingReplacer(lecture, chapterSlug)
    chapterHtml = re.sub(r"<p>\s*[0-9]+\.[0-9]+(\.[0-9]+)?(?:&#x2002;|&#x2003;)+(.+?)</?p>",
        headingReplacer.replace, chapterHtml, flags=re.DOTALL)
    chapterTableOfContentsMarkdownLine = (f"* **[{chapterTitle}]("
        f"/class-notes/lectures/{lecture}/{chapterSlug}.html)**\n")
    tableOfContentsMarkdown += (chapterTableOfContentsMarkdownLine +
        headingReplacer.tableOfContentsMarkdown)
    lectureTableOfContentsMarkdown += (chapterTableOfContentsMarkdownLine +
        headingReplacer.tableOfContentsMarkdown)

    chapterHtml = chapterHtml.replace(f"{lecture}-images/",
        f"/class-notes/images/lectures/{lecture}/")
    chapterHtml = re.sub(r"(src|href)=\"(.*?)\"",
        functools.partial(replaceImageUrl, lecture), chapterHtml)

    #chapterHtml = re.sub(r"<br */>", " ", chapterHtml)

    listItemReplacer = ListItemReplacer()
    chapterHtml = re.sub(r"<li>\s*<p>\s*(<em>|<b>)?"
        r"(\u2022|\u2013|\*|\(\S*?\)|\S*?\.|\S*?\)|\(<em>\S*?</em>\)|\(<b>\S*?</b>\))"
        r"(</em>|</b>)? ", listItemReplacer.replace, chapterHtml)

    if listItemReplacer.css != "":
      chapterHtml = f"<style type=\"text/css\">\n{listItemReplacer.css}</style>\n{chapterHtml}"

    chapterHtml = re.sub(r"<p>\s*(?:&#x2003;)+[\s\u0083]*\Z", "", chapterHtml)

    chapterHtml = f"""
{{::nomarkdown}}
<div class="lwarp-contents">
{{% raw %}}
{mathJaxDefinitions}

{chapterHtml}
{{% endraw %}}
</div>
{{:/nomarkdown}}
"""
    writeFile(os.path.join("_includes", "lectures", lecture, f"{chapterSlug}.html"), chapterHtml)

    texFileName = next(x for x in texFileNames if x.startswith(f"{i+1:02}_"))

    chapterMarkdown = f"""
---
title: "{lectureTitle} \u2013 {escapedChapterTitle}"
permalink: "/lectures/{lecture}/{chapterSlug}.html"
sidebar: "sidebar"
toc: true
tex_path: "src/lectures/{lecture}/{texFileName}"
---

{{% include lectures/{lecture}/{chapterSlug}.html %}}""".lstrip()
    writeFile(os.path.join("pages", "lectures", lecture, f"{chapterSlug}.md"), chapterMarkdown)

    sidebarYaml += f"""
          - title: "{escapedChapterTitle}"
            url: "/lectures/{lecture}/{chapterSlug}.html"
            output: "web"
""".lstrip("\r\n")

  writeFile(os.path.join("pages", "lectures", lecture, "index.md"), lectureTableOfContentsMarkdown)

  return sidebarYaml, indexMarkdown, tableOfContentsMarkdown



def main():
  os.chdir(os.path.join(os.path.dirname(__file__), ".."))

  deleteDir(os.path.join("_includes", "lectures"))
  createDir(os.path.join("_includes", "lectures"))
  deleteDir(os.path.join("images", "lectures"))
  createDir(os.path.join("images", "lectures"))
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
      - title: "\u00dcber diese Mitschriebe"
        output: "web"
        folderitems:
          - title: "Startseite"
            url: "/index.html"
            type: "homepage"
            output: "web"
          - title: "Komplettes Inhaltsverzeichnis"
            url: "/table-of-contents.html"
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

*Julian Valentin*

Diese Vorlesungsmitschriebe entstanden als H\u00f6rer in Vorlesungen an der Universit\u00e4t Stuttgart in den Jahren 2009 bis 2014. Sie dienten haupts\u00e4chlich als Lernhilfe f\u00fcr mich; aus Zeitgr\u00fcnden fehlen viele Skizzen und mathematische Beweise. Studentische Mitschriebe sind keine offiziellen Skripte; weder die Universit\u00e4t Stuttgart noch ihre Mitarbeiter sind f\u00fcr sie verantwortlich. Fehler k\u00f6nnen auf [GitHub](https://github.com/valentjn/class-notes) gemeldet werden. Die Mitschriebe stehen unter der [CC-BY-SA-4.0-Lizenz](https://creativecommons.org/licenses/by-sa/4.0/).

Die kompakt geschriebenen Vorlesungsmitschriebe ergeben mit ihren 31 Vorlesungen, 178 Kapiteln, mehr als 1100 PDF-Seiten und \u00fcber 500.000 W\u00f6rtern (meistens Formeln) eine kleine Bibliothek, die viele verschiedene Themen aus Mathematik und Informatik abdeckt. Die Vorlesungsmitschriebe stehen zur Verf\u00fcgung

* [als LaTeX-Code](https://github.com/valentjn/class-notes),
* [als einzelne PDFs f\u00fcr jede Vorlesung](https://github.com/valentjn/class-notes/releases),
* [als Sammlungs-PDF](https://github.com/valentjn/class-notes/releases) (das alle Vorlesungen in eine einzige handliche 9-MB-PDF-Datei zusammenfasst) und
* als HTML-Version.

Die vorliegende HTML-Version wurde mithilfe des `lwarp`-Pakets halbautomatisiert aus der LaTeX-Originalversion erzeugt.

Folgende Mitschriebe stehen zur Verf\u00fcgung:

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

  tableOfContentsMarkdown = """
---
title: "Komplettes Inhaltsverzeichnis"
permalink: "/table-of-contents.html"
sidebar: "sidebar"
toc: false
---
""".lstrip("\r\n")

  prevField = None

  for lecture in lectures:
    print(f"Processing '{lecture}'...")

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

    curSidebarYaml, curIndexMarkdown, curTableOfContentsMarkdown = processLecture(lecture)
    sidebarYaml += curSidebarYaml
    indexMarkdown += curIndexMarkdown
    tableOfContentsMarkdown += curTableOfContentsMarkdown

    prevField = field

    if len(os.listdir(imagesDirPath)) == 0: deleteDir(imagesDirPath)

  indexMarkdown += """
  </tbody>
</table>
""".lstrip("\r\n")

  writeFile(os.path.join("_data", "sidebars", "sidebar.yml"), sidebarYaml)
  writeFile(os.path.join("pages", "index.md"), indexMarkdown)
  writeFile(os.path.join("pages", "table-of-contents.md"), tableOfContentsMarkdown)



if __name__ == "__main__":
  main()
