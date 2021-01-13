# different queues for use
from typing import Callable, Any, Tuple
from random import choice as rchoice


class PriorityQueue:
    def __init__(self, is_min: bool):
        """!
        """
        self.is_min = is_min
        self.queue = []

    def push(self, key, val):
        """!
        push element to priority queue
        """
        self.queue.append((key, val))
        self.sort()

    def sort(self):
        """!
        sort priority queue
        """
        if self.is_min is True:
            self.queue.sort(key=lambda x: x[0])
        else:
            self.queue.sort(key=lambda x: x[0], reverse=True)

    def index(self, val) -> int:
        """!
        """
        if not self.queue:
            return -1
        for i, (k, v) in enumerate(self.queue):
            if v == val:
                return i
        return -1

    def insert(self, key, val):
        """!
        push element if val is not queue, if not queue
        """
        index = self.index(val)
        if index == -1:
            self.push(key, val)
        else:
            self.queue[index] = (key, val)
        self.sort()

    def min(self):
        if self.is_min:
            return self.queue.pop(0)
        else:
            return self.queue.pop()

    def max(self):
        if self.is_min:
            return self.queue.pop()
        else:
            return self.queue.pop(0)

    def key(self, v):
        """!
        """
        for k, val in self.queue:
            if val == v:
                return k
        raise ValueError("value not in queue: " + str(v))

    def values(self, k):
        """!
        """
        return set([v for key, v in self.queue if key == k])

    def _range(self, mn=float("-inf"), mx=float("inf")):
        """!
        extract a range of values from priority queue

        \param mn bottom excluded range
        \param mx top excluded range
        """
        lst = []
        for i, (key, val) in enumerate(self.queue):
            if mn < key and key < mx:
                lst.append((i, key, val))

        return lst

    def index_range(self, mn=float("-inf"), mx=float("inf")):
        """!
        """
        return [t[0] for t in self._range(mn, mx)]

    def value_range(self, mn=float("-inf"), mx=float("inf")):
        """!
        """
        return [t[2] for t in self._range(mn, mx)]

    def key_range(self, mn=float("-inf"), mx=float("inf")):
        """!
        """
        return [t[1] for t in self._range(mn, mx)]

    def choice(self):
        """!
        """
        random_index = rchoice(range(len(self.queue)))
        return self.queue.pop(random_index)

    def get(self, i: int):
        """!
        """
        if len(self.queue) > i:
            return self.queue.pop(i)
        raise IndexError("argument out of bounds: " + str(i))

    def __len__(self):
        return len(self.queue)

    def __contains__(self, v):
        for key, val in self.queue:
            if val == v:
                return True
        return False

    def __str__(self):
        """!
        """
        return " ".join([str(t) for t in self.queue])
