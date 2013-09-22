import collections
import threading

# Temporary storage
data = threading.local()
data.field_options = {}
data.field_stack = [[]]
data.instance_stack = collections.defaultdict(list)

from .meta import *
from .fields import *

# Special object used to instruct the reader to continue to the end of the file
def Remainder(obj):
    return -1


