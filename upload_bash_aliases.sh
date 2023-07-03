#!/bin/bash

cp -p ~/.bash_aliases "$(dirname "$0")"
cd "$(dirname "$0")"
git add .
git commit -m "Updated bash_aliases"
git pull --rebase
git push
