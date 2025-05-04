import customtkinter as ctk
import threading
import ipaddress
import time
import sys
import signal
import os
import subprocess
from datetime import datetime
from typing import Optional, List, Dict
from scapy.all import ARP, Ether, srp, conf, IFACES
import queue

# Description:
#
# Author: Dherslof
# Date: 2025-02-19
# License: MIT

# App version - don't forget to update this
APP_VERSION = "0.1.0"

class PasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Authentication Required")
        self.geometry("400x180")
        self.password = None

        ctk.CTkLabel(self, text="Sudo privileges required for scanning, please enter sudo password:").pack(pady=10)

        self.entry = ctk.CTkEntry(self, show="*")  # Mask input
        self.entry.pack(pady=5, padx=20, fill="x")

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        self.ok_button = ctk.CTkButton(button_frame, text="OK", command=self.on_ok)
        self.ok_button.pack(side="left", padx=5)

        self.cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side="left", padx=5)

        self.entry.bind("<Return>", lambda event: self.on_ok())  # Enter key submits

        self.wait_window()  # Make the dialog modal

    def on_ok(self):
        self.password = self.entry.get()
        self.destroy()

    def on_cancel(self):
        self.password = None
        self.destroy()

def request_sudo_password(parent):
    dialog = PasswordDialog(parent)
    return dialog.password  # Returns password or None if canceled

class ScannerState:
    def __init__(self):
        self.is_scanning = False
        self.sudo_password: Optional[str] = None
        self.message_queue = queue.Queue()

class NetworkScanner:
    def __init__(self, state: ScannerState):
        self.ns_gui_state = state
        self.current_process = None

    def get_interfaces(self) -> List[str]:
        """Retrieve available network interfaces."""
        try:
            return [i.name for i in IFACES.data.values()]
        except Exception as e:
            self.ns_gui_state.message_queue.put(("error", f"Failed to get network interfaces: {str(e)}"))
            return []

    def validate_ip_range(self, ip_range: str) -> bool:
        """Validate if the provided IP range is valid."""
        try:
            ipaddress.ip_network(ip_range)
            return True
        except ValueError:
            return False

    def scan_network(self, interface: str, ip_range: str, timeout: int) -> List[Dict[str, str]]:
        """Perform network scan with proper process management and error handling."""
        devices = []
        process = None

        def cleanup_processes(sudo_password: str) -> None:
            """Helper function to clean up scan processes"""
            try:
                cleanup_cmd = ["sudo", "-S", "pkill", "-9", "-f", "scapy"]
                cleanup_process = subprocess.Popen(
                    cleanup_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                cleanup_process.communicate(input=f"{sudo_password}\n", timeout=5)

                # Verify cleanup
                time.sleep(1)
                verify_cmd = ["pgrep", "-f", "scapy"]
                result = subprocess.run(verify_cmd, capture_output=True, text=True)
                if result.stdout.strip():
                    self.ns_gui_state.message_queue.put(("warning", f"Found remaining processes: {result.stdout.strip()}"))
                else:
                    self.ns_gui_state.message_queue.put(("success", "All scan processes cleaned up"))
            except Exception as e:
                self.ns_gui_state.message_queue.put(("error", f"Cleanup error: {str(e)}"))

        if not interface or interface not in self.get_interfaces():
            self.ns_gui_state.message_queue.put(("error", f"Invalid interface: {interface}"))
            return devices

        if not self.validate_ip_range(ip_range):
            self.ns_gui_state.message_queue.put(("error", f"Invalid IP range: {ip_range}"))
            return devices

        self.ns_gui_state.message_queue.put(("info", f"Starting scan on {interface} in range {ip_range}"))

        try:
            if os.geteuid() != 0:
                if not self.ns_gui_state.sudo_password:
                    self.ns_gui_state.message_queue.put(("error", "Sudo password required for scanning"))
                    return devices

                resp_timeout = 2  # response_timeout per request
                cmd = [
                    "sudo", "-S", "python3", "-c",
                    f"from scapy.all import ARP, Ether, srp; "
                    f"answered_list = srp(Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(pdst='{ip_range}'), "
                    f"iface='{interface}', timeout={resp_timeout}, verbose=False)[0]; "
                    f"print([(rcv.psrc, rcv.hwsrc) for snd, rcv in answered_list])"
                ]

                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    preexec_fn=os.setsid
                )

                self.current_process = process

                try:
                    self.ns_gui_state.message_queue.put(("info", "Running scan with sudo privileges"))
                    process.stdin.write(f"{self.ns_gui_state.sudo_password}\n")
                    process.stdin.flush()

                    start_time = time.time()
                    while True:
                        # Check if we should stop
                        if hasattr(self, 'stop_scan') and self.stop_scan:
                            self.ns_gui_state.message_queue.put(("info", "Scan stopped by user"))
                            return devices

                        # Calculate elapsed time and progress
                        elapsed_time = time.time() - start_time
                        # Convert to percentage but cap at 100%
                        progress = min(1.0, elapsed_time / timeout)
                        self.ns_gui_state.message_queue.put(("progress", progress))

                        # Check for timeout
                        if elapsed_time > timeout:
                            self.ns_gui_state.message_queue.put(("warning", f"Scan timeout after {timeout} seconds"))
                            raise subprocess.TimeoutExpired(cmd, timeout)

                        # Check if process has finished
                        try:
                            output, error = process.communicate(timeout=0.1)
                            # If process finished successfully, set progress to 100%
                            self.ns_gui_state.message_queue.put(("progress", 1.0))
                            break
                        except subprocess.TimeoutExpired:
                            # Sleep a bit to prevent too frequent updates
                            time.sleep(0.2)  # Adjust this value to control update frequency
                            continue

                    if output:
                        try:
                            data = eval(output.strip())
                            for ip, mac in data:
                                devices.append({'ip': ip, 'mac': mac})
                                self.ns_gui_state.message_queue.put(("success", f"Found device - IP: {ip}, MAC: {mac}"))
                        except Exception as e:
                            self.ns_gui_state.message_queue.put(("error", f"Error parsing scan results: {str(e)}"))

                except subprocess.TimeoutExpired:
                    self.ns_gui_state.message_queue.put(("warning", "Scan stopped due to timeout"))

        except Exception as e:
            if "Operation not permitted" not in str(e):
                self.ns_gui_state.message_queue.put(("error", f"Scan error: {str(e)}"))

        finally:
            if process and process.pid:
                cleanup_processes(self.ns_gui_state.sudo_password)
            self.current_process = None
            self.stop_scan = False  # Reset stop flag

        return devices


class NetworkScannerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Store cTkinter's original state() method to not overwrite it with our own
        self.ns_gui_state = self.state
        self.widgets_order = []

        # Initialize state and scanner
        self.ns_gui_state = ScannerState()
        self.scanner = NetworkScanner(self.ns_gui_state)

        # Setup GUI
        self.title("dherslof - APIPA Scanner")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")

        self.setup_variables()
        self.create_widgets()
        self.setup_message_checking()

    def setup_variables(self):
        """Initialize GUI variables."""
        self.interface_var = ctk.StringVar(value="")
        self.timeout_var = ctk.StringVar(value="60")
        self.ip_range_var = ctk.StringVar(value="169.254.0.0/16")

        # Predefined IP ranges
        self.ip_ranges = [
            "169.254.0.0/16",
            "192.168.1.0/24",
            "192.168.0.0/24",
            "10.0.0.0/24",
            "172.16.0.0/24"
        ]

    def create_widgets(self):
        """Create and arrange GUI widgets."""
        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            self.main_frame,
            text="Scan configuration",
            font=("Helvetica", 16, "bold")
        )
        title.pack(pady=10)

        # Settings frame
        settings_frame = ctk.CTkFrame(self.main_frame)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Interface selection
        interface_frame = ctk.CTkFrame(settings_frame)
        interface_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(interface_frame, text="Network Interface:").pack(side="left", padx=5)
        self.interface_dropdown = ctk.CTkComboBox(
            interface_frame,
            values=self.scanner.get_interfaces(),
            variable=self.interface_var,
            width=200
        )
        self.interface_dropdown.pack(side="left", padx=5)

        # IP Range selection
        ip_frame = ctk.CTkFrame(settings_frame)
        ip_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(ip_frame, text="IP Range:").pack(side="left", padx=5)
        self.ip_range_dropdown = ctk.CTkComboBox(
            ip_frame,
            values=self.ip_ranges,
            variable=self.ip_range_var,
            width=200
        )
        self.ip_range_dropdown.pack(side="left", padx=5)

        # Timeout setting
        timeout_frame = ctk.CTkFrame(settings_frame)
        timeout_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(timeout_frame, text="Timeout (seconds):").pack(side="left", padx=5)
        self.timeout_entry = ctk.CTkEntry(
            timeout_frame,
            textvariable=self.timeout_var,
            width=100
        )
        self.timeout_entry.pack(side="left", padx=5)

        # Buttons
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start Scan",
            command=self.start_scan,
            fg_color="#28a745"
        )
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ctk.CTkButton(
            button_frame,
            text="Stop Scan",
            command=self.stop_scan,
            fg_color="#dc3545",
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)

        self.clear_log_button = ctk.CTkButton(
            button_frame,
            text="Clear Log",
            command=lambda: self.reset_previous_runs(),
            fg_color="#0056b3"
        )
        self.clear_log_button.pack(side="left", padx=5)

        # progress bar
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.pack(pady=10, padx=20, fill="x")

        self.scan_progress_bar = ctk.CTkProgressBar(self.progress_frame, mode="determinate", progress_color="#28a745")
        self.scan_progress_bar.pack(fill="x")
        self.scan_progress_bar.set(0)

        # Log display
        self.log_frame = ctk.CTkFrame(self.main_frame)
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = ctk.CTkTextbox(
            self.log_frame,
            height=200,
            wrap="word",
            font=("Courier", 12)
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Version footer
        self.footer = ctk.CTkLabel(
            self.main_frame,
            text=f"Version: {APP_VERSION}",
            font=("Helvetica", 10)
        )
        self.footer.pack(side="left", anchor="w", padx=10, pady=10)

        self.pack_all_widgets()
        self.hide_progress_bar()

    def pack_all_widgets(self):
    # Unpack everything first
        for widget, _ in self.widgets_order:
            widget.pack_forget()

        # Pack everything in order
        for widget, pack_info in self.widgets_order:
         widget.pack(**pack_info)

    def hide_progress_bar(self):
        self.progress_frame.configure(height=0)
        self.scan_progress_bar.pack_forget()

    def show_progress_bar(self):
        self.progress_frame.configure(height=20)
        self.pack_all_widgets()  # Repack everything to maintain order
        self.scan_progress_bar.pack(fill="x")

    def reset_previous_runs(self):
        self.log_text.delete("1.0", "end")
        self.scan_progress_bar.set(0)
        self.hide_progress_bar()

    def setup_message_checking(self):
        """Setup periodic message queue checking."""
        def check_messages():
            while not self.ns_gui_state.message_queue.empty():
                msg_type, message = self.ns_gui_state.message_queue.get()
                if msg_type == "progress":
                    self.scan_progress_bar.set(message)
                else:

                    self.log_message(message, msg_type)
            self.after(100, check_messages)

        self.after(100, check_messages)

    def log_message(self, message: str, msg_type: str = "info"):
        """Log a message with timestamp and appropriate formatting."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Color coding for different message types
        colors = {
            "error": "#ff4444",
            "success": "#00C851",
            "info": "#33b5e5",
            "warning": "#ffbb33",
            "progress": "#ffbb33" # Color don't matter, just used as a pipe for reporting progress to GUI
        }

        self.log_text.insert("end", f"[{timestamp}] ", "timestamp")
        self.log_text.insert("end", f"{message}\n", msg_type)

        # Configure tags for color coding
        self.log_text.tag_config("timestamp", foreground="#888888")
        for tag, color in colors.items():
            self.log_text.tag_config(tag, foreground=color)

        self.log_text.see("end")

    def request_sudo_password(self):
        """Request sudo password from user."""
        self.ns_gui_state.sudo_password = request_sudo_password(self)
        return self.ns_gui_state.sudo_password is not None

    def validate_inputs(self) -> bool:
        """Validate user inputs before starting scan."""
        if not self.interface_var.get():
            self.log_message("Please select a network interface", "error")
            return False

        try:
            timeout = int(self.timeout_var.get())
            if timeout <= 0:
                raise ValueError
        except ValueError:
            self.log_message("Please enter a valid timeout value (positive integer)", "error")
            return False

        if not self.scanner.validate_ip_range(self.ip_range_var.get()):
            self.log_message("Please enter a valid IP range", "error")
            return False

        return True

    def start_scan(self):
        """Start network scan."""
        if not self.validate_inputs():
            return

        if os.geteuid() != 0 and not self.ns_gui_state.sudo_password:
            if not self.request_sudo_password():
                self.log_message("Sudo password required for scanning", "error")
                return

        self.ns_gui_state.is_scanning = True
        self.update_button_states()

        self.show_progress_bar()
        self.scan_progress_bar.set(0)

        # Start scan in separate thread
        scan_thread = threading.Thread(
            target=self.run_scan,
            daemon=True
        )
        scan_thread.start()

    def stop_scan(self):
        """Stop ongoing scan."""
        self.ns_gui_state.is_scanning = False
        self.log_message("Scan stopped by user", "warning")
        self.update_button_states()

    def run_scan(self):
        """Execute network scan."""
        try:
            self.scanner.scan_network(
                interface=self.interface_var.get(),
                ip_range=self.ip_range_var.get(),
                timeout=int(self.timeout_var.get())
            )
        except Exception as e:
            self.log_message(f"Scan failed: {str(e)}", "error")
        finally:
            self.ns_gui_state.is_scanning = False
            self.update_button_states()

    def update_button_states(self):
        """Update button states based on scanning status."""
        if self.ns_gui_state.is_scanning:
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
        else:
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    app = NetworkScannerGUI()
    app.mainloop()