#!/bin/bash

#Copy binary to /usr/local/bin
mv modbusClientAdapter /usr/bin

#Ensure binary is executable
chmod +x /usr/bin/modbusClientAdapter

#Set up init.d resources so that modbusClientAdapter is started when the gateway starts
mv modbusClientAdapter.etc.initd /etc/init.d/modbusClientAdapter
mv modbusClientAdapter.etc.default /etc/default/modbusClientAdapter

#Ensure init.d script is executable
chmod +x /etc/init.d/modbusClientAdapter

#Add adapter to log rotate
cat << EOF > /etc/logrotate.d/modbusClientAdapter.conf
/var/log/modbusClientAdapter {
    size 10M
    rotate 3
    compress
    copytruncate
    missingok
}
EOF

#Remove modbusClientAdapter from monit in case it was already there
sed -i '/modbusClientAdapter.pid/{N;N;N;N;d}' /etc/monitrc

#Add the adapter to monit
sed -i '/#  check process apache with pidfile/i \
  check process modbusClientAdapter with pidfile \/var\/run\/modbusClientAdapter.pid \
    start program = "\/etc\/init.d\/modbusClientAdapter start" with timeout 60 seconds \
    stop program  = "\/etc\/init.d\/modbusClientAdapter stop" \
    depends on edge \
 ' /etc/monitrc

#restart monit
/etc/init.d/monit restart

#Start the adapter
monit start modbusClientAdapter

echo "modbusClientAdapter Deployed"