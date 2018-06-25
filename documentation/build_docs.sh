#!/bin/bash

pandoc gettingstarted.md links.md -H header.html -F mermaid-filter -t html -o gettingstarted.html

pandoc gettingstarted.md links.md -F mermaid-filter -o gettingstarted.pdf

pandoc gettingstarted.md links.md -s -F mermaid-filter -f markdown -t rst -o gettingstarted.rst

ex -sc '1i|.. _gettingstarted:' -cx gettingstarted.rst
ex -sc '2i| ' -cx gettingstarted.rst

sed -i.bu 's/    Note:/.. note::/g' gettingstarted.rst

pandoc gettingstarted.md dashapp_documentation.md links.md -F mermaid-filter -o total_documentation.pdf

make html

make latex

cd _build/latex && pdflatex risk_dash.tex
