from app.models.profit_linked_list.profit_linked_list import ProfitLinkedList


class MonthlyProfitQueue:

    def __init__(self):
        MAX_SIZE : int = 31
        self.queue : ProfitLinkedList = ProfitLinkedList()

    def enqueue(self, val: dict) -> None:
        self.queue.append(val)

    def dequeue(self) -> None:
        self.queue.remove_head()

    def get_monthly_profit_sum(self) -> float:
        pass