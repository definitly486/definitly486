#!/bin/sh
sshpass -p  639639 ssh  -T definitly@192.168.8.103 << 'EOF'
#!/bin/sh

exec >> "$HOME/log" 2>&1

LOCKFILE="/tmp/myscript.lock"

if [ -f "$LOCKFILE" ]; then
  echo "Already running"
  exit 1
fi

trap "rm -f $LOCKFILE" EXIT
touch "$LOCKFILE"

var1=5000
while [ $var1 -gt 0 ]
do
  cputemp=$(sysctl -n dev.cpu.0.temperature | cut -c 1-2)
  top_proc=$(ps -axo comm,%cpu | sort -k2 -nr | awk 'NR==2 {print $1, $2}')
  now=$(date "+%Y-%m-%d %H:%M:%S")

  echo "PID:$$ time:$now cputemp:$cputemp"
  echo "time:$now top:$top_proc"

  sleep 60
  var1=$((var1 - 1))
done
EOF
