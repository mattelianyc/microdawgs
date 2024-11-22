import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import subprocess
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_training()

    def restart_training(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        
        logger.info("Starting training process...")
        self.process = subprocess.Popen([sys.executable, "src/train.py"])

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            logger.info(f"Detected change in {event.src_path}")
            self.restart_training()

def watch_training():
    handler = TrainingHandler()
    observer = Observer()
    observer.schedule(handler, path='src', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if handler.process:
            handler.process.terminate()
    observer.join()

if __name__ == "__main__":
    watch_training() 