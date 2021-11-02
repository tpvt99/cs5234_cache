from collections import OrderedDict
import random


class UpdatePolicy:

    def __init__(self, n: int):
        self.n = n

    def change_n(self, delta: int):
        self.n += delta

    def is_full(self) -> bool:
        raise NotImplementedError 

    def update_access(self, i: int):
        raise NotImplementedError 

    def add_in(self, new_i: int):
        raise NotImplementedError

    def remove_one(self) -> int:
        raise NotImplementedError


class LRUPolicy(UpdatePolicy):

    def __init__(self, n: int):
        super().__init__(n)
        self.ordering = OrderedDict()

    def is_full(self):
        return len(self.ordering) >= self.n
    
    def update_access(self, i: int):
        self.ordering.move_to_end(i, last=True)

    def add_in(self, new_i: int):
        assert len(self.ordering) < self.n
        self.ordering[new_i] = None

    def remove_one(self):
        k, _ = self.ordering.popitem(last=False)
        return k


class LFUPolicy(UpdatePolicy):

    def __init__(self, n: int):
        super().__init__(n)
        self.ordering = dict()

    def is_full(self):
        return len(self.ordering) >= self.n
    
    def update_access(self, i: int):
        self.ordering[i] += 1

    def add_in(self, new_i: int):
        assert len(self.ordering) < self.n
        self.ordering[new_i] = 0

    def remove_one(self):
        k_remove = 0
        v_remove = float('inf')
        for k, v in self.ordering.items():
            if v < v_remove:
                k_remove = k
                v_remove = v
        self.ordering.pop(k_remove)
        return k_remove


class FIFOPolicy(UpdatePolicy):
    
    def __init__(self, n: int):
        super().__init__(n)
        self.ordering = OrderedDict()

    def is_full(self):
        return len(self.ordering) >= self.n
    
    def update_access(self, i: int):
        pass

    def add_in(self, new_i: int):
        assert len(self.ordering) < self.n
        self.ordering[new_i] = None

    def remove_one(self):
        k, _ = self.ordering.popitem(last=False)
        return k


class RandomPolicy(UpdatePolicy):
    # based on https://stackoverflow.com/questions/15993447/python-data-structure-for-efficient-add-remove-and-random-choice

    def __init__(self, n: int):
        super().__init__(n)
        self.item_to_position = {}
        self.items = []

    def is_full(self):
        return len(self.items) >= self.n
    
    def update_access(self, i: int):
        pass

    def add_in(self, new_i: int):
        assert len(self.items) < self.n
        self.items.append(new_i)
        self.item_to_position[new_i] = len(self.items) - 1

    def remove_one(self):
        rand_i = random.choice(self.items)
        position = self.item_to_position.pop(rand_i)
        last_item = self.items.pop()
        if position != len(self.items):
            self.items[position] = last_item
            self.item_to_position[last_item] = position
        return rand_i
