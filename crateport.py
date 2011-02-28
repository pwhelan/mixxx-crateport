#!/usr/bin/env python
#

import sqlite3
import sys
import xml.dom
import xml.dom.minidom

def generateCrateXML(crates):
	dom = xml.dom.getDOMImplementation()
	document = dom.createDocument(None, None, None)
	ncrates = document.createElement('crates')
	document.appendChild(ncrates)
	
	for cratename in crates:
		ncrate = document.createElement('crate')
		ncrates.appendChild(ncrate)
		ncrate.setAttribute('name', cratename)
		
		for track in crates[cratename]:
			ntrack = document.createElement('track')
			ncrate.appendChild(ntrack)
			for key in track.keys():
				ntrack.setAttribute(key, str(track[key]))
	
	return document.toxml()

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
				library.artist AS artist,
				library.title AS title,
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

