class QuestionQueue(list):

    def has_next(self):
        return len(self) > 0

    def next(self):
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
        self.__delslice__(0, len(self))
        application_logger.info('Question queue cleared!')


