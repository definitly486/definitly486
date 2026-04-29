#!/bin/sh
# Определение среды
if [ -n "$PSModulePath" ]; then
  ENV_TYPE="powershell"
elif [ "$MSYSTEM" = "MINGW64" ] || [ "$MSYSTEM" = "MINGW32" ]; then
  ENV_TYPE="mingw"
else
  ENV_TYPE="linux"
fi

echo "Detected environment: $ENV_TYPE"

# Выбор команды ssh
if [ "$ENV_TYPE" = "linux" ]; then
  SSH_CMD="sshpass -p 639639 ssh -T definitly@192.168.8.103"
else
  echo "sshpass disabled for $ENV_TYPE"
  SSH_CMD="ssh -T definitly@192.168.8.103"
fi

$SSH_CMD << 'EOF'
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
