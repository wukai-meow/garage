type emulate >/dev/null 2>/dev/null || alias emulate=true
# sync: 
# add to bashrc: 
# (ping -c 1 bing.com &> /dev/null && wget https://raw.githubusercontent.com/wukai-meow/garage/main/.bash_aliases -O ~/.bash_aliases &> /dev/null &) 
# (ping -c 1 silk3 &> /dev/null && rsync silk3:~/.bash_aliases ~/ &> /dev/null &) 

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
alias ring='tput bel'

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
#alias tmuxa='tmux attach-session -t'
alias tmuxn='tmux new-session -s'

compress() {
    emulate -L ksh
    if [ $# == 1 ]; then
    src="$1"
        tar c --totals --checkpoint-action=echo="#%u: %Т %t" --checkpoint=100000 $src | pigz -6 > "$src".tgz
    elif [ $# == 2 ]; then
        src="$1"
        dst="$2"
        tar c --totals --checkpoint-action=echo="#%u: %Т %t" --checkpoint=100000 $src | pigz -6 > $dst
    elif [ $# == 3 ]; then
        nsrc="$1"
        dst="$2"
        thread="$3"
        tar c --totals --checkpoint-action=echo="#%u: %Т %t" --checkpoint=100000 $src | pigz -6 -p $nthread > $dst
    else
        echo "Usage: compress src dst nthread (dst defaults to src.tar.gz ; nthread defaults to max)"
    fi
}

extracttgz() {
    emulate -L ksh
    pigz -dc "$1" | tar xf -
}

s() {
  emulate -L ksh
  sgpt '"'"$*"'"'
}
ss() {
  emulate -L ksh
  sgpt -s '"'"$*"'"'
}
path() {
  emulate -L ksh
  [ -e "$1" ] && readlink -f "$1"
}


alias ipy='ipython3'
alias ipython='ipython3'
alias python='python3'
alias rsync='rsync -a --progress'
alias git-reignore="git rm -rf --cached . && git add ."
alias viba='vi ~/.bashrc'
alias vibashrc='vi ~/.bashrc'
alias viali='vi ~/.bash_aliases'
alias petarclean='rm data* dump* check* input* *.log log.* hard* spec_* bev.* sev.* *.lst *.mp4 fort.* *.npy stellar_*; for dir in {0..14}; do rm -rf $dir; done'
alias petarwc='wc -l data.* | sort -t . -k 2n | less'
alias ':q'=exit
alias petarls="ls | egrep '^data.[0-9]+$' | sort -n -k 1.6"
alias galevclean='rm spec_out*; rm stellar_magnitude*; rm log_GalevNB*; rm fort.13'
alias git_update='git fetch --all && git reset --hard origin/dev '
