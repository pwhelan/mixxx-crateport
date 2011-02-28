#!/usr/bin/env python
#

import sqlite3
import sys
import xml.dom
import xml.dom.minidom
from argparse import ArgumentParser

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
				track_locations.location,
				track_locations.filename
			
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

def findTrack(conn, ntrack):
	location = ntrack.getAttribute('location')
	artist = ntrack.getAttribute('artist')
	title = ntrack.getAttribute('title')
	filename = ntrack.getAttribute('filename')
	
	cursor = conn.cursor()
	
	cursor.execute("""
		SELECT
			l.id,
			l.filetype
			FROM library l
			INNER JOIN track_locations tl
				ON l.location = tl.id
			WHERE 
				(tl.location = ?)
		""", (location,))
	
	track = cursor.fetchone()
	if track != None:
		return track
	
	cursor.execute("""
		SELECT
			l.id,
			l.filetype
			FROM library l
			INNER JOIN track_locations tl
				ON l.location = tl.id
			WHERE 
				(tl.filename = ?)
		""", (filename,))
	
	track = cursor.fetchone()
	if track != None:
		return track
	
	cursor.execute("""
		SELECT
			l.id,
			l.filetype
			FROM library l
			WHERE 
				(l.artist = ? AND l.title = ?)
		""", (artist, title))
	
	track = cursor.fetchone()
	if track != None:
		return track
	
	return None

def importCrateXML(conn, dcrate):
	cursor = conn.cursor()
	ncrates = dcrate.documentElement
	if ncrates.tagName != 'crates':
		raise Exception('Not a Crates XML File')
	
	for ncrate in ncrates.childNodes:
		if ncrate.tagName != 'crate':
			raise Exception('Not a Crate')
		
		try:
			cursor.execute("INSERT INTO crates(name) VALUES(?)", 
				(ncrate.getAttribute('name'),))
		except sqlite3.IntegrityError:
			continue
		
		cursor.execute("SELECT id FROM crates WHERE name = ?", 
			(ncrate.getAttribute('name'),))
		crateId = cursor.fetchone()
		
		for ntrack in ncrate.childNodes:
			if ncrate.tagName != 'crate':
				raise Exception('Not a Crate')
			
			track = findTrack(conn, ntrack)
			try:
				cursor.execute("""
					INSERT INTO crate_tracks(crate_id, track_id)
					VALUES(?, ?)
				""", (str(crateId), track['id']))
			except sqlite3.IntegrityError:
				continue

def main():
	opt = ArgumentParser(description='Import and Export Crates from Mixxx')
	opt.add_argument('-i, --import', dest='export', action='store_false', required=False) 
	opt.add_argument('-e, --export', dest='export', action='store_true', required=False)
	opt.add_argument('-d, --dbname', dest='dbname', required=False, default='/home/madjester/.mixxx/mixxxdb.sqlite')
	opt.add_argument('file')
	
	args = opt.parse_args()
	
	conn = sqlite3.connect(args.dbname)
	conn.row_factory = sqlite3.Row
	
	if args.export == True:
		crates = getCrates(conn)
		print generateCrateXML(crates)
	else:
		crates = xml.dom.minidom.parse(args.file)
		importCrateXML(conn, crates)
	
	conn.close()

if __name__ == '__main__':
	main()
	
