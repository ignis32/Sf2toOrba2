 
import OrbaPreset.OrbaPreset as OrbaPreset
from typing import List, Optional
class TestClass:
    abc: str
    cda: str
    def __init__ (self):
        pass

obj = TestClass()

print(obj.__class__.__dict__)

print( hasattr(obj, 'abc'))
print( hasattr(obj, 'aaa'))


 

orba_preset =  OrbaPreset.PresetEntry()
print(orba_preset.__class__.__annotations__)

print( hasattr(obj, 'orba_preset'))
print( hasattr(obj, 'orba_preset'))