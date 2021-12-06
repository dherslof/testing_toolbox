//------------------------------------------------------------------------------
// Project: logcat_injector
// File name: main.rs
// File Description: The log entry injector main file
// License: MIT
//------------------------------------------------------------------------------

#[macro_use]
extern crate clap;
use clap::{App, AppSettings, Arg};

use std::io;
use std::process;

mod adb;
mod entry;

fn main() {
    // verify unix
    if !cfg!(unix) {
        eprintln!("Not a unix system, exiting...");
        process::exit(-1);
    }

    // setup cli and get arguments
    let matches = App::new("logcat_injector - Inject log entry's to logcat from host")
        .version(crate_version!())
        .author(crate_authors!("\n"))
        .about(crate_description!())
        .setting(AppSettings::ColorAlways)
        .arg(
            Arg::with_name("Tag")
                .help("The logTag to use")
                .required(false)
                .long("TAG")
                .short("t")
                .takes_value(true),
        )
        .arg(
            Arg::with_name("Message")
                .help("Message to inject")
                .required(false)
                .long("MESSAGE")
                .short("m")
                .takes_value(true),
        )
        .arg(
            Arg::with_name("adb-Device")
                .help("adb device to use")
                .required(false)
                .long("device")
                .short("d")
                .takes_value(true),
        )
        .get_matches();

    // Set log tag
    let log_tag: &str;
    if matches.is_present("Tag") {
        log_tag = matches.value_of("Tag").unwrap();
    } else {
        log_tag = entry::DEFAULT_TAG;
        println!("No log tag provided, using default: {}", log_tag);
    }

    // Get adb device
    let adb_device: adb::AdbWrapper;
    if matches.is_present("adb-Device") {
        adb_device =
            adb::AdbWrapper::set_device_from_matches(matches.value_of("adb-Device").unwrap());
    } else {
        let device = match adb::AdbWrapper::discover() {
            Ok(d) => Ok(d),
            Err(err) => {
                eprintln!("Failed to get adb device: {}", err);
                Err(err)
            }
        };
        // Exit if we failed to set adb device
        if device.is_err() {
            process::exit(0);
        }

        adb_device = device.unwrap();
    }

    // Print name of device used
    match adb_device.device_name() {
        Some(device) => println!("Using device: {}", device),
        None => eprintln!("No adb device name set"), // Should never happen
    }


    // If message provided, we inject en exit
    if matches.is_present("Message") {
        // Create log entry
        let logcat_entry = entry::LogCatEntry::new(log_tag, matches.value_of("Message").unwrap());

        // inject log entry
        adb_device.inject_log_entry(
            logcat_entry.get_log_tag().as_str(),
            logcat_entry.get_log_msg().as_str(),
        );

        println!("Injected: \n{:?}", logcat_entry);
    } else {
        // Continuously read and inject
        loop {
            let mut input_msg = String::new();
            match io::stdin().read_line(&mut input_msg) {
                Ok(_n) => {
                    // Check if we should break and exit
                    if input_msg == "exit\n\r".to_string() || input_msg == "quit\n\r".to_string() {
                        process::exit(0);
                    }

                    // Create entry and inject
                    let logcat_entry = entry::LogCatEntry::new(log_tag, input_msg.as_str());

                    // inject log entry
                    adb_device.inject_log_entry(
                        logcat_entry.get_log_tag().as_str(),
                        logcat_entry.get_log_msg().as_str(),
                    );

                    println!("Injected: {:?}", adb_device);
                    //println!("{} bytes read", n);
                    //println!("{}", input_msg);
                }
                Err(error) => eprintln!("Failed to read stdin: {}", error),
            }
        }
    }
}
