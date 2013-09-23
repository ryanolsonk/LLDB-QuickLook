//
//  NSObject+LLDBQuickLook.m
//  SlyBits
//
//  Created by Ryan Olson on 9/15/13.
//
//  The MIT License (MIT)
//
//  Copyright (c) 2013 Ryan Olson
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy of
//  this software and associated documentation files (the "Software"), to deal in
//  the Software without restriction, including without limitation the rights to
//  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
//  the Software, and to permit persons to whom the Software is furnished to do so,
//  subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all
//  copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
//  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
//  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
//  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
//  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//

#import "NSObject+LLDBQuickLook.h"

@implementation NSObject (LLDBQuickLook)

// A default implementation so the debugger doesn't barf when calling the selector.
- (NSData *)quickLookDebugData
{
    return nil;
}

// The default filename consists of the class name of the object and a string of digits from the timestamp
// There is no extension, as we don't have a good way to know what kind of file we're saving.
// NSObject subclasses can use this base implementation, but should at least append an appropriate file extension.
- (NSString *)quickLookDebugFilename
{
    // By putting this into an unsigned int, we might loose the most significant digits.
    // That's ok, we really just care about a reasonably unique string for the filename.
    unsigned int timestampInMilliseconds = (unsigned int)([NSDate timeIntervalSinceReferenceDate] * 1000);
    NSString *className = NSStringFromClass([self class]);
    return [NSString stringWithFormat:@"%@_%u", className, timestampInMilliseconds];
}

@end
