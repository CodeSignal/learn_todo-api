class Todo:
    """A class representing a single TODO item."""
    def __init__(self, id, title, done=False, description=None):
        self.id = id
        self.title = title
        self.done = done
        self.description = description

    def to_dict(self):
        """Convert the TODO item to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "description": self.description,
        }
