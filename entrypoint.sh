#!/bin/bash

env | sed 's/^\(.*\)$/export \1/g' > $HOME/environment
cron
touch $HOME/cron.log
tail -f $HOME/cron.log
