- mettre l'interface eth1 en Acces par pont
- copier isc-dhcp-server dans /etc/default/isc-dhcp-server
- copier dhcpd.conf dans /etc/dhcp/dhcpd.conf
- mettre l'interface eth1 en static 192.168.5.1/24


sudo systemctl restart networking.service
sudo systemctl restart isc-dhcp-server.service
sudo systemctl status isc-dhcp-server.service

