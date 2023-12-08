#!/bin/bash

cp -p ~/.bash_aliases "$(dirname "$0")"
cp -p ~/.vimrc "$(dirname "$0")"
cp -p ~/.config/htop/htoprc "$(dirname "$0")"
cp -p ~/.tmux.conf "$(dirname "$0")"

cd "$(dirname "$0")"
git add .
git commit -m "Updated bash_aliases"
git pull --rebase
git push
