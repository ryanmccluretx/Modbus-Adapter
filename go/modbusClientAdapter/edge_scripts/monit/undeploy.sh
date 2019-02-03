#!/bin/bash

#Remove modbusClientAdapter from monit
sed -i '/modbusClientAdapter.pid/{N;N;N;N;d}' /etc/monitrc

#Remove the init.d script
rm /etc/init.d/modbusClientAdapter

#Remove the default variables file
rm /etc/default/modbusClientAdapter

#Remove the binary
rm /usr/bin/modbusClientAdapter

#restart monit
/etc/init.d/monit restart

