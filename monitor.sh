#!/bin/sh

var1=5
while [ $var1 -gt 0 ]
do

cputemp=$(sysctl -n dev.cpu.0.temperature | cut -c 1-2)
top=$(top | awk 'NR==9;' | awk '{print $12 ,$11}')
echo cputemp:$cputemp
echo top:$top

sleep 10
done
