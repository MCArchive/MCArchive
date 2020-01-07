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
    def __init__(self, id=None, a=None, b=None, c=None):
        self.id = id if id else 0
        self.a = a
        self.b = b
        self.c = c

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

def test_apply_diff():
    old = ParentObj(1, "foo", "bar", 42, [])
    new = ParentObj(1, "foo", "baz", 42, [])
    diff = old.diff(new)

    appto = ParentObj(1, "foo", "bar", 69, [])
    appto.apply_diff(diff)

    # a didn't change from old to new, or in appto, so it's untouched
    assert appto.a == "foo"
    # b changed from old to new, so it was changed in appto when the diff was applied
    assert appto.b == "baz"
    # c didn't change from old to new, so the different value in appto wasn't changed
    assert appto.c == 69

def test_apply_diff_child():
    old = ParentObj(1, "foo", "bar", 42, [
        ChildObj(1, 69, 420, "lol")
    ])
    new = ParentObj(1, "foo", "bar", 42, [
        ChildObj(1, 69, 1337, "lol")
    ])
    diff = old.diff(new)

    appto = ParentObj(1, "foo", "bar", 42, [
        ChildObj(1, 69, 420, "kek")
    ])
    appto.apply_diff(diff)

    # same deal for the child as the test above
    assert appto.children[0].a == 69
    assert appto.children[0].b == 1337
    assert appto.children[0].c == "kek"

def test_apply_diff_add_child():
    old = ParentObj(1, "foo", "bar", 42, [
        ChildObj(1, 69, 420, "lol"),
    ])
    new = ParentObj(1, "foo", "bar", 42, [
        ChildObj(1, 69, 420, "lol"),
        ChildObj(2, 27, 42, "kek"),
    ])
    diff = old.diff(new)

    appto = ParentObj(1, "foo", "bar", 42, [
        ChildObj(1, 69, 420, "lol"),
    ])
    appto.apply_diff(diff)

    assert len(appto.children) == 2

def test_apply_diff_rm_child():
    old = ParentObj(1, "foo", "bar", 42, [
        ChildObj(1, 69, 420, "lol"),
        ChildObj(2, 27, 42, "kek"),
    ])
    new = ParentObj(1, "foo", "bar", 42, [
        ChildObj(1, 69, 420, "lol"),
    ])
    diff = old.diff(new)

    appto = ParentObj(1, "foo", "bar", 42, [
        ChildObj(1, 69, 420, "lol"),
        ChildObj(2, 27, 42, "kek"),
    ])
    appto.apply_diff(diff)

    assert len(appto.children) == 1

