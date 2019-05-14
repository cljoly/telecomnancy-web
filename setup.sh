#!/usr/bin/env bash

SSHKEY=./gitly_ssh.key

if [ -f $SSHKEY ]; then
  rm -v $SSHKEY $SSHKEY.pub
fi

ssh-keygen -t rsa -C "" -N "" -f $SSHKEY
mkdir -p clone_dir
