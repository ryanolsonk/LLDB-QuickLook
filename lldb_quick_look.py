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


class DebuggerError(Exception):
    """Exception raised when when a debugger command cannot proceed due to bad state or invalid input"""
    pass

def quick_look_command(debugger, command, result, internal_dict):
    """
    Quick Look Full (qlf): A command to save arbitrary data from a debugging session 
    to a tmp location & open in Finder with the full version of Quick Look
    Invoke as
    (lldb) qlf <object>
    e.g.
    (lldb) qlf self.view
    """
    try:
        savedFilePath = get_data_and_save(debugger, command)
        print >> result, "Data written to {0!s}".format(savedFilePath)
        open_with_quick_look(savedFilePath)
    except DebuggerError, err:
        print >> result, "Error: {0!s}".format(err)


def quick_look_lite_command(debugger, command, result, internal_dict):
    """
    Quick Look (ql): A command to save arbitrary data from a debugging session to a tmp location 
    and open using qlmanage - a stripped down version of Quick Look invokable from the command line.
    Invoke as
    (lldb) ql <object>
    e.g.
    (lldb) ql self.imageView.image
    """
    try:
        savedFilePath = get_data_and_save(debugger, command)
        print >> result, "Data written to {0!s}".format(savedFilePath)
        open_with_quick_look_lite(savedFilePath)
    except DebuggerError, err:
        print >> result, "Error: {0!s}".format(err)


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


def get_data_and_save(debugger, command):
    """
    Asks the object passed in command for its debugData and debugFilename.
    Saves the data to the filename under /tmp/{target}
    Raises DebuggerError exceptions for bad state or invalid commands
    Returns the path of the saved file in the success case.
    """
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()

    if not target.IsValid() or not process.IsValid():
        raise DebuggerError("unable to get target/process")

    options = lldb.SBExpressionOptions()
    options.SetIgnoreBreakpoints()

    dataCommand = "(NSData *)[({0!s}) debugData]".format(command)
    filenameCommand = "(NSString *)[({0!s}) debugFilename]".format(command)

    
    if frame.IsValid():
        data = frame.EvaluateExpression(dataCommand, options)
        filename = frame.EvaluateExpression(filenameCommand, options).GetObjectDescription()
    else:
        data = target.EvaluateExpression(dataCommand, options)
        filename = target.EvaluateExpression(filenameCommand, options).GetObjectDescription()

    if data.GetValueAsUnsigned() == 0:
        raise DebuggerError("can't get debug data. Make sure the object has a non-nil response to the selector debugData")

    lengthCommand = "(NSUInteger)[({0!s}) length]".format(data.path)
    length = target.EvaluateExpression(lengthCommand, options).GetValueAsUnsigned()

    bytesCommand = "(const void *)[({0!s}) bytes]".format(data.path)
    bytes = target.EvaluateExpression(bytesCommand, options).GetValueAsUnsigned()

    error = lldb.SBError()
    memoryBuffer = process.ReadMemory(bytes, length, error)
    if error.Fail():
        raise DebuggerError("couldn't read memory: {0!s}".format(error))

    directory = os.path.join("/tmp", str(target))
    if not os.path.exists(directory):
        os.makedirs(directory)

    path = os.path.join(directory, str(filename))
    with open(path, "w") as dataFile:
        dataFile.write(memoryBuffer)
        
    return path


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add --function lldb_quick_look.quick_look_command qlf')
    debugger.HandleCommand('command script add --function lldb_quick_look.quick_look_lite_command ql')

