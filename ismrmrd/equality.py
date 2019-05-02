
import ctypes


def compare(this, other, attribute):

    a = getattr(this, attribute)
    b = getattr(other, attribute)

    if isinstance(a, ctypes.Array):
        return a[:] == b[:]
    return a == b


class EqualityMixin:
    def __eq__(self, other):
        try:
            return all(compare(self, other, field) for field, _ in self._fields_)
        except:
            return False
