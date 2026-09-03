from scapy.all import *

packets = sniff(count=100)
wrpcap("captured.pcap", packets)
print("Захвачено 100 пакетов и сохранено в файл captured.pcap")