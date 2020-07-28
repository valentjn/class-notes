# L<sup>A</sup>T<sub>E</sub>X Class Notes (German)

[comment]: <> "LTeX: language=en-US"

*Julian Valentin*

This repository contains L<sup>A</sup>T<sub>E</sub>X class notes in German taken during lectures at the University of Stuttgart, Germany, in the years of 2009 to 2014. Their main purpose was helping me studying and preparing for exams. Due to time constraints, most of the drawings and mathematical proofs are missing. However, these class notes are provided here in the hope that somebody might benefit from them. Mistakes can be reported at the [GitHub repo](https://github.com/valentjn/class-notes). The L<sup>A</sup>T<sub>E</sub>X realization of the notes is licensed under the [CC BY-SA 4.0 license](https://creativecommons.org/licenses/by-sa/4.0/).

The class notes consist of 31 lectures, 178 chapters, and over 1100 pages, treating various areas of mathematics and computer science. In case an English translation of a paragraph is needed, [DeepL](https://www.deepl.com/translator) seems to produce somewhat suitable translations.

A “collection” PDF that combines all lectures into a single handy 9 MB PDF file is available as well.

## Lectures

- Analysis
  - Analysis 1
  - Analysis 2
  - Analysis 3
  - Analysis 4
  - Functional Analysis 1 *(Funktionalanalysis 1)*
  - Functional Analysis 2 *(Funktionalanalysis 2)*
- Algebra
  - Linear Algebra and Analytical Geometry 1 *(Lineare Algebra und Analytische Geometrie 1)*
  - Linear Algebra and Analytical Geometry 2 *(Lineare Algebra und Analytische Geometrie 2)*
  - Algebra
- Topology
  - Topology *(Topologie)*
- Applied mathematics
  - Probability Theory *(Wahrscheinlichkeitstheorie)*
  - Mathematical Statistics *(Mathematische Statistik)*
  - Linear Control Theory *(Lineare Kontrolltheorie)*
- Numerical analysis
  - Numerical Linear Algebra *(Numerische Lineare Algebra)*
  - Numerical Mathematics 1 *(Numerische Mathematik 1)*
  - Numerical Mathematics 2 *(Numerische Mathematik 2)*
  - Partial Differential Equations *(Partielle Differentialgleichungen)*
  - Approximation and Geometric Modeling *(Approximation und geometrische Modellierung)*
  - Finite Elements *(Finite Elemente)*
- Computer science
  - Programming and Software Engineering *(Programmierung und Software-Entwicklung)*
  - Data Structures and Algorithms *(Datenstrukturen und Algorithmen)*
  - Formal Languages and Automata *(Formale Sprachen und Automatentheorie)*
  - Computability and Complexity *(Berechenbarkeit und Komplexität)*
  - Algorithmic Geometry *(Algorithmische Geometrie)*
  - Discrete Optimization *(Diskrete Optimierung)*
  - Cryptographic Procedures *(Kryptografische Verfahren)*
  - Theoretical and Methodological Foundations of Visual Computing *(Theoretische und methodische Grundlagen des Visual Computing)*
  - Modeling and Simulation *(Modellbildung und Simulation)*
- Miscellaneous areas
  - Optical Phenomena in Nature and Everyday Life *(Optische Phänomene in Natur und Alltag)*
  - Basic Principles of Geosciences *(Geowissenschaftliche Grundlagen der Planetenforschung)*
  - History of Wind Energy Use *(Geschichte der Windenergie-Nutzung)*

## How to Build

To build the PDFs yourself, the following is required:

- Recent version of L<sup>A</sup>T<sub>E</sub>X (KOMA-Script version at least v3.31). The provided PDFs were built with [TeX Live 2020](https://www.tug.org/texlive/).
- [Python 3](https://www.python.org/)
- [SCons](https://scons.org/)

Execute `scons` to build all lectures and the collection. Use `-j 4` to run four jobs simultaneously. Supply a space-separated list of lecture names (may include `collection`) to build specific PDFs. The PDFs will be stored in `build/lectures/LECTURENAME` and `build/collection`, respectively.

### Possible Problems

- Make sure that your system runs SCons with Python 3, otherwise running `scons` will fail (e.g., Ubuntu). On Linux, you can try running `/usr/bin/env python3 $(which scons)` instead.
- For other potential build problems, a look at `.travis.yml` might help.
