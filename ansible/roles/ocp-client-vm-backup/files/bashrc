# .bashrc

# User specific aliases and functions

alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias ls='ls -F'
alias ll='ls -lF'
alias la='ls -aF'

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

# Set up Bash Git Prompt
if [ -f "$HOME/.bash-git-prompt/gitprompt.sh" ]; then
   GIT_PROMPT_THEME=Evermeet
   GIT_PROMPT_SHOW_CHANGED_FILES_COUNT=1
   GIT_PROMPT_ONLY_IN_REPO=0
   source "$HOME/.bash-git-prompt/gitprompt.sh"
fi
