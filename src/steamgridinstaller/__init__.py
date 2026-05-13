#!/usr/bin/python3

# Copyright 2026 ocket8888
# This file is part of steamgridinstaller.
# steamgridinstaller is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# steamgridinstaller is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with steamgridinstaller. If not, see <https://www.gnu.org/licenses/>.

import sys as _sys
from argparse import ArgumentParser as _ArgumentParser
import os as _os
from importlib import metadata as _metadata

from .api import getAssets as _getAssets, ParseError as _ParseError, RequestError as _RequestError
from .fs import locateOrCreateGridFolder as _locateOrCreateGridFolder, writeAsset as _writeAsset, WriteAssetError as _WriteAssetError
from .progress import printProgressBar as _printProgressBar

__version__ = _metadata.version(__package__)

def main() -> int:
	parser = _ArgumentParser(
		description="A downloader/installer for SteamGrid collections",
		epilog="%(prog)s will attempt to find games that closely resemble the names on SteamGridDB. For example, the game listed on SteamGridDB as 'Ace Combat 7: Skies Unknown' is known to Steam as 'ACE COMBAT™ 7: SKIES UNKNOWN'. " +
			"%(prog)s will resolve this, but it will issue a warning letting you know it has done so. It may get things wrong and may fail to find some unlisted games. "+
			"To fix this, you must use the -O/--override option to manually specify the ID. Although I've gone to great pains to ensure that this doesn't happen (except for unlisted games nothing I can do about that) so hopefully you won't need to."
	)
	parser.add_argument("collectionID", metavar="collection ID", help="The ID of the SteamgridDB collection you want to install. You can find this at the end of the URL when viewing a collection in a browser.")
	parser.add_argument(
		"-o",
		"--output-directory",
		default=_os.path.join(_os.environ["HOME"], ".local", "share", "Steam", "userdata"),
		dest="outputDirectory",
		help="Sets the output directory. The default location is to look for a Steam user under ~/.local/share/Steam/userdata and place it there. This must be the path to the directory containing Steam users - NOT the folder where you want the grids to go!"
	)
	parser.add_argument(
		"-O",
		"--override",
		help="Overrides an association between a (SteamgridDB) game name or numeric asset ID and a numeric (Steam) game ID. " +
			"This is useful when the closest match is incorrect or when a game is unlisted (e.g. The 7th Guest) and we won't be able to find it through the Steam API, or for non-Steam games. " +
			"Using a numeric asset ID to override an asset for a steam ID can be useful when two games in your library share a name (e.g. Dead Space and its 2022 remake with the same name) or " +
			"when you want most assets associated with a particular game to be used for that game but you want to use a background listed for it with some other game.",
		nargs=2,
		action="append",
		metavar=("GAME_NAME_OR_ASSET_ID", "STEAM_ID")
	)
	parser.add_argument("-v", "--version", action="version", version=__version__, help="Print version information and exit.")
	parser.add_argument("--debug", help="Logs a lot of debugging information to the console.", action="store_true", default=False)
	args = parser.parse_args()

	try:
		outDir = _locateOrCreateGridFolder(args.outputDirectory, args.debug)
	except (FileExistsError, FileNotFoundError) as e:
		print(e, file=_sys.stderr)
		return 3

	overrides = dict[str | int, int]()
	for (override, ID) in args.override if args.override else []:
		key: str | int
		try:
			key = int(override)
		except ValueError:
			key = override

		try:
			value = int(ID, 10)
		except ValueError as e:
			print("invalid override '", override, " -> ", ID, "': ", e, sep="", file=_sys.stderr)
			print("steam game ID must be numeric", file=_sys.stderr)
			return 4

		overrides[key] = value

	if args.debug:
		print("Overrides:")
		print(*(f"{key}: {value}" for key, value in overrides.items()), sep="\n")

	try:
		assets = _getAssets(args.collectionID, "grid", overrides, args.debug)
	except _ParseError as e:
		print("getting collection grids:", e, file=_sys.stderr)
		return 1
	except _RequestError as e:
		print("getting collection grids:", e, file=_sys.stderr)
		return 2

	try:
		assets.extend(_getAssets(args.collectionID, "hero", overrides, args.debug))
	except _ParseError as e:
		print("getting collection heroes:", e, file=_sys.stderr)
		return 1
	except _RequestError as e:
		print("getting collection heroes:", e, file=_sys.stderr)
		return 2

	try:
		logos = _getAssets(args.collectionID, "logo", overrides, args.debug)
	except _ParseError as e:
		print("getting collection logos", e, file=_sys.stderr)
		return 1
	except _RequestError as e:
		print("getting collection logos:", e, file=_sys.stderr)
		return 2

	print()
	itemNo = 0
	total = len(assets) + len(logos)
	for asset, item in assets:
		itemNo += 1
		_printProgressBar(itemNo, total, args.debug)
		if item is None:
			print("Warning: skipping apparent non-Steam game:", asset.game.name, file=_sys.stderr)
			print()
		else:
			try:
				_writeAsset(asset, item.id, outDir, args.debug)
			except _WriteAssetError as e:
				print(f"Error: skipping asset #", asset.id, " for game '", asset.game.name, "' due to error: ", e, file=_sys.stderr)
				print()

	for asset, item in logos:
		itemNo += 1
		_printProgressBar(itemNo, total, args.debug)
		if item is None:
			print("Warning: skipping apparent non-Steam game:", asset.game.name, file=_sys.stderr)
			print()
		else:
			try:
				_writeAsset(asset, item.id, outDir, args.debug, isLogo=True)
			except _WriteAssetError as e:
				print(f"Error: skipping asset #", asset.id, " for game '", asset.game.name, "' due to error: ", e, file=_sys.stderr)
				print()

	return 0

if __name__ == "__main__":
	_sys.exit(main())
