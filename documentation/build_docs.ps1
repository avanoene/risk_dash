
pandoc gettingstarted.md ./links.md -H ./header.html -F mermaid-filter.cmd -t html -o gettingstarted.html

pandoc gettingstarted.md ./links.md -F mermaid-filter.cmd -o gettingstarted.pdf

pandoc gettingstarted.md ./links.md -s -F mermaid-filter.cmd -f markdown -t rst -o gettingstarted.rst

pandoc ../LICENSE.md  -f markdown -t rst -o license.rst

pandoc ../README.md  -f markdown -t rst -o readme.rst

pandoc dashapp_documentation.md -f markdown -t rst -o dashapp_documentation.rst

@('.. _gettingstarted:', ' ') + (Get-Content ./gettingstarted.rst) | Set-Content ./gettingstarted.rst
(Get-Content ./gettingstarted.rst) -replace '    Note:', '.. note::' | Set-Content ./gettingstarted.rst

@('.. _dashapp_documentation:', ' ') + (Get-Content ./dashapp_documentation.rst) | Set-Content ./dashapp_documentation.rst
(Get-Content ./dashapp_documentation.rst) -replace '    Note:', '.. note::' | Set-Content ./dashapp_documentation.rst

@('.. _license:', ' ', 'Software License', '======================================') + (Get-Content ./license.rst) | Set-Content ./license.rst


sphinx-build -b latex ./ ./_build/latex
sphinx-build -b html ./ ./_build/html

./_build/html/make.bat
./_build/latex/make.bat