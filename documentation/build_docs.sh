#!/bin/bash

pandoc -H header.html -F mermaid-filter -t html -o Documentation.html Documentation.md
