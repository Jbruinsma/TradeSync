class ListNode:
    def __init__(self, val : dict):
        self.val : dict = val
        self.prev : ListNode | None = None
        self.next : ListNode | None = None

class LinkedList:

    def __init__(self):
        self.head : ListNode | None = None
        self.tail : ListNode | None = None
        self.size : int = 0

    def append(self, val: dict) -> None:
        new_node = ListNode(val)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def remove_head(self) -> dict | None:
        if self.is_empty():
            return None
        else:
            removed_node = self.head
            if self.head == self.tail:
                self.head = None
                self.tail = None
            else:
                self.head = self.head.next
                self.head.prev = None
            self.size -= 1
            return removed_node.val

    def get_head(self) -> dict | None:
        if self.is_empty():
            return None
        return self.head.val

    def is_empty(self) -> bool:
        return self.size == 0