import sys
import builtins

from biwako import bin, common, args


class BitStructureMetaclass(common.DeclarativeMetaclass):
    @classmethod
    def __prepare__(cls, name, bases, **options):
        return super(BitStructureMetaclass, cls).__prepare__(name, bases, **options)


class Structure(bin.Structure, metaclass=BitStructureMetaclass):
    def __init__(self, *args, **kwargs):
        super(Structure, self).__init__(*args, **kwargs)
        self._bits_left = 0
        self._bit_buffer = 0

    def read(self, size=None):
        bit_buffer = self._bit_buffer
        if size > self._bits_left:
            # Read more bytes from the file
            read_size = int(((size - self._bits_left) + 7) / 8)
            field = bin.Integer(size=read_size)
            bytes = self._file.read(read_size)
            value = field.decode(bytes)
            bit_buffer = (bit_buffer << size) | value
            self._bits_left += read_size * 8
        self._bits_left -= size % 8
        bits = bit_buffer >> self._bits_left
        self._bit_buffer = bit_buffer & (1 << self._bits_left) - 1
        return bits

    def get_raw_bytes(self):
        output = b''
        bits_read = 0
        byte = 0
        for field in self.__class__._fields:
            value = getattr(self, field.name)
            if field.name not in self._raw_values:
                setattr(self, field.name, getattr(self, field.name))
            bits_read += field.size
            bits = self._raw_values[field.name]
            byte = (byte << field.size) + bits
            if bits_read > 8:
                byte >>= bits_read - (bits_read % 8)
                bits_read -= bits_read - (bits_read % 8)
            output += bytes([byte])
        return output


class Field(metaclass=common.DeclarativeFieldMetaclass):
    size = args.Argument(resolve_field=True)
    choices = args.Argument(default=())
    default = args.Argument(default=args.NotProvided)

    def __init__(self, label='', **kwargs):
        self.label = label

        for name, arg in self.arguments.items():
            if name in kwargs:
                value = kwargs.pop(name)
            elif arg.has_default:
                value = arg.default
            else:
                raise TypeError("The %s argument is required for %s fields" % (arg.name, self.__class__.__name__))
            setattr(self, name, value)
        if kwargs:
            raise TypeError("%s is not a valid argument for %s fields" % (list(kwargs.keys())[0], self.__class__.__name__))

        # Once the base values are all in place, arguments can be initialized properly
        for name, arg in self.arguments.items():
            setattr(self, name, arg.initialize(self, getattr(self, name)))

    def for_instance(self, instance):
        return self

    def resolve(self, instance):
        if self._parent is not None:
            instance = self._parent.resolve(instance)
        return getattr(instance, self.name)

    def read(self, obj):
        # If the size can be determined easily, read
        # that number of bytes and return it directly.
        if self.size is not None:
            return obj.read(self.size)

        # Otherwise, the field needs to supply its own
        # technique for determining how much data to read.
        raise NotImplementedError()

    def write(self, obj, value):
        # By default, this doesn't do much, but individual
        # fields can/should override it if necessary
        obj.write(value)

    def set_name(self, name):
        self.name = name
        label = self.label or name.replace('_', ' ')
        self.label = label.title()

    def attach_to_class(self, cls):
        cls._fields.append(self)

    def validate(self, obj, value):
        # This should raise a ValueError if the value is invalid
        # It should simply return without an error if it's valid

        # First, make sure the value can be encoded
        self.encode(value)

        # Then make sure it's a valid option, if applicable
        if self.choices and value not in set(v for v, desc in self.choices):
            raise ValueError("%r is not a valid choice" % value)

    def _extract(self, instance):
        try:
            return self.read(instance), None
        except FullyDecoded as obj:
            return obj.bytes, obj.value

    def read_value(self, file):
        try:
            bytes = self.read(file)
            value = self.decode(bytes)
            return bytes, value
        except FullyDecoded as obj:
            return obj.bytes, obj.value

    def __get__(self, instance, owner):
        if not instance:
            return self

        try:
            value = instance._extract(self)
        except IOError:
            if self.default is not args.NotProvided:
                return self.default
            raise AttributeError("Attribute %r has no data" % field.name)

        if self.name not in instance.__dict__:
            instance.__dict__[self.name] = self.decode(value)
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
        instance._raw_values[self.name] = self.encode(value)

    def __repr__(self):
        return '<%s: %s>' % (self.name, type(self).__name__)


class Integer(Field):
    size = args.Argument()
    signed = args.Argument(default=False)

    def encode(self, value):
        if value > (1 << self.size) - 1:
            raise ValueError("Value is large for this field.")
        return value & ((1 << self.size) - 1)

    def decode(self, value):
        if value > (1 << self.size) - 1:
            raise ValueError("Value is large for this field.")
        return value & ((1 << self.size) - 1)

    def __add__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: a + b)
    __radd__ = __add__

    def __sub__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: a - b)

    def __rsub__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: b - a)

    def __mul__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: a * b)
    __rmul__ = __mul__

    def __pow__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: a ** b)

    def __rpow__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: b ** a)

    def __truediv__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: a / b)

    def __rtruediv__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: b / a)

    def __floordiv__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: a // b)

    def __rfloordiv__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: b // a)

    def __divmod__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: divmod(a, b))

    def __rdivmod__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: divmod(b, a))

    def __and__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: a & b)
    __rand__ = __and__

    def __or__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: a | b)
    __ror__ = __or__

    def __xor__(self, other):
        return bin.CalculatedValue(self, other, lambda a, b: a ^ b)
    __rxor__ = __xor__


class FixedInteger(Integer):
    def __init__(self, value, *args, **kwargs):
        super(FixedInteger, self).__init__(*args, signed=value < 0, **kwargs)
        self.decoded_value = value
        self.encoded_value = super(FixedInteger, self).encode(value)

    def encode(self, value):
        if value != self.decoded_value:
            raise ValueError('Expected %r, got %r.' % (self.decoded_value, value))
        return self.encoded_value

    def decode(self, value):
        if value != self.encoded_value:
            raise ValueError('Expected %r, got %r.' % (self.encoded_value, value))
        return self.decoded_value


class Flag(Integer):
    size = args.Override(default=1)

    def encode(self, value):
        return int(super(Flag, self).encode(value))

    def decode(self, value):
        return bool(super(Flag, self).decode(value))


class Reserved(Field):
    default = args.Override(default=None)

    def __init__(self, *args, **kwargs):
        super(Reserved, self).__init__(*args, **kwargs)

        # Hack to add the reserved field to the class without
        # having to explicitly give it a (likely useless) name
        frame = sys._getframe(2)
        locals = frame.f_locals
        locals[self.get_available_name(locals.keys())] = self

    def get_available_name(self, locals):
        i = 0
        while True:
            name = '_reserved_%s' % i
            if name not in locals:
                return name
            i += 1

    def set_name(self, name):
        if hasattr(self, 'name'):
            raise TypeError('Reserved fields must not be given an attribute name')
        super(Reserved, self).set_name(name)

    def encode(self, value):
        return 2 ** self.size - 1

    def decode(self, value):
        return None


