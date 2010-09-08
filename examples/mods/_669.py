from biwako import bin


class Sample(bin.Structure):
    title = bin.FixedLengthString(size=13, encoding='ascii', padding='\x00')
    size = bin.PositiveInteger(size=4)
    loop_start = bin.PositiveInteger(size=4, default_value=0)
    loop_end = bin.PositiveInteger(size=4, default_value=0xFFFFF)
    
    @property
    def data(self):
        index = self.get_parent().samples.index(self)
        return self.get_parent().sample_data[index]
    
    def __unicode__(self):
        return self.title


class Note(bin.PackedStructure):
    pitch = bin.PositiveInteger(size=6)
    sample = bin.PositiveInteger(size=6)
    volume = bin.PositiveInteger(size=4)
    command = bin.PositiveInteger(size=4)
    command_value = bin.PositiveInteger(size=4)
    
    @sample.getter
    def sample(self, index):
        return self.get_parent().samples[index]

    @sample.setter
    def sample(self, sample):
        return self.get_parent().samples.index(sample)


class Row(bin.Structure):
    notes = bin.List(Note, size=8)
    
    def __iter__(self):
        return iter(self.notes)


class Pattern(bin.Structure):
    rows = bin.List(Row, size=64)
    
    def __iter__(self):
        return iter(self.rows)


class _669(bin.File):
    marker = bin.FixedString('if')
    message = bin.String(size=108, encoding='ascii', padding=' ')
    sample_count = bin.PositiveInteger(size=1, max_value=64)
    pattern_count = bin.PositiveInteger(size=1, max_value=128)
    restart_position = bin.PositiveInteger(size=1)
    pattern_order = bin.List(bin.PositiveInteger(size=1, max_value=128), size=128)
    pattern_tempos = bin.List(bin.PositiveInteger(size=1), size=128)
    pattern_breaks = bin.List(bin.PositiveInteger(size=1), size=128)
    samples = bin.List(Sample, size=sample_count)
    patterns = bin.List(Pattern, size=pattern_count)
    sample_data = bin.ByteString(size=bin.REMAINDER)
    
    @message.getter
    def message(self, raw_message):
        padding = type(self).message.padding
        return [
            raw_message[0:36].strip(padding),
            raw_message[36:72].strip(padding),
            raw_message[72:108].strip(padding),
        ]
    
    @message.setter
    def message(self, message):
        padding = type(self).message.padding
        return ''.join(line.ljust(36, padding) for line in message)
    
    @sample_data.getter
    def sample_data(self, data):
        offset = 0
        output = []
        for info in self.samples:
            output.append(data[offset:offset + info.size])
        return output
    
    @sample_data.setter
    def sample_data(self, data_list):
        return ''.join(data_list)
    
    def __iter__(self):
        for index in self.pattern_order:
            yield self.patterns[index]
    
    def __unicode__(self):
        return self.message[0]
    
    class Options:
        endianness = bin.LittleEndian


if __name__ == '__main__':
    track = _669(open(sys.argv[1], 'rb'))
    for line in track.message:
        print line
