class CopyDiff(object):
    """Base class providing copy and diff functions"""

    def copy(self, **kwargs):
        copy = self.blank(**kwargs)
        copy.copy_from(self)
        return copy

    def copy_from(self, other):
        """Copies changes from `other` to this object."""
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
                self.add_child(ochild.copy())

    def diff(self, new, prefix=[]):
        """
        Returns a dict representing the differences between this mod and `new`.

        Output is in the following format:
        {
            // scalar for simple fields (all except children)
            '<field name>': {'type': 'scalar', 'old': '<old value>', 'new': '<new value>'}
            'children': {
                'type': 'dict',
                'added': [<refs to added objects>],
                'removed': [<refs to removed objects>],
                'changed': [{
                    'old': <ref to old obj>,
                    'new': <ref to new obj>,
                    'changes': {<dict in this format for diff between old and new>}
                }]
            }
        }
        """
        diff = {}
        for f in self.copydiff_fields():
            a = getattr(self, f)
            b = getattr(new, f)
            if a != b:
                diff[f] = {'type': 'scalar', 'old': a, 'new': b}
        # List removed children
        diff['children'] = {'type': 'dict', 'added': [], 'removed': [], 'changed': []}
        for schild in self.get_children():
            if not any(map(lambda n: n.same_as(schild), new.get_children())):
                diff['children']['removed'].append(schild)
        # List added and changed children
        for nchild in new.get_children():
            # Find a matching child in this object
            schild = next(filter(lambda s: nchild.same_as(s), self.get_children()), None)
            if schild:
                diff['children']['changed'].append({
                    'old': schild,
                    'new': nchild,
                    'changes': schild.diff(nchild),
                })
            else:
                diff['children']['added'].append(nchild)

        return diff

    def blank(self, **kwargs):
        """Creates an "empty" instance of this object"""
        raise NotImplementedError
    def copydiff_fields(self):
        """Returns a list of fields to be copied or diffed"""
        return []
    def get_children(self): raise NotImplementedError
    def add_child(self, ch): raise NotImplementedError
    def rm_child(self, ch): raise NotImplementedError

