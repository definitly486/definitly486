#!/bin/sh

var1=5
while [ $var1 -gt 0 ]
do
var=$(sshpass -p 639639 ssh  definitly@192.168.8.101 "sysctl -n dev.cpu.0.temperature | cut -c 1-2")
#gputemp=$(sshpass -p 639639 ssh  definitly@192.168.8.101 "nvidia-settings -tq "[gpu:0]/GPUCoreTemp"")
gputemp=$(sensors | grep temp1 | awk {'print$2'})
top=$(sshpass -p 639639 ssh  definitly@192.168.8.101 "top | awk 'NR==9;' | awk '{print \$12 ,\$11}'")
echo cputemp:$var
echo gputemp:$gputemp
echo $top
sleep 10
done
