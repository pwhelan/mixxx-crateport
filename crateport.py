#!/usr/bin/env python
#

import sqlite3
import sys

def generateCrateXML(crates):
	for cratename in crates:
		print crates[cratename]

def getCrates(conn):
	cursor = conn.cursor()
	crates = {}
	
	cursor.execute("SELECT id, name FROM crates")
	
	row = cursor.fetchone()
	while row:
		crates[row['name']] = []
		
		cur2 = conn.cursor()
		cur2.execute("""
			SELECT
				library.id AS id,
				track_locations.location AS filename
			
			FROM crate_tracks
				INNER JOIN library
					ON crate_tracks.track_id = library.id
				INNER JOIN track_locations
					ON library.location = track_locations.id
			WHERE
				crate_tracks.crate_id = ?
			
			""", str(row['id']))
		
		track = cur2.fetchone()
		
		while track:
			crates[row['name']].append(track)
			track = cur2.fetchone()
		
		row = cursor.fetchone()
	
	return crates

if __name__ == '__main__':
	if len(sys.argv) >= 2:
		dbname = sys.argv[1]
	else:
		dbname = '/home/madjester/.mixxx/mixxxdb.sqlite'
	
	conn = sqlite3.connect(dbname)
	conn.row_factory = sqlite3.Row
	
	crates = getCrates(conn)
	print generateCrateXML(crates)
	
	conn.close()

