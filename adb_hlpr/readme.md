# adb_hlpr - adb Helper
Simple support tool for wrapping [adb](https://developer.android.com/studio/command-line/adb) commands which maybe isn't used every day. Can be used in alias for improved speed. 

## Dependencies
* typing_extensions (pip3 install typing_extensions)

## Supported commands
| Function    | cmd         |Description |
| ----------- | ----------- | -----------|
| screenshot  | `python3 adb_hlpr -s` | take a screenshot of the screen |
| dump log    | `python3 adb_hlpr -d` | dump logcat log, all buffers |
| inject log  | `python3 adb_hlpr -i "<log message>"` | Inject a logcat message. **Note -** No special chars |
| clear log | `python3 adb_hlpr -C` | clear (flush) logcat log |
| create bug report  | `python3 adb_hlpr -b` | generate a bugreport |
| screenrecord  | `python3 adb_hlpr -r <nr_of_seconds` | record the screen for **n** seconds (Android needs a rendering screen) |

### Help flags
* -v, verbose logging of wrapper itself
* -h, show help
