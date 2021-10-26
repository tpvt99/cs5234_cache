from collections import OrderedDict


class UpdatePolicy:

    def __init__(self):
        pass

    def in_queue(self):
        raise NotImplementedError 

    def update_access(self, i: int):
        raise NotImplementedError 

    def add_in(self, new_i: int):
        raise NotImplementedError

    def remove_one(self):
        raise NotImplementedError


class LRUPolicy(UpdatePolicy):

    def __init__(self):
        super().__init__()
        self.ordering = OrderedDict()

    def in_queue(self):
        return len(self.ordering)
    
    def update_access(self, i: int):
        self.ordering.move_to_end(i, last=True)

    def add_in(self, new_i: int):
        self.ordering[new_i] = None

    def remove_one(self):
        k, _ = self.ordering.popitem(last=False)
        return k
