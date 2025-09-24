# inotify-list

A simple Bash script to list processes using inotify and display inotify limits on your system.

## Usage

```bash
sudo ./inotify_list.sh
```

Show help:

```bash
./inotify_list.sh -h
```

## Output

- Lists each process using inotify, showing PID, command, and inotify count.
- Shows total inotify instances and system limits.