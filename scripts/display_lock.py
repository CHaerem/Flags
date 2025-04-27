#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import time
import fcntl
import errno
import logging

logger = logging.getLogger(__name__)

class DisplayLock:
    """
    A file-based locking mechanism to ensure exclusive access to the e-paper display.
    This prevents GPIO conflicts when multiple processes attempt to update the display simultaneously.
    """
    
    def __init__(self, lock_file=None, timeout=10):
        """Initialize the display lock with the specified lock file and timeout."""
        # Base directory of this project (~/Flags)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.lock_file = lock_file or os.path.join(base_dir, ".display.lock")
        self.timeout = timeout
        self.fd = None
        self.acquired = False
    
    def acquire(self, timeout=None):
        """
        Acquire the display lock with a timeout.
        Returns True if the lock was acquired, False otherwise.
        """
        if self.acquired:
            return True
            
        timeout = timeout if timeout is not None else self.timeout
        start_time = time.time()
        
        try:
            # Create the lock file if it doesn't exist
            self.fd = open(self.lock_file, 'w+')
            
            while True:
                try:
                    # Try to acquire an exclusive lock (non-blocking)
                    fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.acquired = True
                    logger.debug(f"Display lock acquired: {self.lock_file}")
                    return True
                except IOError as e:
                    # Resource temporarily unavailable - lock is held by another process
                    if e.errno != errno.EAGAIN:
                        logger.error(f"Error acquiring display lock: {e}")
                        return False
                        
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        logger.warning(f"Timeout waiting for display lock: {elapsed:.1f}s")
                        return False
                    
                    # Wait a bit before retrying
                    time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error setting up display lock: {e}")
            self._cleanup()
            return False
    
    def release(self):
        """Release the display lock."""
        if self.acquired and self.fd:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_UN)
                self.acquired = False
                logger.debug(f"Display lock released: {self.lock_file}")
            except Exception as e:
                logger.error(f"Error releasing display lock: {e}")
            finally:
                self._cleanup()
    
    def _cleanup(self):
        """Clean up file descriptor resources."""
        if self.fd:
            try:
                self.fd.close()
            except:
                pass
            self.fd = None
    
    def __enter__(self):
        """Context manager entry."""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit."""
        self.release()


def with_display_lock(func):
    """
    Decorator to ensure a function is executed with the display lock.
    If the lock cannot be acquired, the function will not be executed.
    """
    def wrapper(*args, **kwargs):
        with DisplayLock() as lock:
            if lock.acquired:
                return func(*args, **kwargs)
            else:
                logger.warning(f"Could not acquire display lock for {func.__name__}")
                return None
    return wrapper