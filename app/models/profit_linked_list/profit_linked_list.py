class ProfitListNode:

    def __init__(self, val: dict):
        self.val : dict | None = val
        self.prev : ProfitListNode | None = None
        self.next : ProfitListNode | None = None

    def __str__(self) -> str:
        return f"{self.val}"


class ProfitLinkedList:

    def __init__(self):
        self.head : ProfitListNode | None= None
        self.tail : ProfitListNode | None= None
        self.size : int = 0

    def __str__(self) -> str:
        if self.is_empty():
            return "[]"
        else:
            ll_str = ""
            curr = self.head
            while curr is not None:
                ll_str += f"{curr.val}"
                curr = curr.next
                if curr is not None:
                    ll_str += " <--> "
            return ll_str

    def __len__(self) -> int:
        return self.size

    def prepend(self, val: dict) -> None:
        new_node = ProfitListNode()
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.size += 1

    def append(self, val : dict) -> None:
        new_node = ProfitListNode()
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def remove_head(self) -> ProfitListNode | None:
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
            removed_node.next = None
            self.size -= 1
            return removed_node

    def get_head_value(self) -> dict | None:
        if self.is_empty():
            return None
        else:
            return self.head.val

    def clear(self) -> None:
        self.head = None
        self.tail = None
        self.size = 0

    def is_empty(self) -> bool:
        return self.head is None and self.size == 0