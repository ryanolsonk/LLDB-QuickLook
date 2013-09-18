# The MIT License (MIT)

# Copyright (c) 2013 Ryan Olson

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import lldb
import os
import subprocess
import optparse
import shlex


class DebuggerError(Exception):
    """
    Exception raised when when a debugger command cannot proceed due to bad state or invalid input
    """
    pass


def create_quick_look_options():
    usage = "usage: %prog <options> -- <expr>"
    parser = optparse.OptionParser(prog='quicklook', usage=usage)
    parser.add_option('-f', '--filename', type='string', dest='filename', help='Override filename for saving the data', metavar='filename.ext')
    parser.add_option('-l', '--lite', action='store_true', dest='lite', help='Use the stripped down version of Quick Look (qlmanage)', default=False)
    return parser


def quick_look_command(debugger, command, result, internal_dict):
    """
    Overview:

    A command to inspect objects that are not well represented by strings in the debug console.
    The command will ask an object for its quickLookDebugData and save that data to the object's 
    quickLookFilename or a custom filename passed using the -f option. The file will be saved under /tmp/<target>
    You can make any object into a quick look data provider by simply implementing the quickLookDebugData and quickLookFilename methods.

    Examples:

    quicklook self.imageView.image
    quicklook [[UIApplication sharedApplication] keyWindow]

    Some use cases:

    Debugging images not accessible from the Xcode GUI.
    Debugging views that are not on screen or obscured by another view.
    Saving images for screenshots or to watch a view change over time.
    Opening text in a propper editor without having to copy/paste.

    IMPORTANT NOTE:

    Because this command takes 'raw' input, if you use any
    command options you must use ' -- ' between the end of the command options
    and the beginning of the raw input.


    """

    # Separate the options from the expression
    command_list = shlex.split(command)
    try:
        # "--" indicates the end of the arguments and beginning of the expression
        dashdash_idx = command_list.index("--")
        arguments = command_list[:dashdash_idx]
        # strip everything up to and including the "-- " to get the expression
        expression = command[(command.rindex("--") + 3):]
    except ValueError:
        # no "--" found, assume no arguments
        arguments = []
        expression = command


    # Parse the options
    parser = create_quick_look_options()
    try:
        (options, args) = parser.parse_args(arguments)
    except:
        result.SetError("Option parsing failed")
        return


    # Save the data
    try:
        savedFilePath = get_data_and_save(debugger, expression, options.filename)
        print >> result, "Data written to {0!s}".format(savedFilePath)
    except DebuggerError, err:
        result.SetError(str(err))
        return


    # Open with Quick Look
    if options.lite:
        open_with_quick_look_lite(savedFilePath)
    else:
        open_with_quick_look(savedFilePath)


def open_with_quick_look(filePath):
    """
    If "Enable access for assistive devices" is checked in system preferences, this method
    will use AppleScript to open the finder and trigger Quick Look. Otherwise, it falls
    back to the lightweight "qlmanage" program (intended for debugging Quick Look,
    but invokable from the command line).
    filePath must be absolute
    e.g. open_with_quick_look("/tmp/file.png")
    """

    # Use the full quick look if GUI scripting is enabled
    if os.path.exists("/private/var/db/.AccessibilityAPIEnabled"):

        qlAppleScript = """
        set theFile to ("{0}" as POSIX file)
        tell application "Finder"
            activate
            open (container of file theFile)
            select theFile
        end tell
    
        tell application "System Events" to keystroke "y" using command down
        """.format(filePath)

        osaProcess = subprocess.Popen(["osascript", "-"], stdin=subprocess.PIPE)
        osaProcess.communicate(qlAppleScript)

    # Fall back to the pseudo quick look
    else:
        open_with_quick_look_lite(filePath)


def open_with_quick_look_lite(filePath):
    subprocess.Popen(["qlmanage", "-p", filePath])


def get_data_and_save(debugger, expression, overrideFilename):
    """
    Asks the object passed in expression for its debugData and debugFilename.
    Saves the data to the filename under /tmp/{target}
    Raises DebuggerError exceptions for bad state or invalid commands
    Returns the path of the saved file in the success case.
    """
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()

    if not target.IsValid() or not process.IsValid():
        raise DebuggerError("Unable to get target/process")

    options = lldb.SBExpressionOptions()
    options.SetIgnoreBreakpoints()

    dataCommand = "(NSData *)[({0!s}) quickLookDebugData]".format(expression)
    if frame.IsValid():
        data = frame.EvaluateExpression(dataCommand, options)
    else:
        data = target.EvaluateExpression(dataCommand, options)

    if data.GetValueAsUnsigned() == 0:
        raise DebuggerError("Can't get debug data from {0!s}. Make sure the object has a non-nil response to the selector quickLookDebugData".format(expression))

    lengthCommand = "(NSUInteger)[({0!s}) length]".format(data.path)
    length = target.EvaluateExpression(lengthCommand, options).GetValueAsUnsigned()

    bytesCommand = "(const void *)[({0!s}) bytes]".format(data.path)
    bytes = target.EvaluateExpression(bytesCommand, options).GetValueAsUnsigned()

    error = lldb.SBError()
    memoryBuffer = process.ReadMemory(bytes, length, error)
    if error.Fail():
        raise DebuggerError("Couldn't read memory: {0!s}".format(error))

    directory = os.path.join("/tmp", str(target))
    if not os.path.exists(directory):
        os.makedirs(directory)

    # If a filename was not specfied with the command, ask the expression for it
    if overrideFilename is None:
        filenameCommand = "(NSString *)[({0!s}) quickLookDebugFilename]".format(expression)
        if frame.IsValid():
            filename = frame.EvaluateExpression(filenameCommand, options).GetObjectDescription()
        else:
            filename = target.EvaluateExpression(filenameCommand, options).GetObjectDescription()
    else:
        filename = overrideFilename

    if filename is None:
        raise DebuggerError("No filename provided. Please specify one in quickLookDebugFilename or by passing a name in the -f option")

    path = os.path.join(directory, str(filename))
    with open(path, "w") as dataFile:
        dataFile.write(memoryBuffer)
        
    return path


def __lldb_init_module(debugger, internal_dict):
    parser = create_quick_look_options()
    quick_look_command.__doc__ = quick_look_command.__doc__ + parser.format_help()
    debugger.HandleCommand('command script add --function lldb_quick_look.quick_look_command quicklook')

