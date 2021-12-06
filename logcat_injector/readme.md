# Logcat injector 
Inject log entry's to [logcat](https://developer.android.com/studio/command-line/logcat) from host. Either continuously or once. Can be useful to mark a certain `starting point` or
a `special event` which can be good to know when looking in the logs after. Written in Rust. 

## Dependencies
* [adb](https://developer.android.com/studio/command-line/adb)
* [rust (cargo)](https://www.rust-lang.org/tools/install)

## Building
Build from source using cargo:
```bash
$ git clone git@github.com:dherslof/testing_toolbox.git && cd testing_toolbox/cargo_injector
$ cargo install

```

## Usage
Inject log message `foobar` with my special log tag `myTag`: 
```bash
$ log_injector --tag "myTag" --message "foobar"
```

Continuously add messages with default tag: 
```bash
$ log_injector
```


