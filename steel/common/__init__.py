import collections
import threading

# Temporary storage
data = threading.local()
data.field_options = {}
data.field_stack = [[]]
data.instance_stack = collections.defaultdict(list)

from steel.common.meta import *
from steel.common.fields import *

# Special object used to instruct the reader to continue to the end of the file
def Remainder(obj):
    return -1


