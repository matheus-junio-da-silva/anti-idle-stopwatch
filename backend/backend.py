# backend.py
import time
import threading
from datetime import timedelta
from pynput import mouse, keyboard
from queue import Queue, Empty
from typing import Optional, Callable

class Stopwatch:
    """Thread-safe stopwatch with idle time detection handling"""
    def __init__(self):
        self._start_time: Optional[float] = None
        self._elapsed: float = 0
        self._is_running: bool = False
        self._lock = threading.Lock()
        self._idle_threshold: int = 300  # 5 minutes default
        self._last_activity_time: float = time.monotonic()

    def start(self) -> None:
        """Start or resume the stopwatch"""
        with self._lock:
            if not self._is_running:
                self._start_time = time.monotonic()
                self._is_running = True

    def pause(self) -> None:
        """Pause the stopwatch"""
        with self._lock:
            if self._is_running:
                self._elapsed += time.monotonic() - self._start_time
                self._is_running = False

    def reset(self) -> None:
        """Reset stopwatch to initial state"""
        with self._lock:
            self._start_time = None
            self._elapsed = 0
            self._is_running = False

    def get_elapsed(self) -> timedelta:
        """Get current elapsed time"""
        with self._lock:
            if self._is_running:
                current_elapsed = self._elapsed + (time.monotonic() - self._start_time)
            else:
                current_elapsed = self._elapsed
            return timedelta(seconds=current_elapsed)

    def subtract_idle_time(self, idle_seconds: int) -> None:
        """Subtract idle time from total elapsed"""
        with self._lock:
            self._elapsed = max(0, self._elapsed - idle_seconds)

    def update_activity(self) -> None:
        """Update last activity timestamp"""
        with self._lock:
            self._last_activity_time = time.monotonic()

    def check_idle_time(self) -> float:
        """Calculate current idle time in seconds"""
        with self._lock:
            return time.monotonic() - self._last_activity_time

    @property
    def idle_threshold(self) -> int:
        return self._idle_threshold

    @idle_threshold.setter
    def idle_threshold(self, value: int) -> None:
        with self._lock:
            self._idle_threshold = value

class ActivityMonitor:
    """Monitors user activity using input devices"""
    def __init__(self, activity_callback: Callable[[], None]):
        self._activity_callback = activity_callback
        self._listeners = []
        self._event_queue = Queue()
        self._running = False

    def _on_activity(self) -> None:
        """Handle any user activity event"""
        self._event_queue.put(True)

    def _process_events(self) -> None:
        """Process events from the queue"""
        while self._running:
            try:
                self._event_queue.get(timeout=0.1)
                self._activity_callback()
            except Empty:
                continue

    def start(self) -> None:
        """Start monitoring"""
        self._running = True
        self._listeners = [
            mouse.Listener(on_move=self._on_activity),
            keyboard.Listener(on_press=self._on_activity)
        ]
        for listener in self._listeners:
            listener.start()
        
        self._processor_thread = threading.Thread(target=self._process_events)
        self._processor_thread.start()

    def stop(self) -> None:
        """Stop monitoring"""
        self._running = False
        for listener in self._listeners:
            listener.stop()
        self._processor_thread.join()