# frontend.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from backend import Stopwatch, ActivityMonitor
import threading
import csv
import os
from typing import Optional
import time

class TimerApp:
    """Main application GUI"""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart Stopwatch")
        self.stopwatch = Stopwatch()
        self.activity_monitor: Optional[ActivityMonitor] = None
        self.idle_check_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Initialize UI
        self._setup_ui()
        self._setup_idle_check()
        self.protocols()

    def _setup_ui(self) -> None:
        """Create and arrange UI components"""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Time display
        self.time_var = tk.StringVar(value="00:00:00")
        time_label = ttk.Label(
            main_frame, 
            textvariable=self.time_var,
            font=('Helvetica', 24)
        )
        time_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Controls
        self.start_btn = ttk.Button(
            main_frame, 
            text="Start", 
            command=self.toggle_timer
        )
        self.reset_btn = ttk.Button(
            main_frame,
            text="Reset",
            command=self.reset_timer,
            state=tk.DISABLED
        )
        self.start_btn.grid(row=1, column=0, padx=5)
        self.reset_btn.grid(row=1, column=1, padx=5)

        # Idle settings
        ttk.Label(main_frame, text="Idle Threshold (minutes):").grid(
            row=2, column=0, pady=10, sticky="e"
        )
        self.idle_entry = ttk.Entry(main_frame, width=5)
        self.idle_entry.insert(0, "5")
        self.idle_entry.grid(row=2, column=1, sticky="w")
        ttk.Button(main_frame, text="Set", command=self.update_idle_threshold).grid(
            row=2, column=2, padx=5
        )

        # Export button
        ttk.Button(
            main_frame,
            text="Export Today's Data",
            command=self.export_data
        ).grid(row=3, column=0, columnspan=3, pady=10)

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def _setup_idle_check(self) -> None:
        """Initialize idle time monitoring"""
        self.activity_monitor = ActivityMonitor(self.handle_activity)
        self.activity_monitor.start()
        self.running = True
        self.idle_check_thread = threading.Thread(target=self.check_idle_time)
        self.idle_check_thread.start()

    def protocols(self) -> None:
        """Set up window protocols"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_timer(self) -> None:
        """Handle start/pause toggle"""
        if self.stopwatch._is_running:
            self.stopwatch.pause()
            self.start_btn.config(text="Start")
            self.reset_btn.config(state=tk.NORMAL)
        else:
            self.stopwatch.start()
            self.start_btn.config(text="Pause")
            self.reset_btn.config(state=tk.DISABLED)
            self.update_time_display()

    def reset_timer(self) -> None:
        """Handle timer reset"""
        self.stopwatch.reset()
        self.time_var.set("00:00:00")
        self.reset_btn.config(state=tk.DISABLED)

    def update_idle_threshold(self) -> None:
        """Update maximum allowed idle time"""
        try:
            minutes = int(self.idle_entry.get())
            self.stopwatch.idle_threshold = minutes * 60
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")

    def handle_activity(self) -> None:
        """Handle user activity detection"""
        self.stopwatch.update_activity()
        if not self.stopwatch._is_running:
            self.stopwatch.start()
            self.start_btn.config(text="Pause")

    def check_idle_time(self) -> None:
        """Background thread to check for idle time"""
        while self.running:
            idle_time = self.stopwatch.check_idle_time()
            threshold = self.stopwatch.idle_threshold
            
            if idle_time >= threshold:
                self.root.after(0, self.handle_idle_timeout, threshold)
                
            time.sleep(1)

    def handle_idle_timeout(self, threshold: int) -> None:
        """Handle idle timeout confirmation"""
        self.stopwatch.pause()
        response = messagebox.askyesno(
            "Idle Time Detected",
            f"Subtract {threshold//60} minutes of idle time?",
            parent=self.root
        )
        
        if response:
            self.stopwatch.subtract_idle_time(threshold)
        self.update_time_display()
        self.start_btn.config(text="Start")

    def update_time_display(self) -> None:
        """Update the GUI time display"""
        if self.stopwatch._is_running:
            elapsed = self.stopwatch.get_elapsed()
            self.time_var.set(str(elapsed).split('.')[0])
            self.root.after(1000, self.update_time_display)

    def export_data(self) -> None:
        """Export today's data to CSV"""
        filename = f"timer_export_{datetime.now().date()}.csv"
        elapsed = self.stopwatch.get_elapsed()
        
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            if os.stat(filename).st_size == 0:
                writer.writerow(["Date", "Total Time"])
            writer.writerow([datetime.now().date(), elapsed])
        
        messagebox.showinfo("Export Complete", f"Data saved to {filename}")

    def on_close(self) -> None:
        """Handle window close event"""
        self.running = False
        self.activity_monitor.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()