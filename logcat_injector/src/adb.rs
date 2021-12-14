//------------------------------------------------------------------------------
// Project: logcat_injector
// File name: adb.rs
// File Description: The adb logcat entry
// License: MIT
//------------------------------------------------------------------------------

use std::error::Error;
use std::fmt;
use std::io::{BufRead, BufReader};
use std::process::{Command, Stdio};

#[derive(Debug)]
pub struct AdbError {
    error_msg: String,
}
impl AdbError {
    fn new(msg: &str) -> AdbError {
        return AdbError {
            error_msg: msg.to_string(),
        };
    }
}

impl fmt::Display for AdbError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.error_msg)
    }
}

impl Error for AdbError {
    fn description(&self) -> &str {
        return &self.error_msg;
    }
}

impl From<std::io::Error> for AdbError {
    fn from(err: std::io::Error) -> Self {
        let tmp = err.to_string();
        return AdbError::new(&tmp.as_str());
    }
}

#[derive(Debug, Default)]
pub struct AdbWrapper {
    device: String,
}

impl fmt::Display for AdbWrapper {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "device: {:?}\n", &self.device)
    }
}

impl AdbWrapper {
    pub fn discover() -> Result<AdbWrapper, AdbError> {
        let mut device_vec = Vec::new();
        let mut line_counter = 0;

        let adb_devices = Command::new("adb")
            .arg("devices")
            .stdout(Stdio::piped())
            .spawn()?
            .stdout
            .ok_or_else(|| AdbError::new("'adb devices' failed"))?;

        let adb_devices_reader = BufReader::new(adb_devices);
        adb_devices_reader
            .lines()
            .filter_map(|line| line.ok())
            .filter(|line| line.find("device").is_some())
            .for_each(|line| {
                if line_counter >= 1 {
                    let device_name: Vec<&str> = line.split_whitespace().collect();
                    //println!("DEV - found: {}", line);
                    let device_name: String = device_name[0].to_string();
                    //println!("DEV - when splitted: {}", device_name);

                    device_vec.push(device_name);
                }
                line_counter += 1;
            });

        if device_vec.len() < 1 {
            return Err(AdbError::new("No adb device found"));
        } else if device_vec.len() > 1 {
            return Err(AdbError::new(
                "Multiple adb devices found, please explicit provide device name",
            ));
        }

        //println!("DEV - number of lines: {}", device_vec.len());
        return Ok(AdbWrapper {
            device: device_vec[0].clone(),
        });
    }

    pub fn set_device_from_matches(device_name: &str) -> AdbWrapper {
        return AdbWrapper {
            device: device_name.to_string(),
        };
    }

    pub fn device_name(&self) -> Option<String> {
        if self.device.is_empty() {
            return None;
        } else {
            return Some(self.device.clone());
        }
    }

    pub fn inject_log_entry(&self, log_tag: &str, log_msg: &str) {
        Command::new("adb")
            .arg("shell")
            .arg("log")
            .arg("-t")
            .arg(log_tag)
            .arg(log_msg)
            .output()
            .expect("'adb shell log' for log injection failed");
    }
}
