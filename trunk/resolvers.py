#
import sys

def defaultResolver(modules = True, **kwargs):
    globalsDict = dict(sys._getframe(2).f_globals)
    localsDict = dict(sys._getframe(2).f_locals)
    if kwargs:
        localsDict.update(kwargs)
    return dictResolver(globalsDict, modules, **localsDict)
    
def dictResolver(globalsDict, modules=True, **kwargs):
    localsDict = dict(kwargs)
    if localsDict:
        if modules:
            def resolver(name):
                try:
                    return globalsDict[name]
                except: pass
                try:
                    return localsDict[name]
                except: pass
                return sys.modules[name]
            return resolver
        else:
            def resolver(name):
                try:
                    return globalsDict[name]
                except: pass
                return localsDict[name]
            return resolver
    else:
        if modules:
            def resolver(name):
                try:
                    return globalsDict[name]
                except: pass
                return sys.modules[name]
            return resolver
        else:
            def resolver(name):
                try:
                    return globalsDict[name]
                except: pass
            return resolver

def customResolver(nameResolver, modules=True, **kwargs):
    localsDict = dict(kwargs)
    if localsDict:
        if modules:
            def resolver(name):
                try:
                    return nameResolver(name)
                except: pass
                try:
                    return localsDict[name]
                except: pass
                return sys.modules[name]
            return resolver
        else:
            def resolver(name):
                try:
                    return nameResolver(name)
                except: pass
                try:
                    return localsDict[name]
                except: pass
            return resolver
    else:
        if modules:
            def resolver(name):
                return nameResolver(name)
                return sys.modules[name]
            return resolver
        else:
            def resolver(name):
                return nameResolver(name)
            return resolver
