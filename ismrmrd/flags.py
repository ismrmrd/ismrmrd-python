

class FlagsMixin(object):

    def clearAllFlags(self):
        self.clear_all_flags()

    def isFlagSet(self, flag):
        return self.is_flag_set(flag)

    def setFlag(self, flag):
        self.set_flag(flag)

    def clearFlag(self, flag):
        self.clear_flag(flag)

    def clear_all_flags(self):
        self.flags = 0

    def is_flag_set(self, flag):
        return bool(self.flags & (1 << (flag - 1)))

    def set_flag(self, flag):
        self.flags |= (1 << (flag - 1))

    def clear_flag(self, flag):
        self.flags &= ~(1 << (flag - 1))

