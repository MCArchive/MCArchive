class ObjDiff(object):
    """Represents a difference between two `CopyDiff` objects.

    Contains a list of `DiffField` objects that represent the changes to each
    field in the object.

    Also contains the `children` field which may be be a `ChildListField`.
    """
    def __init__(self, old, new, changes, children=None):
        self.old = old
        self.new = new
        self.changes = changes
        self.children = children

    def get(self, name):
        """Gets a scalar field with the given name."""
        for field in self.changes:
            if field.name == name: return field
        return None

    def is_empty(self):
        """Returns true if this diff contains no changes."""
        return len(self.changes) == 0 and \
            (not self.children or self.children.is_empty())

    def pretty(self, indent=0):
        """Turns this diff into a pretty printed string for debugging."""
        indentstr = "\t" * indent
        out = "{}Changes from {} to {}: ".format(indentstr, self.old, self.new)

        for ch in self.changes:
            if isinstance(ch, ScalarField):
                out += "\n{}{}: {} -> {}".format(indentstr, ch.name, ch.old, ch.new)

        if self.children:
            out += "\n{}Added Children: {}".format(indentstr, self.children.added)
            out += "\n{}Removed Children: {}".format(indentstr, self.children.added)
            out += "\n{}Changed Children:".format(indentstr)
            for ch in self.children.changed:
                out += "\n{}".format(ch.pretty(indent=indent+1))

        return out


class DiffField(object):
    """Represents a generic field in a diff."""
    def __init__(self, name):
        self.name = name

class ScalarField(DiffField):
    """Represents a change to a scalar field (i.e., not a list or dict)"""
    def __init__(self, name, old, new):
        super().__init__(name)
        self.new = new
        self.old = old

class ChildListField(DiffField):
    """Represents a change to a list of child objects whose changes are also tracked."""
    def __init__(self, name, added, removed, changed):
        super().__init__(name)
        self.added = added
        self.removed = removed
        self.changed = changed

    def is_empty(self):
        return len(self.changed) == 0 and len(self.added) == 0 and len(self.removed) == 0


class CopyDiff(object):
    """Base class providing copy and diff functions"""
    def copy(self, **kwargs):
        copy = self.blank(**kwargs)
        copy.copy_from(self)
        return copy

    def copy_from(self, other):
        """Copies changes from `other` to this object."""
        # copy the UUID from other so that we'll know later that this object was a copy of it.
        self.uuid = other.uuid
        # Copy changes to this object
        for f in self.copydiff_fields():
            setattr(self, f, getattr(other, f))
        # Remove children deleted in other
        for schild in self.get_children():
            if not any(map(lambda o: o.same_as(schild), other.get_children())):
                self.rm_child(schild)
        # Copy children and add new children to self
        for ochild in other.get_children():
            # Find a matching child in this object
            schild = next(filter(lambda s: ochild.same_as(s), self.get_children()), None)
            if schild:
                schild.copy_from(ochild)
            else:
                newchild = self.blank_child()
                newchild.copy_from(ochild)
                self.add_child(newchild)

    def diff(self, new, prefix=[]):
        """
        Returns a dict representing the differences between this mod and `new`.

        Return value is an `ObjDiff` representing the differences between the objects.

        Note: At the moment tracked children are always represented by a field
        called `children` and there can only be one. This can be fixed later,
        but it's not really needed at the moment.
        """
        changes = []

        for f in self.copydiff_fields():
            o = getattr(self, f)
            n = getattr(new, f)
            if o != n:
                changes.append(ScalarField(f, old=o, new=n))

        # List removed children
        added = []
        removed = []
        changed = []

        # List removed children.
        for schild in self.get_children():
            if not any(map(lambda n: n.same_as(schild), new.get_children())):
                removed.append(schild)

        # List added and changed children
        for nchild in new.get_children():
            # Find a matching child in the old object
            ochild = self.find_same_child(nchild)
            if ochild:
                chdiff = ochild.diff(nchild)
                if not chdiff.is_empty():
                    changed.append(chdiff)
            else:
                added.append(nchild)

        # If children changed, add a `ChildListField` to the diff.
        if len(added) > 0 or len(removed) > 0 or len(changed) > 0:
            children = ChildListField('children', added, removed, changed)
        else:
            children = None

        return ObjDiff(self, new, changes, children)

    def apply_diff(self, diff):
        """Applies the changes made in the given diff to this object and its children."""
        # Apply field changes.
        for field in self.copydiff_fields():
            change = diff.get(field)
            if change and isinstance(change, ScalarField):
                setattr(self, field, change.new)
        # Apply child changes
        if diff.children:
            # Add added children
            for ch in diff.children.added:
                newch = self.blank_child()
                newch.copy_from(ch)
                self.add_child(newch)
            # Remove removed children
            for ch in diff.children.removed:
                schild = self.find_same_child(ch)
                if schild: self.rm_child(schild)
            # Change changed children
            for ch in diff.children.changed:
                schild = self.find_same_child(ch.new)
                if schild: schild.apply_diff(ch)

    def blank(self, **kwargs):
        """Creates an "empty" instance of this object"""
        raise NotImplementedError
    def blank_child(self, **kwargs):
        """Creates an "empty" instance of a child of this object.
        None if this object can't have children"""
        return None
    def copydiff_fields(self):
        """Returns a list of fields to be copied or diffed"""
        return []
    def same_as(self, other):
        """Checks if this object is the "same" as another.

        Objects are the "same" if one is a copy of the other made with `copy_from` or `copy`.  """
        return self.uuid == other.uuid
    def get_children(self): raise NotImplementedError
    def add_child(self, ch): raise NotImplementedError
    def rm_child(self, ch): raise NotImplementedError

    def find_same_child(self, other):
        """Finds the first child in self that is `same_as` `other`.`"""
        return next(filter(lambda s: other.same_as(s), self.get_children()), None)

