#!/bin/sh

# add upstream if not exists
git remote -v
#git remote add upstream git@github.com:redhat-cop/agnosticd.git

# sync local repo with agnosticd 'development' (the agnosticd HEAD)
git checkout development
git fetch upstream
git merge upstream/development

# push changes from agnosticd HEAD into my fork
git push

# sync my local branch with updates from upstream agnosticd HEAD
git checkout mercury-setup
git fetch -p origin
git merge origin/mercury-setup
git push