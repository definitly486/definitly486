#!/bin/sh
sshpass -p  639639 ssh definitly@192.168.8.103 << 'EOF'
#!/bin/sh

var1=5
while [ $var1 -gt 0 ]
do
  cputemp=$(sysctl -n dev.cpu.0.temperature | cut -c 1-2)
  top=$(top | awk 'NR==9' | awk '{print $12 ,$11}')
  now=$(date "+%Y-%m-%d %H:%M:%S")

  echo "time:$now cputemp:$cputemp" >> $HOME/log
  echo "time:$now top:$top" >> $HOME/log

  sleep 60
done
EOF
