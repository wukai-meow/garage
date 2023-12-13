#!/bin/bash

my_dir="$(dirname "$0")"
echo $my_dir

cp -p ~/.bash_aliases $my_dir/

rsync -av --progress --files-from=<( printf ".bash_aliases\n.vimrc\n.tmux.conf\n.config/htop/htoprc\n" ) ~/ $my_dir/linux_config/

cd $my_dir
git add .
git commit -m "Updated bash_aliases"
git pull --rebase
git push
