#!/bin/bash
PID=$(ps aux | grep '[p]ython -u app.py' | awk '{print $2}')

if [ -n "$PID" ]; then
  kill $PID
  echo "程序已停止"
else
  echo "程序未运行"
fi