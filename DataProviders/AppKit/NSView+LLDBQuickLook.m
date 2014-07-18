//
//  NSView+LLDBQuickLook.m
//  Sweeper
//
//  Created by Jay Chae  on 7/18/14.
//  Copyright (c) 2014 JCLab. All rights reserved.
//

#import "NSView+LLDBQuickLook.h"
#import "NSObject+LLDBQuickLook.h"

@implementation NSView (LLDBQuickLook)

- (NSData *)quickLookDebugData
{
    NSBitmapImageRep *imageRepresentation = [self bitmapImageRepForCachingDisplayInRect:self.bounds];
    [self cacheDisplayInRect:self.bounds toBitmapImageRep:imageRepresentation];
    return [imageRepresentation representationUsingType:NSPNGFileType properties:nil];
}

- (NSString *)quickLookDebugFilename
{
    NSString *filename = [super quickLookDebugFilename];
    return [filename stringByAppendingPathExtension:@"png"];
}

@end
