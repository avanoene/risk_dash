#!/bin/bash

pandoc gettingstarted.md links.md -H header.html -F mermaid-filter -t html -o gettingstarted.html

pandoc gettingstarted.md links.md -F mermaid-filter -o gettingstarted.pdf

pandoc gettingstarted.md links.md -s -F mermaid-filter -f markdown -t rst -o gettingstarted.rst

pandoc securities.md -s -F mermaid-filter -f markdown -t rst -o securities.rst

pandoc -F mermaid-filter -o securities.pdf securities.md

pandoc gettingstarted.md dashapp_documentation.md securities.md links.md -F mermaid-filter -o total_documentation.pdf
