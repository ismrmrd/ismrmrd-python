

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


class ChannelMaskMixin(object):
    """Mixin providing channel mask helpers for structs with a channel_mask field.

    channel_mask is uint64[16], supporting up to 1024 channels.
    Channel N lives in word N // 64, bit position N % 64.
    """

    _MAX_CHANNELS = 1024

    def _check_channel_id(self, channel_id):
        if not (0 <= channel_id < self._MAX_CHANNELS):
            raise ValueError(f"channel_id {channel_id} is out of range [0, {self._MAX_CHANNELS})")

    def isChannelActive(self, channel_id):
        self._check_channel_id(channel_id)
        word, bit = divmod(channel_id, 64)
        return bool(self.channel_mask[word] & (1 << bit))

    def setChannelActive(self, channel_id):
        self._check_channel_id(channel_id)
        word, bit = divmod(channel_id, 64)
        self.channel_mask[word] |= (1 << bit)

    def setChannelNotActive(self, channel_id):
        self._check_channel_id(channel_id)
        word, bit = divmod(channel_id, 64)
        self.channel_mask[word] &= ~(1 << bit)

    def setAllChannelsNotActive(self):
        for i in range(len(self.channel_mask)):
            self.channel_mask[i] = 0

