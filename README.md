LLDB-QuickLook
==============

![LLDB-QuickLook Example 1](http://f.cl.ly/items/2q2t253L3w130Q0Z3i1D/calendar.png)

![LLDB-QuickLook Example 2](http://f.cl.ly/items/0F381J0i2z3l291A1Q3U/background.png)

LLDB-QuickLook is a debugger command to open images, views, and more using Quick Look. This command is great for inspecting any object that is not well represented by a string in the debugging console. The command is inspired by Xcode's new Quick Look feature, but is better in two ways:

1.) You can inspect any object accessible by an lldb expression, not just objects available in the Xcode GUI.
2.) Any type of object can be inspected by implementing a simple data provider protocol, not just UIImages.

The command is quite simple. It asks an object in your program for debug data, saves the data to a tmp file on your computer, and opens the file using Finder and Quick Look.

## Getting Started

1. Clone the repository.
2. Copy the `.lldbinit` file to your home directory (or append the lines to your existing `.lldbinit`).
3. Update the path to `lldb_quick_look.py` in the `.lldbinit` file to match the script's location on your machine.
4. Add the `DataProviders` directory to your Xcode project. **LLDB-QuickLook requires Xcode 5 or later.**
5. To use the full version of quick look, ensure that "Enable access for assistive devices" setting is checked in System Preferences.

![Enable access for assistive devices](http://f.cl.ly/items/1Y060S3c2W0f321m3H1Y/enable-access-for-assistive-devices.png)

## Using the Command

When your program is paused on a breakpoint in lldb, calling the command:

`quicklook <object>` or `ql <object>`

will ask the object for its `quickLookDebugData` and save that data to the object's `quickLookFilename`. The file will be saved under `/tmp/<target>` and opened using Finder + Quick Look. You can make any object into a Quick Look data provider by simply implementing the `quickLookDebugData` and `quickLookFilename` methods. Simple implementations of data providers for `NSObject`, `UIImage`, `UIView`, `NSData`, and `NSString` can be found in the `DataProviders` directory.

## Examples

`(lldb) quicklook self.imageView.image`

`(lldb) ql [[UIApplication sharedApplication] keyWindow]`

`(lldb) quicklook -f some_object.json -- [self jsonString]`

`(lldb) ql -l self.view`

## Some use cases

* Debugging images not accessible from the Xcode GUI.
* Debugging views that are not on screen or obscured by another view.
* Saving images for screenshots or to watch a view change over time.
* Opening text in a proper editor without having to copy/paste from the console.

Tip: type `help quicklook` from the lldb prompt to see the options for the command.

## About

`quicklook` uses lldb's powerful (but poorly documented) python scripting bridge. I don't typically write in python, so apologies if I've mixed in some objective-c style conventions. If you have any ideas, comments, or feedback, I'm [@ryanolsonk](http://twitter.com/ryanolsonk) on twitter, and pull requests are welcome!
