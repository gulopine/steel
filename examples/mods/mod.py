import steel
from steel import bits


class FineTune(bits.Structure):
    bits.Reserved(size=4)
    value = bits.Integer(size=4)


class SampleLength(bits.Integer):
    def encode(self, value):
        return int(value / 2)

    def decode(self, value):
        return value * 2
    

class Sample(steel.Structure):
    name = steel.String(size=22, encoding='ascii')
    size = SampleLength(size=2)
    finetune = steel.SubStructure(FineTune)
    volume = steel.Integer(size=1)
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


class Note(bits.Structure):
    sample_hi = bits.Integer(size=4)
    period = bits.Integer(size=12)
    sample_lo = bits.Integer(size=4)
    effect = bits.Integer(size=12)
    
    @property
    def sample(self):
        index = self.sample_hi << 4 + self.sample_lo
        return self.get_parent().samples[index]
    
    @sample.setter
    def sample(self, sample):
        index = self.get_parent().samples.index(sample)
        self.sample_hi = index >> 4
        self.sample_lo = index & 0xF


class Row(steel.Structure):
    notes = steel.List(Note, size=lambda self: self.get_parent().channels)
    
    def __iter__(self):
        return iter(self.rows)


class Pattern(steel.Structure):
    rows = steel.List(Row, size=64)
    
    def __iter__(self):
        return iter(self.rows)


class MOD(steel.Structure, endianness=steel.BigEndian):
    channels = 4
    
    title = steel.String(size=20, encoding='ascii')
    samples = steel.List(Sample, size=15)
    order_count = steel.Integer(size=1)
    restart_position = steel.Integer(size=1)
    pattern_order = steel.List(steel.Integer(size=1), size=128)
    marker = steel.FixedString('M.K.')
    patterns = steel.List(Pattern, size=lambda self: max(self.pattern_order) + 1)
    sample_data = steel.Bytes(size=steel.Remainder)
    
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

