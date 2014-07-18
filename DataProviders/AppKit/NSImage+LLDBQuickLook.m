//
//  NSImage+LLDBQuickLook.m
//  Sweeper
//
//  Created by Jay Chae  on 7/18/14.
//  Copyright (c) 2014 JCLab. All rights reserved.
//

#import "NSImage+LLDBQuickLook.h"
#import "NSObject+LLDBQuickLook.h"

@implementation NSImage (LLDBQuickLook)

- (NSData *)quickLookDebugData
{
    NSBitmapImageRep *imageRepresentation = [[NSBitmapImageRep imageRepsWithData:[self TIFFRepresentation]] firstObject];
    return [imageRepresentation representationUsingType:NSPNGFileType properties:nil];
}

- (NSString *)quickLookDebugFilename
{
    return [[super quickLookDebugFilename] stringByAppendingPathExtension:@"png"];
}

@end
