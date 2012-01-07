#import <Foundation/Foundation.h>
#import "FMDatabase.h"
#import "FMDatabaseAdditions.h"


/* -----------------------------------------------------------------------------
    Get metadata attributes from file
   
   This function's job is to extract useful information your file format supports
   and return it as a dictionary
   ----------------------------------------------------------------------------- */

Boolean GetMetadataForURL(void* thisInterface, CFMutableDictionaryRef attributes, CFStringRef contentTypeUTI, CFURLRef urlForFile)
{
	Boolean success=NO;
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
	
	FMDatabase *db = [FMDatabase databaseWithPath:[(NSURL*)urlForFile path]];
	
	if ([db open]) {
		FMResultSet *s = [db executeQuery:@"SELECT first_name, last_name FROM players WHERE deleted!=1 ORDER BY last_name, first_name"];
		NSMutableArray *players = [NSMutableArray array];
		while ([s next]) {
			[players addObject:[NSString stringWithFormat:@"%@ %@", [s stringForColumn:@"first_name"], [s stringForColumn:@"last_name"]]];
		}
		
		[s close];
		[db close];
		
		if ([players count] > 0) {
			[(NSMutableDictionary *)attributes setObject:players forKey:(NSString *)kMDItemParticipants];
			success=YES;
		}
	}
	
	[pool release];
    return success;
}
