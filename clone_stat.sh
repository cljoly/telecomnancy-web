#!/usr/bin/env bash

LOCKFILE=lock
SSHKEY=tmp.key
REPOURL=$1
TOKEN=$2

ssh-keygen -y -t rsa -N "" -f $SSHKEY

if [ $? -ne 0 ]; then
  rm $LOCKFILE
  exit 1
fi
echo "Clé SSH genérée"

curl --data-urlencode "key=$(cat $SSHKEY)" --data-urlencode "title=Gitly" \
  "https://gitlab.telecomnancy.univ-lorraine.fr/api/v3/user/keys?private_token=$TOKEN"

if [ $? -ne 0 ]; then
  rm $LOCKFILE
  exit 1
fi
echo "Clé SSH genérée"

GIT_SSH_COMMAND="ssh -i ./$SSHKEY -F /dev/null" git clone "$REPOURL"



