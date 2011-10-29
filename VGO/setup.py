"""
setup.py - script for building VGO executable package

Usage:
    % python setup.py py2exe
    % python setup.py py2app
"""
from distutils.core import setup
try:
    #http://www.py2exe.org/index.cgi/Tutorial
    import py2exe
    setup(windows=[{"script" : "main.py"}], options={"py2exe" : {"includes" : ["sip", "PyQt4._qt"]}}
        )
except ImportError:
    try:
        #http://undefined.org/python/py2app.html#py2app-documentation
        import py2app
        setup(app=['main.py'],)
    except ImportError:
        print "Neither py2app or py2exe is installed"
