//------------------------------------------------------------------------------
// Project: logcat_injector
// File name: entry.rs
// File Description: The adb logcat entry
// License: MIT
//------------------------------------------------------------------------------

use std::fmt;

pub const DEFAULT_TAG: &str = "HostLogInjector";

//------------------------------------------------------------------------------

#[derive(Debug)]
pub struct LogCatEntry {
    log_tag: String,
    log_msg: String,
}

impl fmt::Display for LogCatEntry {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Log-Tag: {:?}\nMessage: {:?}",
            &self.log_tag, &self.log_msg
        )
    }
}

impl LogCatEntry {
    pub fn new(tag: &str, msg: &str) -> LogCatEntry {
        return LogCatEntry {
            log_tag: tag.to_string(),
            log_msg: msg.to_string(),
        };
    }

    pub fn get_log_tag(&self) -> &String {
        return &self.log_tag;
    }

    pub fn get_log_msg(&self) -> &String {
        return &self.log_msg;
    }
}

//------------------------------------------------------------------------------
