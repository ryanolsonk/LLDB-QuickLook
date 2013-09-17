//
//  NSObject+LLDBQuickLook.h
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

#import <Foundation/Foundation.h>

// An informal protocol that objects can choose to implement if they will benefit from Quick Look debugging.
// Default implementations are provided on NSObject to keep the debugger from barfing when it calls the selectors.
@interface NSObject (LLDBQuickLook)

// The data returned by this method will be saved to a tmp file by the lldb commands 'ql' and 'qlf'.
// The tmp file will then be opened with Quick Look.
- (NSData *)quickLookDebugData;

// The filename returned by this method will be used for the tmp file.
// Specifying a propper extension for the file helps Quick Look display the file
// and choose an appropriate application to open the file.
- (NSString *)quickLookDebugFilename;

@end
