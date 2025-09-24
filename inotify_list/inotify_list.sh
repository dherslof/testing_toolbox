#!/usr/bin/env bash

# Author: dherslof
# Description: Short script to list some numbers which might be interesting

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  echo "Usage: $0"
  echo "Lists processes using inotify and shows inotify limits."
  echo "example: $ sudo $1"
  exit 0
fi

for pid in $(ls /proc | grep -E '^[0-9]+$'); do
  if [ -r "/proc/$pid/fd" ]; then
    count=$(ls "/proc/$pid/fd" 2>/dev/null | xargs -I{} readlink "/proc/$pid/fd/{}" 2>/dev/null | grep -c inotify 2>/dev/null)
    if [ "$count" -gt 0 ]; then
      cmd=$(cat "/proc/$pid/comm" 2>/dev/null)
      echo "$pid $cmd $count"
    fi
  fi
done | sort -k3 -n

total_count=$(find /proc/*/fd/* -lname 'anon_inode:inotify' 2>/dev/null | wc -l)
max_watcher=$(cat /proc/sys/fs/inotify/max_user_watches)
max_instances=$(cat /proc/sys/fs/inotify/max_user_instances)

echo "Total count: ${total_count}"
echo "Max watchers: ${max_watcher}"
echo "Max instances: ${max_instances}"

