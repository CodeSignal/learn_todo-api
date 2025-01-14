class Todo:
    """A class representing a single TODO item."""
    def __init__(self, id, task, done=False, description=None):
        self.id = id
        self.task = task
        self.done = done
        self.description = description

    def to_dict(self):
        """Convert the TODO item to a dictionary."""
        return {
            "id": self.id,
            "task": self.task,
            "done": self.done,
            "description": self.description,
        }
