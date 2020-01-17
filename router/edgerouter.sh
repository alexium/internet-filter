#!/bin/vbash

VYATTA_CMD=/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper
TAG="configure_ip_addresses"

log_error() {
  echo $@ | logger -t $TAG    
}

commands=$(/config/scripts/edgerouter.py 2>&1)
if [ $? != 0 ]; then
  [ ${#commands} -ge 1 ] && log_error $commands
  exit 1
fi

[ ${#commands} -le 0 ] && exit 0

$VYATTA_CMD begin
[ $? -ge 1 ] && log_error "VYATTA_CMD begin failed"  
while read -r cmd; do
  $VYATTA_CMD $cmd
done <<< "$commands"
[ $? -ge 1 ] && log_error "VYATTA_CMD firewall modify failed"
$VYATTA_CMD commit
[ $? -ge 1 ] && log_error "VYATTA_CMD commit failed"
$VYATTA_CMD end
[ $? -ge 1 ] && log_error "VYATTA_CMD end failed"

exit 0
