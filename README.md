# nxml2fries

 Converts PubMed NXML format into (almost) raw text to be used for NL analysis.

## Requirements

 This software assumes a unix-like environment and that you have a working installation of [nxml2txt](https://github.com/spyysalo/nxml2txt) added to your path. Besided that you only need [Python](https://www.python.org).

## Usage

 ```Shell
 ./nxml2fries [--no-citations] arg1.nxml [... argn.nxml]
 ```

* **--no-citation**: If enabled, this option removes the reference citations from the text and replaces the space they used by white-spaces characters.

* __argn.nxml__: The nxml file or list of files to operate over.

## Output format

Each output file is in _tab-separated-values_ format. Its fields are:

* **Paragraph ID**: A unique id in the document assigned to the corrent paragraph
* **Section ID**: The id of the section in the paper.*
* **Normalized section name**: A normalized version of the section to create equivalence classes of sections between papers. For example, _Materials/Methods_ and _Materials and methods_ would have the same normalized name _materials-methods_.*
* **Is title**: Wether the text in the line is the title of a section/paper/figure. __1__ for true and __0__ for false.
* **Text**: The text of the current paragraph/figure/reference.

_* If this field has no information, it's content will be **N/A**._

## Examples

| ID | sec_id | sec_norm | Is title | Text |
| --- | --- | --- | --- | --- |
| 52 | s2f | N/A | 1 | Biochemical analyses |

The title for section _s2f_.


| ID | sec_id | sec_norm | Is title | Text |
| --- | --- | --- | --- | --- |
59 | s2g | materials-methods | 0 | To measure the effect of Ras on PI3KC2beta ... |

A paragraph of _section-id s2g_, with a normalized section.

| ID | sec_id | sec_norm | Is title | Text |
| --- | --- | --- | --- | --- |
96 | references | references | 0 | 1 Karnoub AE , Weinberg RA ( 2008 )  Ras oncogenes: split personalities . Nat Rev Mol Cell Biol 9 : 517 - 531 18568040 |

One of the references of a paper

| ID | sec_id | sec_norm | Is title | Text |
| --- | --- | --- | --- | --- |
| 25 | fig-4 | fig-4 | 1 | ITSN1 and Ras form a BiFC complex. |

A figure's title
