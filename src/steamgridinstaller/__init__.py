#!/usr/bin/python3

import sys
from argparse import ArgumentParser

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

	for asset in assets:
		print(asset.game.name, f"(#{asset.game.id})", f"{asset.height}x{asset.width}")

	return 0

if __name__ == "__main__":
	sys.exit(main())