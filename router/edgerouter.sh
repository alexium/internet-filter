#!/bin/vbash

VYATTA_CMD=/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper

commands=$(/config/scripts/edgerouter.py $@)
if [ $? != 0 ]; then
  [ ${#commands} -ge 1 ] && echo $commands
  exit 1
fi

[ ${#commands} -le 0 ] && exit 0

$VYATTA_CMD begin
while read -r cmd; do
  $VYATTA_CMD $cmd
done <<< "$commands"
$VYATTA_CMD commit
$VYATTA_CMD end
