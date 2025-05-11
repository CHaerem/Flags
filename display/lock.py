"""
Display lock implementation to prevent concurrent access to physical display hardware.
Uses file-based locking to ensure multiple processes don't interfere with each other.
"""

import os
import time
import fcntl
import errno
import logging
import datetime

logger = logging.getLogger(__name__)

class DisplayLock:
    """
    A file-based locking mechanism to ensure exclusive access to the e-paper display.
    This prevents GPIO conflicts when multiple processes attempt to update the display simultaneously.
    """
    
    def __init__(self, lock_file=None, timeout=20):
        """
        Initialize the display lock with the specified lock file and timeout.
        
        Args:
            lock_file (str, optional): Path to the lock file. Defaults to None (uses default path).
            timeout (int, optional): Maximum time to wait for lock acquisition in seconds. Defaults to 20.
        """
        # Base directory of this project (~/Flags)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.lock_file = lock_file or os.path.join(base_dir, ".display.lock")
        self.timeout = timeout
        self.fd = None
        self.acquired = False
        
        # Check for stale locks at initialization
        self._check_stale_lock()
    
    def _check_stale_lock(self):
        """Check if the lock file exists but is stale (old) and remove it if needed."""
        try:
            # If the lock file exists, check its age
            if os.path.exists(self.lock_file):
                file_age = time.time() - os.path.getmtime(self.lock_file)
                # If the file is older than 2 minutes, it's likely a stale lock
                if file_age > 120:  # 2 minutes in seconds
                    logger.warning(f"Found stale lock file (age: {file_age:.1f}s), removing it")
                    try:
                        os.remove(self.lock_file)
                        logger.info("Stale lock file removed")
                    except Exception as e:
                        logger.error(f"Failed to remove stale lock file: {e}")
        except Exception as e:
            logger.error(f"Error checking stale lock: {e}")
    
    def acquire(self, timeout=None):
        """
        Acquire the display lock with a timeout.
        
        Args:
            timeout (int, optional): Custom timeout for this acquisition attempt. 
                                     Defaults to None (uses instance timeout).
                                     
        Returns:
            bool: True if the lock was acquired, False otherwise.
        """
        if self.acquired:
            return True
            
        timeout = timeout if timeout is not None else self.timeout
        start_time = time.time()
        
        try:
            # Close previous file descriptor if it exists
            self._cleanup(remove_file=False)
            
            # Create the lock file if it doesn't exist
            self.fd = open(self.lock_file, 'w+')
            # Write current timestamp and process info to the lock file for debugging
            self.fd.write(f"Lock acquired by PID {os.getpid()} at {datetime.datetime.now().isoformat()}\n")
            self.fd.flush()
            
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
                        self._cleanup()
                        return False
                        
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        logger.warning(f"Timeout waiting for display lock: {elapsed:.1f}s")
                        self._cleanup()
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
    
    def _cleanup(self, remove_file=True):
        """
        Clean up file descriptor resources.
        
        Args:
            remove_file (bool, optional): Whether to remove the lock file. Defaults to True.
        """
        if self.fd:
            try:
                self.fd.close()
            except:
                pass
            self.fd = None
            
            # Try to remove the lock file when we're done
            if remove_file:
                try:
                    if os.path.exists(self.lock_file):
                        os.remove(self.lock_file)
                        logger.debug(f"Lock file removed: {self.lock_file}")
                except Exception as e:
                    logger.debug(f"Could not remove lock file: {e}")
    
    def __enter__(self):
        """Context manager entry point."""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit point."""
        self.release()


def with_display_lock(func):
    """
    Decorator to ensure a function is executed with the display lock.
    If the lock cannot be acquired, the function will not be executed.
    
    Args:
        func: The function to wrap with display lock acquisition.
        
    Returns:
        wrapper: The wrapped function that acquires a lock before execution.
    """
    def wrapper(*args, **kwargs):
        with DisplayLock() as lock:
            if lock.acquired:
                return func(*args, **kwargs)
            else:
                logger.warning(f"Could not acquire display lock for {func.__name__}")
                return None
    return wrapper