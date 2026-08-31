from scapy.all import *

# pkt = IP(dst="8.8.8.8")
# print(pkt.show())

# eth = Ether(src ="aa:bb:cc:dd:ee:ff", dst="ff:ff:ff:ff:ff:ff" , type=0x0800) / pkt
# print(eth.show())

tcp_syn = TCP(sport=12345, dport=443, flags="S", seq=1000, window=65535)
pkt = IP(dst="example.com") / tcp_syn
# print(pkt.show())
ls(pkt)

# send(IP(dst="8.8.8.8")/ICMP())