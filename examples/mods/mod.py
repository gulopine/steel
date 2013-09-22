from steel import bit, byte, common


class FineTune(bit.Structure):
    bit.Reserved(size=4)
    value = bit.Integer(size=4)


class SampleLength(bit.Integer):
    def encode(self, value):
        return int(value / 2)

    def decode(self, value):
        return value * 2
    

class Sample(byte.Structure):
    name = byte.String(size=22, encoding='ascii')
    size = SampleLength(size=2)
    finetune = common.SubStructure(FineTune)
    volume = byte.Integer(size=1)
    loop_start = SampleLength(size=2, default=0)
    loop_length = SampleLength(size=2, default=0)
    
    @property
    def loop_end(self):
        return self.loop_start + self.loop_length
    
    @property
    def data(self):
        index = self.get_parent().samples.index(self)
        return self.get_parent().sample_data[index]
    
    def __unicode__(self):
        return self.name


class Note(bit.Structure):
    sample_hi = bit.Integer(size=4)
    period = bit.Integer(size=12)
    sample_lo = bit.Integer(size=4)
    effect = bit.Integer(size=12)
    
    @property
    def sample(self):
        index = self.sample_hi << 4 + self.sample_lo
        return self.get_parent().samples[index]
    
    @sample.setter
    def sample(self, sample):
        index = self.get_parent().samples.index(sample)
        self.sample_hi = index >> 4
        self.sample_lo = index & 0xF


class Row(byte.Structure):
    notes = common.List(Note, size=lambda self: self.get_parent().channels)
    
    def __iter__(self):
        return iter(self.rows)


class Pattern(byte.Structure):
    rows = common.List(Row, size=64)
    
    def __iter__(self):
        return iter(self.rows)


class MOD(byte.Structure, endianness=byte.BigEndian):
    channels = 4
    
    title = byte.String(size=20, encoding='ascii')
    samples = common.List(Sample, size=15)
    order_count = byte.Integer(size=1)
    restart_position = byte.Integer(size=1)
    pattern_order = common.List(byte.Integer(size=1), size=128)
    marker = byte.FixedString('M.K.')
    patterns = common.List(Pattern, size=lambda self: max(self.pattern_order) + 1)
    sample_data = byte.Bytes(size=common.Remainder)
    
    @property
    def pattern_count(self):
        return max(self.order) + 1
    
    @sample_data.getter
    def sample_data(self, data):
        offset = 0
        output = []
        for info in self.samples:
            output.append(data[offset:offset + info.size])
            offset += info.size
        return output
    
    @sample_data.setter
    def sample_data(self, data_list):
        return ''.join(data_list)
    
    def __iter__(self):
        for index in self.pattern_order:
            yield self.patterns[index]
    
    def __unicode__(self):
        return self.title
    

if __name__ == '__main__':
    for format in (MOD,):
        track = format(open(sys.argv[1], 'rb'))
        print('%s: %s' % (format.__name__, track.title))

