# Global state management
class GenerationState:
    def __init__(self):
        self.progress = {"progress": 0, "message": "Not started"}

    def update_progress(self, progress: int, message: str):
        self.progress["progress"] = progress
        self.progress["message"] = message

    def get_progress(self):
        return self.progress.copy()

    def reset(self):
        self.progress["progress"] = 0
        self.progress["message"] = "Not started"

# Create a singleton instance
generation_state = GenerationState() 