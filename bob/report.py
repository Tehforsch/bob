import os
import subprocess
from pathlib import Path

from bob.util import walkfiles

latexHead = r"""
\documentclass[19.5pt]{beamer}
\setbeamertemplate{frametitle}[default][center]
\usepackage{graphicx}
\begin{document}
\section{Report}
"""
latexTail = r"\end{document}"

latexPerFileTemplate = r"""
\begin{{frame}}
  \centering
  \frametitle{{{title}}}
      {name}
    \begin{{figure}}
    \includegraphics[width=0.7\textwidth]{{{filename}}}
    \end{{figure}}
\end{{frame}}
"""


def getLatexContentForFile(filename: Path) -> str:
    title = filename.parent.name
    name = filename.name.replace(".png", "").replace("_", "\_")
    if name == title:
        name = ""
    return latexPerFileTemplate.format(filename=filename, name=name, title=title)


def getLatexFileContents(files: list[Path]) -> str:
    return latexHead + "\n".join(getLatexContentForFile(filename) for filename in files) + latexTail


def parseLatexFile(latexFilePath: Path) -> None:
    os.chdir(latexFilePath.parent)
    print(latexFilePath.parent)
    args = ["pdflatex", "--interaction=nonstopmode", latexFilePath.name]
    subprocess.check_call(args)


def createLatexFile(reportFolder: Path, files: list[Path]) -> Path:
    latexFilePath = reportFolder / "main.tex"
    with open(latexFilePath, "w") as f:
        f.write(getLatexFileContents(files))
    return latexFilePath


def createReport(path: Path) -> None:
    reportFolder = path.parent / "report"
    reportFolder.mkdir(exist_ok=True)
    files = [Path("..") / f for f in walkfiles(path) if f.suffix == ".png"]
    files.sort()
    latexFile = createLatexFile(reportFolder, files)
    parseLatexFile(latexFile)
