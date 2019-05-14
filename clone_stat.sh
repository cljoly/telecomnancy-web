#!/usr/bin/env bash

LOCKFILE=lock
REPOURL=$1
REPONAME=$(echo $REPOURL | sed -e 's/.*\/\(.*\)$/\1/')
TOKEN=$2
SSHKEY=$3
JSON_RESULT=../stat.json

GIT_SSH_COMMAND="ssh -i ./$SSHKEY -F /dev/null" git clone "$REPOURL" $REPONAME

if [ $? -ne 0 ]; then
  exit 2
fi
echo "Dépot cloné"

cd $REPONAME

gitinspector --format=json -HlmrTw >$JSON_RESULT

cd - || exit 3
