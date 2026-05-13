# Copyright 2026 ocket8888
# This file is part of steamgridinstaller.
# steamgridinstaller is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# steamgridinstaller is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with steamgridinstaller. If not, see <https://www.gnu.org/licenses/>.

import os as _os
from typing import AnyStr as _AnyStr, Final as _Final

import requests as _requests

from .model import Asset as _Asset

_MIME_EXT_MAP: _Final[dict[str, str]] = {
	"image/png": ".png",
	"image/webp": ".png",
	"image/jpg": ".jpg",
	"image/jpeg": ".jpg",
}

class WriteAssetError(Exception):
	"""
	represents an error that occurred trying to write a Steam grid asset to disk.
	"""

def getExtFromMime(mime: str) -> str:
	if not mime.startswith("image/"):
		raise TypeError(f"non-image or unrecognized MIME type: {mime}")

	try:
		return _MIME_EXT_MAP[mime.split(";")[0].strip()]
	except KeyError as e:
		raise TypeError(f"unsupported image MIME type: {mime}")

def locateOrCreateGridFolder(start: str, debug: bool) -> str:
	"""
	given a starting location, finds the grids folder. If it does not exist, it
	will be created.
	"""
	found: str | None = None
	for entry in _os.scandir(start):
		if entry.is_dir():
			if debug:
				print("found steam user folder:", entry.path)
			found = entry.path

	if found is None:
		raise FileNotFoundError("no steam user folders exist in the given directory")

	found = _os.path.join(found, "config")
	if not _os.path.isdir(found):
		raise FileNotFoundError("steam user directory does not contain 'config' dir")

	found = _os.path.join(found, "grid")

	if not _os.path.exists(found):
		_os.mkdir(found)
	elif not _os.path.isdir(found):
		raise FileExistsError(f"'{found}' exists but is not a directory")

	return found

def eraseExisting(fname: str, debug: bool):
	"""
	Erases any existing files that correspond to the same game as `fname`.
	"""
	base = fname.removesuffix(".jpg").removesuffix(".png")
	for ext in ["jpg", "JPG", "jpeg", "JPEG", "png", "PNG"]:
		existing = f"{base}.{ext}"
		if _os.path.exists(existing):
			if debug:
				print("removing existing file:", existing)
			_os.remove(existing)

def writeAsset(asset: _Asset, id: int, path: str, debug: bool, isLogo: bool = False):
	"""
	Writes the given asset to a steam grid file.
	"""
	fname = _os.path.join(path, f"{id}")
	if isLogo:
		if debug:
			print("game", id, f"({asset.game.name}) is logo")
		fname = f"{fname}_logo"
	elif asset.width == 600 and asset.height == 900:
		if debug:
			print("game", id, f"({asset.game.name}) is cover")
		fname = f"{fname}p"
	elif (asset.width == 3840 and asset.height == 1240) or (asset.width == 1920 and asset.height == 620):
		if debug:
			print("game", id, f"({asset.game.name}) is wide cover")
		fname = f"{fname}_hero"
	elif (asset.width != 920 or asset.height != 430) and (asset.width != 460 or asset.height != 215):
		raise WriteAssetError(f"unsupported dimensions for game asset: {asset.height}x{asset.width}")

	try:
		fname = f"{fname}{getExtFromMime(asset.mime)}"
	except TypeError as e:
		raise WriteAssetError(f"failed to get extension from mime type '{asset.mime}': {e}") from e

	url = asset.url
	if asset.animationType == "WebP":
		if asset.fakePng is None:
			raise WriteAssetError("WebP-animated assets must provide a fake PNG URL")
		if debug:
			print("asset is a webp - using fakePng URL")
		url = asset.fakePng

	if debug:
		print("fetching resource from:", url)

	try:
		data = _requests.get(url).content
	except (_requests.exceptions.RequestException, IOError) as e:
		raise WriteAssetError(f"failed to fetch asset data: {e}") from e

	try:
		eraseExisting(fname, debug)
		if debug:
			print("writing asset to file:", fname)
		with open(fname, 'wb') as fd:
			fd.write(data)
	except OSError as e:
		raise WriteAssetError(f"failed to write game asset data to disk: {e}") from e
	finally:
		if debug:
			print()
