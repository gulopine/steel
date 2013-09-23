import steel
from steel import bits


class Sample(steel.Structure):
    title = steel.String(size=13, encoding='ascii')
    size = steel.Integer(size=4)
    loop_start = steel.Integer(size=4, default=0)
    loop_end = steel.Integer(size=4, default=0xFFFFF)
    
    @property
    def data(self):
        index = self.get_parent().samples.index(self)
        return self.get_parent().sample_data[index]
    
    def __unicode__(self):
        return self.title


class Note(bits.Structure):
    pitch = bits.Integer(size=6)
    sample = bits.Integer(size=6)
    volume = bits.Integer(size=4)
    command = bits.Integer(size=4)
    command_value = bits.Integer(size=4)
    
    @sample.getter
    def sample(self, index):
        return self.get_parent().samples[index]

    @sample.setter
    def sample(self, sample):
        return self.get_parent().samples.index(sample)


class Row(steel.Structure):
    notes = steel.List(Note, size=8)
    
    def __iter__(self):
        return iter(self.notes)


class Pattern(steel.Structure):
    rows = steel.List(Row, size=64)
    
    def __iter__(self):
        return iter(self.rows)


class _669(steel.Structure, endianness=steel.LittleEndian):
    marker = steel.FixedString('if')
    message = steel.List(steel.String(size=36, encoding='ascii', padding=' '), size=3)
    sample_count = steel.Integer(size=1, max_value=64)
    pattern_count = steel.Integer(size=1, max_value=128)
    restart_position = steel.Integer(size=1)
    pattern_order = steel.List(steel.Integer(size=1, max_value=128), size=128)
    pattern_tempos = steel.List(steel.Integer(size=1), size=128)
    pattern_breaks = steel.List(steel.Integer(size=1), size=128)
    samples = steel.List(Sample, size=sample_count)
    patterns = steel.List(Pattern, size=pattern_count)
    sample_data = steel.ByteString(size=steel.REMAINDER)
    
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
        return self.message[0]
    

if __name__ == '__main__':
    track = _669(open(sys.argv[1], 'rb'))
    for line in track.message:
        print(line)
