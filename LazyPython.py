# To use this add:
# import LazyPython
# sys.excepthook = LazyPython.LazyPython()
#
# to your $PYTHONSTARTUP file

import re, exceptions, traceback, sys, os

# There's no version_info in 1.5.2.  Use sys.version instead
if sys.version[0:3] < '2.1':
    raise ImportError, 'Python Version 2.1 or above is required.'


    
__author__ = "Nathaniel Gray <n8gray@caltech.edu>"
__version__ = '0.5.5'
__date__ = "Sun Sep 30 15:38:50 PDT 2001"

# This is deep, deep evil!  I love it!

_auto_quote_funcs_=['cd', 'cp', 'cpr', 'delete', 'll', 'ln', 'lnh', 'lr', 
                    'ls', 'mkdir', 'mv', 'popd', 'pushd', 'rm', 'rmdir', 'who',
                    'whos', 'execfile']
_auto_paren_funcs_=[]
_PAREN_ESCAPE = '/'
_QUOTE_ESCAPE = ','
_SHELL_ESCAPE = '!'

#####################################################################
###  You probably don't want to change things below here
#####################################################################

_first_word_re_=re.compile(r'^[ \t]*[^ \t\n]+[ \t\n]')
# All commands are evaluated in the interpreter's namespace
_ns_ = sys.modules['__main__'].__dict__

class LazyPython:
    """
Lazy Python is an attempt to make interactive python less painful for
lazy, lazy programmers.  There are five ways (three, sir), ah yes, three ways 
that LazyPython does this:

    1. Auto-Quoting
        Certain functions, methods, and other callables can be invoked with:
            >>> func arg1 arg2 arg3
        and the input will be translated to this:
            --> func("arg1", "arg2", "arg3")
        The list of auto-quoted functions is in LazyPython and can be
        extended or altered.

        You can force auto-quoting by using ',' as the first character
        of a line.  For example:
            >>> ,my_function /home/me   # becomes my_function("/home/me")
        Note that the ',' MUST be the first character on the line!  This
        won't work:
            >>> x = ,my_function /home/me    # syntax error

    2. Auto-Parenning
        Callable objects (i.e. functions, methods, etc) can be invoked like
        this (notice the commas between the arguments, unlike auto-quoting):
            >>> callable_ob arg1, arg2, arg3
        and the input will be translated to this:
            --> callable_ob(arg1, arg2, arg3)
        You can force auto-parenning by using '/' as the first character
        of a line.  For example:
            >>> /popd             # becomes 'popd()'
        Note that the '/' MUST be the first character on the line!  This
        won't work:
            >>> print /globals    # syntax error

    5. Shell-Escapes
        Any line that starts with '!' is treated as a shell escape. So
        if you want to copy a file you can type:
            >>> !cp file1.py file2.py
        Note that !cd /some/dir won't change the working directory of
        the Python interpreter.  All shell escapes take place in a subshell
        that is immediately discarded.  You have to use os.chdir or the cd
        convenience function to change the interpreter's directory.

IMPORTANT NOTES ON USAGE:  
    1.  The intent of this work is to make little functions like dir,
        pprint, and reload easier to use interactively.  By design, these 
        tricks only work in the interactive shell and only at the __main__ 
        scope.  DON'T USE THEM WHEN YOU WRITE SCRIPTS!

    2.  LazyPython tells you that it's altered your command line by
        displaying the new command line preceded by -->.  e.g.:
            >>> ls research/results
            --> ls("research/results")
        The only exception is shell escapes.  They are simply executed
        without printing anything.

    5.  LazyPython isn't triggered at all unless the command you enter
        would normally cause a SyntaxError.  Here are some examples of
        commands that don't work because they aren't syntax errors:
            >>> ls /usr/local/lib    # Looks like division
            >>> len [1,2,3,4]        # Looks like indexing
            >>> zip (1,2,3), (4,5,6) # Looks like call + tuple construct
        In these cases you must force auto-quoting or auto-parenning with
        the appropriate escape character.    

    4.  Whitespace is more important than usual (even for Python ;^)!  
        The function name must have some trailing whitespace and arguments 
        to auto-quote functions cannot have embedded whitespace.  
        >>> ls pathname/with whitespace
        becomes
        --> ls("pathname/with", "whitespace")
        and
        >>> len"something"
        causes a SyntaxError.
        >>> /zip (1,2,3), (4,5,6) # Works
        But
        >>> /zip(1,2,3), (4,5,6) # Fails --> zip(1,2,3),((4,5,6))

        Just remember to always put a space after your function name and 
        you'll be fine.  If you need whitespace in an auto-quote function's 
        argument I'm afraid you're just going to have to write your 
        function call out the old-fashioned way, ya lazy bum.

Current Auto-Quote Functions:
    cd, cp, cpr, delete, execfile, ll, ln, lnh, lr, ls, mkdir, mv, popd, 
    pushd, rm, rmdir, who, whos

To extend this list for the current session, type:
    >>> LazyPython._auto_quote_funcs_.append('funcname')
To permanently alter this list, edit LazyPython.py

Note that the characters used as escapes (!,/,,) can be changed by editing
LazyPython.py
"""
    def __init__(self):
        # Save the original excepthook for use when there *is* an error
        self._orig_ehook = sys.excepthook
        
    def uninstall(self):
        sys.excepthook = self._orig_ehook
        print "LazyPython uninstalled"
        
    def __call__(self, tp, val, argin3):
        global _auto_quote_funcs_

        # We only handle SyntaxErrors
        if not isinstance(val, exceptions.SyntaxError):
            self._orig_ehook(tp,val,argin3)
            return
        
        # Complain if we're not at the top level
        if (val.text[0]).isspace():
            raise RuntimeError, \
                    "LazyPython shortcuts do not work in loops or functions."
        
        # Test for shell escape
        if val.text[0] == _SHELL_ESCAPE:
            os.system(val.text[1:])
            return

        # 0 -> normal exception, 1 -> auto-quote, 2 -> auto-paren
        lp_mode = 0


        iFun = _first_word_re_.match(val.text)
        if iFun is None:  #Hard to see how this could happen, but just in case
            self._orig_ehook(tp,val,argin3)
            return
        iFun = iFun.group(0)[:-1]


        if val.text[0] == _PAREN_ESCAPE:
            # Check for the auto-paren escape
            lp_mode = 2
            iFun = iFun[1:]
            text = val.text[1:]
        elif val.text[0] == _QUOTE_ESCAPE:
            # Check for the auto-quote escape
            lp_mode = 1
            iFun = iFun[1:]
            text = val.text[1:]
        else:
            # See if it's an auto-quote/paren function or a callable
            text = val.text
            if iFun in _auto_quote_funcs_:
                lp_mode = 1
            elif iFun in _auto_paren_funcs_:
                lp_mode = 2
            else:
                try:
                    if callable( eval(iFun, _ns_) ):
                        lp_mode = 2
                except:
                    lp_mode = 0

        # Now decide what to do based on lp_mode
        if lp_mode == 0:
            # Normal Exception
            self._orig_ehook(tp,val,argin3)
            return

        if lp_mode == 1:
            theRest = text[len(iFun):].strip()
            # Auto-quote
            newcmd = iFun + '("' + '", "'.join(theRest.split()) + '")\n'
        elif lp_mode == 2:
            # Auto-paren
            #newcmd = iFun + '(' + ','.join(theRest.split()) + ')\n'
            theRest = text[len(iFun):].strip()
            newcmd = iFun + '(' + theRest + ')\n'
        elif lp_mode == 3:
            pass # newcmd has already been set
        else:
            raise RuntimeError, 'Error in LazyPython.py!  Illegal lp_mode.'

        # Try to execute the new command
        try:
            print '-->', newcmd
            sys.displayhook( eval( newcmd, _ns_ ) )
            #exec newcmd in _ns_
        except:
            traceback.print_exc()


print 'Welcome to Lazy Python.  Type "help LazyPython" for help.'
