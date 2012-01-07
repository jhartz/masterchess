#import <QuickLook/QuickLook.h>
#import <Cocoa/Cocoa.h>
#include "MC.h"

/* -----------------------------------------------------------------------------
   Generate a preview for file

   This function's job is to create preview for designated file
   ----------------------------------------------------------------------------- */

OSStatus GeneratePreviewForURL(void *thisInterface, QLPreviewRequestRef preview, CFURLRef url, CFStringRef contentTypeUTI, CFDictionaryRef options)
{
    CFDataRef data = (CFDataRef) renderMCDB((NSURL*) url, (BOOL) 0);
	
    if (data) {
		CFDictionaryRef props = (CFDictionaryRef) [NSDictionary dictionary];
        QLPreviewRequestSetDataRepresentation(preview, data, kUTTypeHTML, props);
    }
	
    return noErr;
}

void CancelPreviewGeneration(void* thisInterface, QLPreviewRequestRef preview)
{
    // implement only if supported
}
