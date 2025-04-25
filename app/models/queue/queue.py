from app.models.queue.linked_list.linked_list import LinkedList


class ProfitQueue:

    def __init__(self):
        self.queue : LinkedList = LinkedList()

    def push(self, val : dict) -> None:
        if val is not None:
            self.queue.append(val)

    def pop(self) -> dict | None:
        if self.is_empty():
            return None
        return self.queue.remove_head()

    def peek(self) -> dict | None:
        if self.is_empty():
            return None
        return self.queue.get_head()

    def is_empty(self) -> bool:
        return self.queue.is_empty()