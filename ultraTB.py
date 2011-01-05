"""
ultraTB.py -- Spice up your tracebacks!

* ColorTB
I've always found it a bit hard to visually parse tracebacks in Python.  The
ColorTB class is a solution to that problem.  It colors the different parts of a
traceback in a manner similar to what you would expect from a syntax-hilighting
text editor.  The colors are defined in the class "Colors" and the defaults 
should look good on a standard linux terminal.  If you are using a different
color scheme you will probably have to tweak the settings in Colors to make
things legible for yourself.  Not being knowledgeable about terminals and 
cross-platform issues, I can only assure that this will work on Linux.  If you
are able to make this work on a different platform I would be interested in
hearing about it.

Installation instructions for ColorTB:
    import sys,ultraTB
    sys.excepthook = ultraTB.ColorTB()

* VerboseTB  
I've also included a port of Ka-Ping Yee's "cgitb.py" that produces all kinds
of useful info when a traceback occurs.  Ping originally had it spit out HTML
and intended it for CGI programmers, but why should they have all the fun?  I
altered it to spit out colored text to the terminal.  It's a bit overwhelming,
but kind of neat, and maybe useful for long-running programs that you believe
are bug-free.  If a crash *does* occur in that type of program you want details.
Give it a shot--you'll love it or you'll hate it.

Installation instructions for ColorTB:
    import sys,ultraTB
    sys.excepthook = ultraTB.VerboseTB()

* Cohabitating with LazyPython
Either module will work in conjunction with my LazyPython hack if you 
install it *before* you install LazyPython.  e.g.:
    import sys,LazyPython,ultraTB
    sys.excepthook = ultraTB.ColorTB()
    sys.excepthook = LazyPython.LazyPython()
    
Note:  Much of the code in this module was lifted verbatim from the standard
library module "traceback.py" and Ka-Ping Yee's "cgitb.py".
"""

# Thanks to William McVey <wam@cisco.com> for the xterm-conditional code.

import sys, traceback, types, os

__version__ = "0.3"
__author__ = "Nathaniel Gray <n8gray@caltech.edu>"
__date__ = "Sun Oct 21 14:51:45 PDT 2001"

if sys.version[0:3] < '2.1':
    raise ImportError, 'Python Version 2.1 or above is required.'

class Colors:
    
    # Note that these color names are the canonical Linux terminal Colors.
    # If your terminal is set up in any customized way, the names won't be
    # accurate.  Also note that the color scheme I have set up is for
    # a black background.  You may have to do some serious tweaking to make
    # things look good for you.
    if os.environ.get("TERM") == "xterm":
       _base = "\033[%sm"
       Normal = "\033[0m"
    else:
       _base = "\001\033[%sm\002"
       Normal = "\001\033[0m\002"
    Black        = _base % '0;30'
    Blue         = _base % '0;34'
    Green        = _base % '0;32'
    Cyan         = _base % '0;36'
    Red          = _base % '0;31'
    Purple       = _base % '0;35'
    Brown        = _base % '0;33'
    LightGray    = _base % '0;37'
    DarkGray     = _base % '1;30'
    LightBlue    = _base % '1;34'
    LightGreen   = _base % '1;32'
    LightCyan    = _base % '1;36'
    LightRed     = _base % '1;31'
    LightPurple  = _base % '1;35'
    Yellow       = _base % '1;33'
    White        = _base % '1;37'
    
    # The color to be used for the top line
    toplineColor = LightRed
    
    # The colors to be used in the traceback
    filenameColor = Green
    linenoColor = Green
    nameColor = Purple
    vNameColor = Cyan        # Slightly different color scheme for VerboseTB
    valColor = Green
    emColor = LightCyan
    
    # Emphasized colors for the last frame of the traceback
    normalEm = LightCyan
    filenameColorEm = LightGreen
    linenoColorEm = LightGreen
    nameColorEm = LightPurple
    valColorEm = LightBlue
    
    # Colors for printing the exception
    excNameColor = LightRed
    lineColor = Yellow
    caretColor = White

    if os.environ.get("TERM") == "xterm":
       # xterms have a lot less colors
       toplineColor = Red
       emColor = Cyan
       # Emphasized colors for the last frame of the traceback
       normalEm = Cyan
       # filenameColorEm = Green
       filenameColorEm = Purple
       linenoColorEm = Green
       nameColorEm = Purple
       valColorEm = Blue
       excNameColor = Red

class ColorTB:
    def __call__(self, etype, value, tb):
        print>>sys.stderr, Colors.toplineColor + '-'*60 + Colors.Normal
        if tb:
            print>>sys.stderr, 'Traceback %s(most recent call last)%s:' % \
                                (Colors.normalEm, Colors.Normal)
            elist = traceback.extract_tb(tb)
            slist = self._format_list( elist )
            for line in slist:
                print>>sys.stderr, line,
            #sys.stderr.writelines( slist )
        lines = self._format_exception_only(etype, value)
        for line in lines[:-1]:
            print>>sys.stderr, " "+line,
        print>>sys.stderr, lines[-1],
        
    def _format_list(self, extracted_list):
        """Format a list of traceback entry tuples for printing.

        Given a list of tuples as returned by extract_tb() or
        extract_stack(), return a list of strings ready for printing.
        Each string in the resulting list corresponds to the item with the
        same index in the argument list.  Each string ends in a newline;
        the strings may contain internal newlines as well, for those items
        whose source text line is not None.
        
        Lifted almost verbatim from traceback.py
        """
        list = []
        for filename, lineno, name, line in extracted_list[:-1]:
            item = '  File %s"%s"%s, line %s%d%s, in %s%s%s\n' % \
                    (Colors.filenameColor, filename, Colors.Normal, 
                     Colors.linenoColor, lineno, Colors.Normal,
                     Colors.nameColor, name, Colors.Normal)
            if line:
                item = item + '    %s\n' % line.strip()
            list.append(item)
        # Emphasize the last entry
        filename, lineno, name, line = extracted_list[-1]
        item = '%s  File %s"%s"%s, line %s%d%s, in %s%s%s%s\n' % \
                (Colors.normalEm,
                 Colors.filenameColorEm, filename, Colors.normalEm,
                 Colors.linenoColorEm, lineno, Colors.normalEm,
                 Colors.nameColorEm, name, Colors.normalEm,
                 Colors.Normal)
        if line:
            item = item + '%s    %s%s\n' % (Colors.lineColor, line.strip(),
                                            Colors.Normal)
        list.append(item)
        return list
        
    def _format_exception_only(self, etype, value):
        """Format the exception part of a traceback.

        The arguments are the exception type and value such as given by
        sys.last_type and sys.last_value. The return value is a list of
        strings, each ending in a newline.  Normally, the list contains a
        single string; however, for SyntaxError exceptions, it contains
        several lines that (when printed) display detailed information
        about where the syntax error occurred.  The message indicating
        which exception occurred is the always last string in the list.
        
        Also lifted nearly verbatim from traceback.py
        """
        list = []
        if type(etype) == types.ClassType:
            stype = Colors.excNameColor + etype.__name__ + Colors.Normal
        else:
            stype = etype  # String exceptions don't get special coloring
        if value is None:
            list.append( str(stype) + '\n')
        else:
            if etype is SyntaxError:
                try:
                    msg, (filename, lineno, offset, line) = value
                except:
                    pass
                else:
                    if not filename: filename = "<string>"
                    list.append('%s  File %s"%s"%s, line %s%d%s\n' % \
                            (Colors.normalEm,
                             Colors.filenameColorEm, filename, Colors.normalEm,
                             Colors.linenoColorEm, lineno, Colors.Normal  ))
                    if line is not None:
                        i = 0
                        while i < len(line) and line[i].isspace():
                            i = i+1
                        list.append('%s    %s%s\n' % (Colors.lineColor,
                                                      line.strip(), 
                                                      Colors.Normal))
                        if offset is not None:
                            s = '    '
                            for c in line[i:offset-1]:
                                if c.isspace():
                                    s = s + c
                                else:
                                    s = s + ' '
                            list.append('%s%s^%s\n' % (Colors.caretColor, s,
                                                       Colors.Normal) )
                        value = msg
            s = self._some_str(value)
            if s:
                list.append('%s%s:%s %s\n' % (str(stype), Colors.excNameColor,
                                              Colors.Normal, s))
            else:
                list.append('%s\n' % str(stype))
        return list

    def _some_str(self, value):
        # Lifted from traceback.py
        try:
            return str(value)
        except:
            return '<unprintable %s object>' % type(value).__name__

class VerboseTB:
    """A port of Ka-Ping Yee's cgitb.py module that outputs color text instead
    of HTML.  Requires inspect and pydoc.  Crazy, man."""

    def text(self, etype, evalue, etb, context=5):
        """Return a nice text document describing the traceback."""
        import sys, os, types, string, time, traceback
        import keyword, tokenize, linecache, inspect, pydoc

        if type(etype) is types.ClassType:
            etype = etype.__name__
        # Header with the exception type, python version, and date
        pyver = 'Python ' + string.split(sys.version)[0] + ': ' + sys.executable
        date = time.ctime(time.time())
        exc = "%s%s%s" % (Colors.excNameColor, str(etype), Colors.Normal)

        head = '%s%s%s\n%s%s%s\n%s' % (Colors.toplineColor, '-'*75, Colors.Normal,
                                       exc, ' '*(75-len(str(etype))-len(pyver)),
                                       pyver, string.rjust(date, 75) )
        head += "\nA problem occured in a Python script.  Here is the sequence of function"\
                "\ncalls leading up to the error, with the most recent (innermost) call last."

        indent = ' '*6
        frames = []
        records = inspect.getinnerframes(etb, context)
        for frame, file, lnum, func, lines, index in records:
            file = file and os.path.abspath(file) or '?'
            link = Colors.filenameColorEm + file + Colors.Normal
            args, varargs, varkw, locals = inspect.getargvalues(frame)
            if func == '?':
                call = ''
            else:
	        def eqrepr(value, repr=pydoc.text.repr): return '=' + repr(value)
                call = 'in %s%s%s%s%s' % (Colors.vNameColor, 
                                          func, Colors.valColorEm, 
                                          inspect.formatargvalues( 
                                                args, varargs, varkw, locals, 
                                                formatvalue=eqrepr),
                                          Colors.Normal)

            names = []
            def tokeneater(type, token, start, end, line,
                           names=names, kwlist=keyword.kwlist,
		           NAME=tokenize.NAME, NEWLINE=tokenize.NEWLINE):
                if type == NAME and token not in kwlist:
                    if token not in names: names.append(token)
                if type == NEWLINE: raise IndexError
            def linereader(file=file, lnum=[lnum], getline=linecache.getline):
                line = getline(file, lnum[0])
                lnum[0] = lnum[0] + 1
                return line

            try:
                tokenize.tokenize(linereader, tokeneater)
            except IndexError: pass
            lvals = []
            for name in names:
                if name in frame.f_code.co_varnames:
                    if locals.has_key(name):
                        value = pydoc.text.repr(locals[name])
                    else:
                        value = '%sundefined%s' % (Colors.emColor, Colors.Normal)
                    name = '%s%s%s' % (Colors.vNameColor, name, Colors.Normal)
                else:
                    if frame.f_globals.has_key(name):
                        value = pydoc.text.repr(frame.f_globals[name])
                    else:
                        value = '%sundefined%s' % (Colors.emColor, Colors.Normal)
                    name = '%sglobal%s %s%s%s' % (Colors.emColor, Colors.Normal,
                                                  Colors.vNameColor, name, 
                                                  Colors.Normal)
                lvals.append('%s %s= %s%s' % (name, Colors.valColorEm, value,
                                              Colors.Normal))
            if lvals:
                lvals = string.join(lvals, '%s,%s ' % (Colors.valColorEm, 
                                                        Colors.Normal) )
                lvals = indent + lvals
            else:
                lvals = ''

            level = link + ' ' + call + '\n'
            excerpt = []
            if index is not None:
                i = lnum - index
                for line in lines:
                    num = ' '*(5-len(str(i))) + str(i)
                    if i == lnum:
                        # This is the line with the error
                        line = '%s%s%s %s%s' %(Colors.linenoColorEm, num, 
                                               Colors.lineColor, line, Colors.Normal)
                    else:
                        line = '%s%s%s %s' %(Colors.linenoColor, num, 
                                             Colors.Normal, line)

                    excerpt.append( line)
                    if i == lnum:
                        excerpt.append(lvals + '\n')
                    i = i + 1
            frames.append(level + string.join(excerpt, ''))

        exception = ['%s%s%s: %s' % (Colors.excNameColor, str(etype), 
                                     Colors.Normal, str(evalue))]
        if type(evalue) is types.InstanceType:
            for name in dir(evalue):
                value = pydoc.text.repr(getattr(evalue, name))
                exception.append('\n%s%s = %s' % (indent, name, value))

        return head + '\n\n' + string.join(frames, '\n') + '\n' + \
                string.join(exception, '')

    def handler(self, info=None):
        import sys
        (etype, evalue, etb) = info or sys.exc_info()
        print self.text(etype, evalue, etb)

    def __call__(self, etype, evalue, etb):
        """This hook can replace sys.excepthook (for Python 2.1 or higher)."""
        self.handler((etype, evalue, etb))
        
        
if __name__ == "__main__":
    def spam(c, (d, e)):
        x = c + d
        y = c * d
        foo(x, y)

    def foo(a, b, bar=1):
        eggs(a, b + bar)

    def eggs(f, g, z=globals()):
        h = f + g
        i = f - g
        return h / i

    print ''
    print '*** Before ***'
    #print ''
    try:
        print spam(1, (2, 3))
    except:
        traceback.print_exc()
    print ''
    
    handler = ColorTB()
    print '*** ColorTB ***'
    try:
        print spam(1, (2, 3))
    except:
        apply(handler, sys.exc_info() )
    print ''
    
    handler = VerboseTB()
    print '*** VerboseTB ***'
    try:
        print spam(1, (2, 3))
    except:
        apply(handler, sys.exc_info() )
    print ''
    
