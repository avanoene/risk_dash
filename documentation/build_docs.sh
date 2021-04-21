#!/bin/bash

pandoc gettingstarted.md ./documentation/links.md -H ./documentation/header.html -F mermaid-filter -t html -o gettingstarted.html

pandoc gettingstarted.md ./documentation/links.md -F mermaid-filter -o gettingstarted.pdf

pandoc gettingstarted.md ./documentation/links.md -s -F mermaid-filter -f markdown -t rst -o gettingstarted.rst

ex -sc '1i|.. _gettingstarted:' -cx ./documentation/gettingstarted.rst
ex -sc '2i| ' -cx ./documentation/gettingstarted.rst

sed -i.bu 's/    Note:/.. note::/g' ./documentation/gettingstarted.rst

pandoc gettingstarted.md ./documentation/dashapp_documentation.md ./documentation/links.md -F mermaid-filter -o total_documentation.pdf

make html

make latex

cd ./documentation/_build/latex && pdflatex risk_dash.tex
