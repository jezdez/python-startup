"""
My Python startup file, carefully gathered from different sources (see below)

Get code from Github::

    git clone https://github.com/jezdez/python-startup.git ~/.python

Put this in your shell profile::

    export PYTHONSTARTUP=$HOME/.python/startup.py

In case you haven't saved these files in $HOME/.python make sure to set
PYTHONUSERDIR approppriately, too::

    export PYTHONUSERDIR=/path/to/dir

"""
# python-startup.py
# Author: Nathan Gray, based on interactive.py by Robin Friedrich and an 
#           evil innate desire to customize things.
# E-Mail: n8gray@caltech.edu
#
# Version: 0.6 

# These modules are always nice to have in the namespace

############################################################################
# Below this is Robin Friedrich's interactive.py with some edits to decrease 
# namespace pollution and change the help functionality
# NG
#
# Also enhanced 'which' to return filename/lineno
# Patch from Stephan Fiedler to allow multiple args to ls variants
# NG 10/21/01  --  Corrected a bug in _glob
#
########################### interactive.py ###########################
#  """Functions for doing shellish things in Python interactive mode.
#
#     Meant to be imported at startup via environment:
#       setenv PYTHONSTARTUP $HOME/easy.py
#       or
#       export PYTHONSTARTUP=$HOME/easy.py
#
#     - Robin Friedrich
#  """


import functools
import glob
import os
import shutil
import subprocess
import sys
import time
import types

try:
    from pydoc import help
except ImportError:
    def help(*objects):
        """Print doc strings for object(s).
        Usage:  >>> help(object, [obj2, objN])  (brackets mean [optional] argument)
        """
        if len(objects) == 0:
            help(help)
            return
        for obj in objects:
            try:
                print '****', obj.__name__ , '****'
                print obj.__doc__
            except AttributeError:
                print `obj`, 'has no __doc__ attribute'
                print

try:
    from collections import defaultdict
except ImportError:
    pass

home = os.path.expandvars('$HOME')
user_dir = os.path.join(home, os.environ.get("PYTHONUSERDIR", ".python"))
sys.path.append(user_dir)

##### Some settings you may want to change #####
# Define the editor used by the edit() function. Try to use the editor
# defined in the Unix environment, or default to vi if not set.
# (patch due to Stephan Fiedler)
#
# %(lineno)s gets replaced by the line number.  Ditto %(fname)s the filename
EDITOR = os.environ.get('EDITOR', 'emacs')
editorbase = EDITOR.split()[0]
if editorbase in ['nedit', 'nc', 'ncl', 'emacs', 'emacsclient', 'xemacs'] :
    # We know these editors supoprt a linenumber argument
    EDITOR = EDITOR + ' +%(lineno)s %(fname)s &'
elif editorbase in ['vi', 'vim', 'jed']:
    # Don't want to run vi in the background!
    # If your editor requires a terminal (e.g. joe) use this as a template
    EDITOR = 'xterm -e ' + EDITOR + ' +%(lineno)s %(fname)s &'
else:
    # Guess that the editor only supports the filename
    EDITOR = EDITOR + ' %(fname)s &'
del editorbase

# The place to store your command history between sessions
histfile = os.path.join(user_dir, "history")

# Functions automatically added to the builtins namespace so that you can
# use them in the debugger and other unusual environments
autobuiltins = ['edit', 'which', 'ls', 'cd', 'mv', 'cp', 'rm', 'help', 'rmdir',
                'ln', 'pwd', 'pushd', 'popd', 'env', 'mkdir']

##### Now set up the interactive features that I like #####

# Colorize the prompts if possible (This is probably non-portable muck)
# Thanks to Stephan Fiedler for the fix!
if os.environ[ 'TERM' ] in [ 'xterm', 'vt100' ]:
    pre = chr(1) + "\033[1;32m" + chr(2) # Turn the text green
    suf = chr(1) + "\033[0m" + chr(2) # Reset to normal
    sys.ps1 = pre + ">>>" + suf + " "
    sys.ps2 = pre + "..." + suf + " "
    del pre, suf
    try:
        # Set up colorized tracebacks
        # Make sure to do this *before* installing LazyPython
        import ultraTB
        sys.excepthook = ultraTB.ColorTB()
    except ImportError:
        pass

# LazyPython only works for Python versions 2.1 and above
try:
    # Try to use LazyPython
    from LazyPython import LazyPython
    sys.excepthook = LazyPython()
except ImportError:
    pass
    
# Pretty-print at the command prompt for more readable dicts and lists.
from pprint import pprint
import __builtin__
def myhook(value, show=pprint, bltin=__builtin__):
    if value is not None:
        bltin._ = value
        show(value)
sys.displayhook = myhook
del __builtin__

try:
    # Try to set up command history completion/saving/reloading
    import readline, atexit, rlcompleter
    readline.parse_and_bind('tab: complete')
    try:
        readline.read_history_file(histfile)
    except IOError:
        pass  # It doesn't exist yet.

    def savehist():
        try:
            global histfile
            readline.write_history_file(histfile)
        except:
            print 'Unable to save Python command history'
    atexit.register(savehist)
    del atexit
except ImportError:
    pass

##### Make reload work recursively #####
try:
    import __builtin__, deep_reload
    __builtin__.reload = deep_reload.reload
    del __builtin__, deep_reload
except ImportError:
    pass

# Make an "edit" command that sends you to the right file *and line number*
# to edit a module, class, method, or function!
# Note that this relies on my enhanced version of which().
def edit(object, editor=EDITOR):
    """Edit the source file from which a module, class, method, or function 
    was imported.
    Usage:  >>> edit(mysteryObject)
    """
    
    if type(object) is type(""):
        fname = object; lineno = 1
        print editor % locals()
        subprocess.Popen(editor % locals(), shell=True)
        return
    
    ret = which(object)
    if not ret: 
        print "Can't edit that!"
        return
    fname, lineno = ret
    if fname[-4:] == '.pyc' or fname[-4:] == '.pyo':
        fname = fname[:-1]
    print editor % locals()
    subprocess.Popen(editor % locals(), shell=True)

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print("%s time: %.5f" % (func.__name__, end - start))
        return res
    return wrapper

def reimport(mod, locals=None):
    if isinstance(mod, str):
        modname = mod
    else:
        modname = mod.__name__
    sys.modules[modname] = None
    del sys.modules[modname]
    new_mod = __import__(modname)
    if locals is not None:
        locals[modname] = new_mod
    return new_mod


def _glob(filenames):
    """Expand a filename or sequence of filenames with possible
    shell metacharacters to a list of valid filenames.
    Ex:  _glob(('*.py*',)) == ['able.py','baker.py','charlie.py']
    """
    if type(filenames) is types.StringType:
        return glob.glob(filenames)
    flist = []
    for filename in filenames:
        globbed = glob.glob(filename)
        if globbed:
            for file in globbed:
                flist.append(file)
        else:
            flist.append(filename)
    return flist

def _expandpath(d):
    """Convert a relative path to an absolute path.
    """
    return os.path.join(os.getcwd(), os.path.expandvars(d))

def _ls(options, *files):
    """
    _ls(options, ['fname', ...'])

    Lists the given filenames, or the current directory if none are
    given, with the given options, which should be a string like '-lF'.
    """
    if len(files) == 0 :
        args = os.curdir
    else :
        args = ' '.join(files)
    subprocess.Popen('ls %s %s' % (options, args), shell=True)

def ls(*files):
    """Same as 'ls -aF'
    Usage:  >>> ls(['dirname', ...])   (brackets mean [optional]
argument)
    """
    _ls('-aF', *files)

def ll(*files):
    """Same as 'ls -alF'
    Usage:  >>> ll(['dirname', ...])   (brackets mean [optional]
argument)
    """
    _ls('-alF', *files)

def lr(*files):
    """Recursive listing. same as 'ls -aRF'
    Usage:  >>> lr(['dirname', ...])   (brackets mean [optional]
argument)
    """
    _ls('-aRF', *files)

mkdir = os.mkdir

def rm(*args):
    """Delete a file or files.
    Usage:  >>> rm('file.c' [, 'file.h'])  (brackets mean [optional] argument)
    Alias: delete
    """
    filenames = _glob(args)
    for item in filenames:
        try:
            os.remove(item)
        except os.error, detail:
            print "%s: %s" % (detail[1], item)
delete = rm

def rmdir(directory):
    """Remove a directory.
    Usage:  >>> rmdir('dirname')
    If the directory isn't empty, can recursively delete all sub-files.
    """
    try:
        os.rmdir(directory)
    except os.error:
        #directory wasn't empty
        answer = raw_input(directory+" isn't empty. Delete anyway?[n] ")
        if answer and answer[0] in 'Yy':
            subprocess.Popen('rm -rf %s' % directory, shell=True)
            print directory + ' Deleted.'
        else:
            print directory + ' Unharmed.'

def mv(*args):
    """Move files within a filesystem.
    Usage:  >>> mv('file1', ['fileN',] 'fileordir')
    If two arguments - both must be files
    If more arguments - last argument must be a directory
    """
    filenames = _glob(args)
    nfilenames = len(filenames)
    if nfilenames < 2:
        print 'Need at least two arguments'
    elif nfilenames == 2:
        try:
            os.rename(filenames[0], filenames[1])
        except os.error, detail:
            print "%s: %s" % (detail[1], filenames[1])
    else:
        for filename in filenames[:-1]:
            try:
                dest = filenames[-1]+'/'+filename
                if not os.path.isdir(filenames[-1]):
                    print 'Last argument needs to be a directory'
                    return
                os.rename(filename, dest)
            except os.error, detail:
                print "%s: %s" % (detail[1], filename)

def cp(*args):
    """Copy files along with their mode bits.
    Usage:  >>> cp('file1', ['fileN',] 'fileordir')
    If two arguments - both must be files
    If more arguments - last argument must be a directory
    """
    filenames = _glob(args)
    nfilenames = len(filenames)
    if nfilenames < 2:
        print 'Need at least two arguments'
    elif nfilenames == 2:
        try:
            shutil.copy(filenames[0], filenames[1])
        except os.error, detail:
            print "%s: %s" % (detail[1], filenames[1])
    else:
        for filename in filenames[:-1]:
            try:
                dest = filenames[-1]+'/'+filename
                if not os.path.isdir(filenames[-1]):
                    print 'Last argument needs to be a directory'
                    return
                shutil.copy(filename, dest)
            except os.error, detail:
                print "%s: %s" % (detail[1], filename)

def cpr(src, dst):
    """Recursively copy a directory tree to a new location
    Usage:  >>> cpr('directory0', 'newdirectory')
    Symbolic links are copied as links not source files.
    """
    shutil.copytree(src, dst)

def ln(src, dst):
    """Create a symbolic link.
    Usage:  >>> ln('existingfile', 'newlink')
    """
    os.symlink(src, dst)

def lnh(src, dst):
    """Create a hard file system link.
    Usage:  >>> ln('existingfile', 'newlink')
    """
    os.link(src, dst)

def pwd():
    """Print current working directory path.
    Usage:  >>> pwd()
    """
    print os.getcwd()

cdlist = [home]
def cd(directory = -1):
    """Change directory. Environment variables are expanded.
    Usage:
    cd('rel/$work/dir') change to a directory relative to your own
    cd('/abs/path')     change to an absolute directory path
    cd()                list directories you've been in
    cd(int)             integer from cd() listing, jump to that directory
    """
    global cdlist
    if type(directory) is types.IntType:
        if directory in range(len(cdlist)):
            cd(cdlist[directory])
            return
        else:
            pprint(cdlist)
            return
    directory = _glob(directory)[0]
    if not os.path.isdir(directory):
        print `directory`+' is not a directory'
        return
    directory = _expandpath(directory)
    if directory not in cdlist:
        cdlist.append(directory)
    os.chdir(directory)

def env():
    """List environment variables.
    Usage:  >>> env()
    """
    #unfortunately environ is an instance not a dictionary
    envdict = {}
    for key, value in os.environ.items():
        envdict[key] = value
    pprint(envdict)

interactive_dir_stack = []
def pushd(directory=home):
    """Place the current dir on stack and change directory.
    Usage:  >>> pushd(['dirname'])   (brackets mean [optional] argument)
                pushd()  goes home.
    """
    global interactive_dir_stack
    interactive_dir_stack.append(os.getcwd())
    cd(directory)

def popd():
    """Change to directory popped off the top of the stack.
    Usage:  >>> popd()
    """
    global interactive_dir_stack
    try:
        cd(interactive_dir_stack[-1])
        print interactive_dir_stack[-1]
        del interactive_dir_stack[-1]
    except IndexError:
        print 'Stack is empty'

def syspath():
    """Print the Python path.
    Usage:  >>> syspath()
    """
    import sys
    pprint(sys.path)

def which(object):
    """Print the source file from which a module, class, function, or method 
    was imported.
    
    Usage:    >>> which(mysteryObject)
    Returns:  Tuple with (file_name, line_number) of source file, or None if
              no source file exists
    Alias:    whence
    """
    object_type = type(object)
    if object_type is types.ModuleType:
        if hasattr(object, '__file__'):
            print 'Module from', object.__file__
            return (object.__file__, 1)
        else:
            print 'Built-in module.'
    elif object_type is types.ClassType:
        if object.__module__ == '__main__':
            print 'Built-in class or class loaded from $PYTHONSTARTUP'
        else:
            print 'Class', object.__name__, 'from', \
                    sys.modules[object.__module__].__file__
            # Send you to the first line of the __init__ method
            return (sys.modules[object.__module__].__file__, 
                    object.__init__.im_func.func_code.co_firstlineno)
    elif object_type in (types.BuiltinFunctionType, types.BuiltinMethodType):
        print "Built-in or extension function/method."
    elif object_type is types.FunctionType:
        print 'Function from', object.func_code.co_filename
        return (object.func_code.co_filename, object.func_code.co_firstlineno)
    elif object_type is types.MethodType:
        print 'Method of class', object.im_class.__name__, 'from', 
        fname = sys.modules[object.im_class.__module__].__file__
        print fname
        return (fname, object.im_func.func_code.co_firstlineno)
    else:
        print "argument is not a module or function."
    return None
whence = which

# Automatically add some convenience functions to __builtin__
import __builtin__
for n in autobuiltins:
    exec '__builtin__.__dict__["%s"] = %s' % (n,n) in globals()
