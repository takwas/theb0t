class QuestionQueue(list):

    def enqueue(self, nick):
        """Add nick to queue."""
        self.append(nick)

    def dequeue(self, nick):
        """
        Go from tail to head and remove first matching nick in queue.
        """
        for i in range(-1, -len(self)-1, -1):
            if (self[i] == nick):
                del self[i]
                break

    def has_next(self):
        """Check if queue has at least one item."""
        return len(self) > 0

    def peek_next(self):
        """Get next item on queue, but don't remove from queue."""
        if self.has_next():
            return self[0]
        else:
            return None

    def pop_next(self):
        """Get next item on queue,and also remove same from queue."""
        if self.has_next():
            return self.pop(0)
        else:
            return None

    def clear(self):
        """Clear all items from queue."""
        self.__delslice__(0, len(self))


