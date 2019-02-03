Instructions for use:

1. Copy modbusClientAdapter.etc.default file into /etc/default, name the file "modbusClientAdapter"
2. Modify the values of the variables defined in the /etc/default/modbusClientAdapter file to match your system
3. Copy modbusClientAdapter.etc.initd file into /etc/init.d, name the file "modbusClientAdapter"
4. From a terminal prompt, execute the following commands:
	3a. chmod 755 /etc/init.d/modbusClientAdapter
	3b. chown root:root /etc/init.d/modbusClientAdapter
	3c. update-rc.d modbusClientAdapter defaults 85

If you wish to start the adapter, rather than reboot, issue the following command from a terminal prompt:

	/etc/init.d/modbusClientAdapter start