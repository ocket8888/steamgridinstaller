#!/usr/bin/python3

import sys
from argparse import ArgumentParser

import requests
import os

from .api import getAssets, ParseError, RequestError
from .fs import locateOrCreateGridFolder, writeAsset, WriteAssetError

def main() -> int:
	parser = ArgumentParser(description="a downloader/installer for SteamGrid collections")
	parser.add_argument("collectionID", metavar="collection ID")
	parser.add_argument("-o", "--output-directory", default=os.path.join(os.environ["HOME"], ".local", "share", "Steam", "userdata"), dest="outputDirectory")
	parser.add_argument(
		"-O",
		"--override",
		help="Format: 'name=ID'. Overrides an association between a (Steamgriddb) game name and a numeric (Steam) game ID. This is useful when the closest match is incorrect or when a game is unlisted (e.g. The 7th Guest) and we wont be able to find it through the Steam API, or for non-steam games",
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

	for asset, item in assets:
		if item is None:
			print("Warning: skipping apparent non-Steam game:", asset.game.name, file=sys.stderr)
		else:
			try:
				writeAsset(asset, item.id, outDir)
			except WriteAssetError as e:
				print(f"Error: skipping asset #", asset.id, " for game '", asset.game.name, "' due to error: ", e, file=sys.stderr)

	for asset, item in logos:
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