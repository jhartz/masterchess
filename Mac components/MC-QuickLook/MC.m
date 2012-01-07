#include "MC.h"

// Based on https://github.com/toland/qlmarkdown/tree/3516603448db8bba398aa144fefa7fbb01616938

NSData* renderMCDB(NSURL* url, BOOL smallPreview)
{
	//NSBundle* bundle = [NSBundle bundleWithIdentifier: @"com.github.jake33.MasterChess"];
	
	NSString* path = [[NSWorkspace sharedWorkspace] absolutePathForAppBundleWithIdentifier: @"com.github.jake33.masterchess"];
	NSBundle* bundle = [NSBundle bundleWithPath: path];
	
    NSTask* task = [[NSTask alloc] init];
	[task setLaunchPath: [bundle pathForResource: @"QuickLook" ofType: @"py"]];
	if (smallPreview) {
		[task setArguments: [NSArray arrayWithObjects: [url path], @"SMALLER", nil]];
	} else {
		[task setArguments: [NSArray arrayWithObjects: [url path], nil]];
	}
	
    NSPipe* pipe = [NSPipe pipe];
    [task setStandardOutput: pipe];
	
    [task launch];
	
    return [[pipe fileHandleForReading] readDataToEndOfFile];
}