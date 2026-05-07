#!/usr/bin/python3

import sys
from argparse import ArgumentParser

import requests

from .api import getAssets, ParseError, RequestError

def main() -> int:
	parser = ArgumentParser(description="a downloader/installer for SteamGrid collections")
	parser.add_argument("collectionID", metavar="collection ID")
	args = parser.parse_args()
	try:
		assets = getAssets(args.collectionID)
	except ParseError as e:
		print(e, file=sys.stderr)
		return 1
	except RequestError as e:
		print(e, file=sys.stderr)
		return 2

	for asset, item in assets:
		dims = f"{asset.height}x{asset.width}"
		if item is None:
			print(asset.game.name, "NON-STEAM", dims)
		else:
			print(asset.game.name, f"(#{item.id})", dims)

	return 0

if __name__ == "__main__":
	sys.exit(main())