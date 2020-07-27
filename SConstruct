import functools
import os

# class with helper methods
class Helper(object):
  # check if a dependency is installed, fail if not (if desired)
  @staticmethod
  def checkProgramInstalled(env, program, fail=False):
    if (not env.GetOption("help")) and (not env.GetOption("clean")):
      conf = Configure(env, log_file=None)

      if (conf.CheckProg(program) is None) and fail:
        message = "Program \"{}\" required, but not found in PATH.".format(program)
        if env["REQUIRE_PROGRAMS"]: raise RuntimeError(message)
        else: warnings.warn(message)

      conf.Finish()
      return False
    else:
      return True

  @staticmethod
  def translateSrcToBuild(path):
    if isinstance(path, (list, tuple)):
      return [Helper.translateSrcToBuild(x) for x in path]
    else:
      newPath = path.abspath.replace("/src", "/build")
      return (Dir(newPath) if path.isdir() else File(newPath))

  @staticmethod
  def buildCollectionIncludeTex(dirNames, target, source, env):
    dirNames = sorted(x for x in dirNames if x != "collection")
    collectionIncludeTex = ""

    for dirName in dirNames:
      dirPath = f"../lectures/{dirName}/"
      collectionIncludeTex += f"""
{{%
  \subimport{{{dirPath}}}{{metadata}}%
  \input{{part}}%
  \subimport{{{dirPath}}}{{include}}%
}}
"""

    for x in target:
      with open(x.abspath, "w") as f: f.write(collectionIncludeTex)

# check SCons version
EnsureSConsVersion(3, 0)

# build flags
variables = Variables(None, ARGUMENTS)

# set up environment, export environment variables of the shell
# (for example needed for custom TeX installations which need PATH)
env = Environment(variables=variables, ENV=os.environ)

# display help about build flags when called with -h
Help(variables.GenerateHelpText(env))

# use timestamp to decide if a file should be rebuilt
# (otherwise SCons won't rebuild even if it is necessary)
env.Decider("timestamp-newer")

# increase line length of LuaLaTeX error log lines by
# setting environment variables
env["ENV"]["max_print_line"] = "10000"
env["ENV"]["error_line"] = "254"
env["ENV"]["half_error_line"] = "238"

# use LuaLaTeX as compiler (successor of pdfLaTeX)
Helper.checkProgramInstalled(env, "lualatex", fail=True)
# filter the output of LuaLaTeX with custom script
luaLatex = "python3 {} lualatex".format(File("#/tools/filterOutput.py").abspath)
env.Replace(PDFTEX=luaLatex, PDFLATEX=luaLatex)

# show file and line number for errors
env.Append(PDFLATEXFLAGS="--file-line-error")
# enable SyncTeX for GUI editors
env.Append(PDFLATEXFLAGS="--synctex=1")
# enable shell commands to display Git version
env.Append(PDFLATEXFLAGS="--shell-escape")
# set output directory
#env.Append(PDFLATEXFLAGS="--output-directory={}".format(buildDirPath))

# compile in build directory
for rootDirName, dirNames, fileNames in os.walk("src", followlinks=True):
  dirNames.sort()

  for fileName in sorted(fileNames):
    file_ = File(os.path.join(rootDirName, fileName))
    env.InstallAs(target=Helper.translateSrcToBuild(file_), source=file_)

# list of targets (collection must be at the end)
dirNames = ([x.name for x in Glob("src/lectures/*") if x.isdir()] + ["collection"])
pdfs = []

for dirName in dirNames:
  dirType = ("lectures" if dirName != "collection" else "collection")
  dirPath = (f"lectures/{dirName}" if dirType != "collection" else "collection")
  dependencies = Helper.translateSrcToBuild(Glob(f"src/{dirPath}/*"))
  env.InstallAs(target=f"build/{dirPath}/{dirName}.tex", source="build/common/preamble.tex")

  if dirType == "lectures":
    dependencies.extend(env.Install(target=f"build/{dirPath}",
        source=f"build/{dirType}/document.tex"))
  else:
    dependencies.extend(env.Command(
        target=f"build/{dirPath}/collectionInclude.tex", source="",
        action=functools.partial(Helper.buildCollectionIncludeTex, dirNames)))
    dependencies.extend(Helper.translateSrcToBuild(Glob("src/lectures/*/*")))

  pdf = env.PDF(target=f"build/{dirPath}/{dirName}.pdf",
      source=f"build/{dirPath}/{dirName}.tex")
  env.Depends(target=pdf, dependency=dependencies)
  env.Alias(dirName, pdf)
  pdfs.append(pdfs)
