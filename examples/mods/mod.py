from biwako import bin


class FineTune(bin.PackedStructure):
    Reserved(size=4)
    value = bin.Integer(size=4)


class SampleLength(bin.PositiveInteger):
    def to_python(self, value):
        return value * 2
    
    def to_bytes(self, value):
        return int(value / 2)


class Sample(bin.Structure):
    name = bin.FixedLengthString(size=22)
    size = SampleLength(size=2)
    finetune = bin.SubStructure(FineTune)
    volume = bin.PositiveInteger(size=1)
    loop_start = SampleLength(size=2, default_value=0)
    loop_length = SampleLength(size=2, default_value=0)
    
    @property
    def loop_end(self):
        return self.loop_start + self.loop_length
    
    @property
    def data(self):
        index = self.get_parent().samples.index(self)
        return self.get_parent().sample_data[index]
    
    def __unicode__(self):
        return self.name


class Note(bin.PackedStructure):
    sample_hi = bin.PositiveInteger(size=4)
    period = bin.PositiveInteger(size=12)
    sample_lo = bin.PositiveInteger(size=4)
    effect = bin.PositiveInteger(size=12)
    
    @property
    def sample(self):
        index = self.sample_hi << 4 + self.sample_lo
        return self.get_parent().samples[index]
    
    @sample.setter
    def sample(self, sample):
        index = self.get_parent().samples.index(sample)
        self.sample_hi = index >> 4
        self.sample_lo = index & 0xF


class Row(bin.Structure):
    notes = bin.List(Note, size=lambda self: self.get_parent().channels)
    
    def __iter__(self):
        return iter(self.rows)


class Pattern(bin.Structure):
    rows = bin.List(Row, size=64)
    
    def __iter__(self):
        return iter(self.rows)


class MOD(bin.File):
    channels = 4
    
    title = bin.FixedLengthString(size=20)
    samples = bin.List(Sample, size=15)
    order_count = bin.PositiveInteger(size=1)
    restart_position = bin.PositiveInteger(size=1)
    pattern_order = bin.List(bin.PositiveInteger(size=1), size=128)
    marker = bin.FixedString('M.K.')
    patterns = bin.List(Pattern, size=lambda self: max(self.pattern_order) + 1)
    sample_data = bin.ByteString(size=bin.REMAINDER)
    
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
    
    class Options:
        endianness = bin.BigEndian


if __name__ == '__main__':
    for format in (MOD,):
        track = format(open(sys.argv[1], 'rb'))
        print '%s: %s' % (format.__name__, track.title)

