#!/bin/bash

tmux new-session -d -s pingtests -n baidu
tmux send-keys -t '=pingtests:=baidu' 'ping 180.76.76.76' Enter
tmux split-window -v -l 75% -t '=pingtests:=baidu' 'ping 192.168.1.1'
tmux split-window -v -l 66% -t '=pingtests:=baidu' 'ping 192.168.50.1'
tmux split-window -v -l 50% -t '=pingtests:=baidu' 'ping 192.168.50.20'
tmux attach-session -t pingtests
#tmux kill-session -t pingtests
