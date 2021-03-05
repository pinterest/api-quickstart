import sys

MODULE = 0
FUNCTION = 1
VALUE = 2

def patch(patches):
    print('monkey_patch')
    originals = [] # contains unpatched values
    for patch in patches:
        module = patch[MODULE]
        function = patch[FUNCTION]
        # remember existing value
        originals.append((module, function, getattr(sys.modules[module], function)))
        # set patched value
        print('patching ' + module + '[' + function + '] = ' + str(patch[VALUE]))
        setattr(sys.modules[module], function, patch[VALUE])
    return originals
