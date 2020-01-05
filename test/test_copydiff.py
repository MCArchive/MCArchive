import pytest

from mcarch.util.copydiff import CopyDiff

class ParentObj(CopyDiff):
    def __init__(self, id, a, b, c, children):
        self.id = id
        self.a = a
        self.b = b
        self.c = c
        self.children = children

    def copydiff_fields(self): return ['a', 'b', 'c']

    def blank(self, **kwargs): TestObj(**kwargs)
    def blank_child(self, **kwargs): ChildObj(**kwargs)
    def get_children(self): return self.children
    def add_child(self, ch): self.children.append(ch)
    def rm_child(self, ch): self.children.remove(ch)
    def same_as(self, other):
        return self.id == other.id

class ChildObj(CopyDiff):
    def __init__(self, id, a, b):
        self.id = id
        self.a = a
        self.b = b

    def copydiff_fields(self): return ['a', 'b']

    def blank(self, **kwargs): ChildObj(**kwargs)
    def blank_child(self, **kwargs): None
    def same_as(self, other):
        return self.id == other.id
    def get_children(self): return []


def test_diff():
    old = ParentObj(1, "foo", "bar", 42, [])
    new = ParentObj(1, "foo", "baz", 27, [])

    diff = old.diff(new)
    print('Diff: {}'.format(diff))
    assert diff.get('a') == None
    assert diff.get('b').old == old.b
    assert diff.get('b').new == new.b
    assert diff.get('c').old == old.c
    assert diff.get('c').new == new.c

def test_diff_add_child():
    old = ParentObj(1, "foo", "bar", 42, [
    ])
    new = ParentObj(1, "foo", "bah", 42, [
        ChildObj(1, 69, 420)
    ])

    diff = old.diff(new)
    print('Diff: {}'.format(diff))
    assert diff.children.removed == old.children

def test_diff_rm_child():
    old = ParentObj(1, "foo", "bar", 42, [
        ChildObj(1, 69, 420)
    ])
    new = ParentObj(1, "foo", "bah", 42, [ ])

    diff = old.diff(new)
    print('Diff: {}'.format(diff))
    assert diff.children.removed == old.children

def test_diff_change_child():
    old = ParentObj(1, "foo", "bar", 42, [
        ChildObj(1, 69, 420)
    ])
    new = ParentObj(1, "foo", "bah", 42, [
        ChildObj(1, 1337, 420)
    ])

    diff = old.diff(new)
    print('Diff: {}'.format(diff))
    assert diff.children.changed[0].get('a').old == 69
    assert diff.children.changed[0].get('a').new == 1337

