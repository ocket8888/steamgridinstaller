#!/usr/bin/python3

# Copyright 2026 ocket8888
# This file is part of steamgridinstaller.
# steamgridinstaller is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# steamgridinstaller is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with steamgridinstaller. If not, see <https://www.gnu.org/licenses/>. 

import sys
from argparse import ArgumentParser

import requests
import os

from .api import getAssets, ParseError, RequestError
from .fs import locateOrCreateGridFolder, writeAsset, WriteAssetError
from .progress import printProgressBar

def main() -> int:
	parser = ArgumentParser(description="a downloader/installer for SteamGrid collections")
	parser.add_argument("collectionID", metavar="collection ID", help="The ID of the SteamgridDB collection you want to install. You can find this at the end of the URL when viewing a collection in a browser.")
	parser.add_argument(
		"-o",
		"--output-directory",
		default=os.path.join(os.environ["HOME"], ".local", "share", "Steam", "userdata"),
		dest="outputDirectory",
		help="Sets the output directory. The default location is to look for a Steam user under ~/.local/share/Steam/userdata and place it there. This must be the path to the directory containing Steam users - NOT the folder where you want the grids to go!"
	)
	parser.add_argument(
		"-O",
		"--override",
		help="Format: 'name=ID'. Overrides an association between a (SteamgridDB) game name and a numeric (Steam) game ID. This is useful when the closest match is incorrect or when a game is unlisted (e.g. The 7th Guest) and we won't be able to find it through the Steam API, or for non-Steam games.",
		action="append",
	)
	args = parser.parse_args()

	try:
		outDir = locateOrCreateGridFolder(args.outputDirectory)
	except (FileExistsError, FileNotFoundError) as e:
		print(e, file=sys.stderr)
		return 3

	overrides = dict[str, int]()
	for override in args.override if args.override else []:
		kv = override.split("=")
		if len(kv) != 2:
			print("invalid override:", override, file=sys.stderr)
			print("format is 'name=ID'", file=sys.stderr)
			return 4
		try:
			value = int(kv[1].strip(), 10)
		except ValueError as e:
			print("invalid override '", override, "': ", e, sep="", file=sys.stderr)
			print("game ID must be numeric", file=sys.stderr)
			return 4
		
		overrides[kv[0]] = value

	try:
		assets = getAssets(args.collectionID, "grid", overrides)
	except ParseError as e:
		print("getting collection grids:", e, file=sys.stderr)
		return 1
	except RequestError as e:
		print("getting collection grids:", e, file=sys.stderr)
		return 2

	try:
		assets.extend(getAssets(args.collectionID, "hero", overrides))
	except ParseError as e:
		print("getting collection heroes:", e, file=sys.stderr)
		return 1
	except RequestError as e:
		print("getting collection heroes:", e, file=sys.stderr)
		return 2
	
	try:
		logos = getAssets(args.collectionID, "logo", overrides)
	except ParseError as e:
		print("getting collection logos", e, file=sys.stderr)
		return 1
	except RequestError as e:
		print("getting collection logos:", e, file=sys.stderr)
		return 2

	itemNo = 0
	total = len(assets) + len(logos)
	for asset, item in assets:
		itemNo += 1
		printProgressBar(itemNo, total)
		if item is None:
			print("Warning: skipping apparent non-Steam game:", asset.game.name, file=sys.stderr)
		else:
			try:
				writeAsset(asset, item.id, outDir)
			except WriteAssetError as e:
				print(f"Error: skipping asset #", asset.id, " for game '", asset.game.name, "' due to error: ", e, file=sys.stderr)

	for asset, item in logos:
		itemNo += 1
		printProgressBar(itemNo, total)
		if item is None:
			print("Warning: skipping apparent non-Steam game:", asset.game.name, file=sys.stderr)
		else:
			try:
				writeAsset(asset, item.id, outDir, isLogo=True)
			except WriteAssetError as e:
				print(f"Error: skipping asset #", asset.id, " for game '", asset.game.name, "' due to error: ", e, file=sys.stderr)

	return 0

if __name__ == "__main__":
	sys.exit(main())