type emulate >/dev/null 2>/dev/null || alias emulate=true

if [ -f ~/.bash_aliases_local ]; then
    . ~/.bash_aliases_local
fi

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# colored GCC warnings and errors
#export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# some more ls aliases
alias ll='ls -alFh'
alias la='ls -A'
alias l='ls -CF'

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# user-defined
alias grepp='grep -P'
alias dff=$'df -BG | grepp -v "snap|run|sys|udev|tmpfs|efi" | awk \'{print $6,"\t",$4,"\t/",$2}\''
alias ddu='dutree -d1'
alias lss='ls -alh'
alias lls='lss'
alias cp='cp -p'
alias cdo='cd $OLDPWD'

alias tail1='tail -n 1'

cdd() {
        local dir="$1"
        local dir="${dir:=$HOME}"
        if [[ -d "$dir" ]]; then
                cd "$dir" >/dev/null; ls --color=auto
        else
                echo "bash: cdls: $dir: Directory not found"
        fi
}

pyclean () {
    find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
}

duu() {
    emulate -L ksh
    if [ $# == 0 ]; then
        du . -h --max-depth=0 | sort -h
    else
        du . -h --max-depth=$1 | sort -h
    fi
}

tmuxa() {
    emulate -L ksh
    if [ $# == 0 ]; then
        tmux a
    else
        tmux attach-session -t $1
    fi
}

tmuxn() {
tmux new-session -s $1
}

compress() {
    emulate -L ksh
    src="$1"
    dst="$2"
    if [ $# == 2 ]; then
        tar c --totals --checkpoint-action=echo="#%u: %Т %t" --checkpoint=100000 $src | pigz -6 > $dst
    else
        nthread="$3"
        tar c --totals --checkpoint-action=echo="#%u: %Т %t" --checkpoint=100000 $src | pigz -6 -p $nthread > $dst
    fi
}

alias ipy='ipython'
alias ipython='ipython3'
alias python='python3'
alias rsync='rsync -a --progress'
alias git-reignore="git rm -rf --cached . && git add ."
alias viba='vi ~/.bashrc'
alias vibashrc='vi ~/.bashrc'
alias viali='vi ~/.bash_aliases'
alias path='readlink -f'
alias petarclean='rm data* dump* check* input* *.log log.* hard* spec_* bev.* sev.* *.lst *.mp4 fort.* *.npy stellar_*; for dir in {0..14}; do rm -rf $dir; done'
alias petarwc='wc -l data.* | sort -t . -k 2n | less'