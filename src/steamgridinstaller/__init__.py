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
	args = parser.parse_args()
	try:
		assets = getAssets(args.collectionID)
	except ParseError as e:
		print(e, file=sys.stderr)
		return 1
	except RequestError as e:
		print(e, file=sys.stderr)
		return 2

	try:
		outDir = locateOrCreateGridFolder(args.outputDirectory)
	except (FileExistsError, FileNotFoundError) as e:
		print(e, file=sys.stderr)
		return 3

	for asset, item in assets:
		if item is None:
			print("Warning: skipping apparent non-Steam game:", asset.game.name, file=sys.stderr)
		else:
			try:
				writeAsset(asset, item.id, outDir)
			except WriteAssetError as e:
				print(f"Error: skipping asset #", asset.id, " for game '", asset.game.name, "' due to error: ", e, file=sys.stderr)

	return 0

if __name__ == "__main__":
	sys.exit(main())