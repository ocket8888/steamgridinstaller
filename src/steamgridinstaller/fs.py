import os
from typing import AnyStr, Final

import requests

from .model import Asset

_MIME_EXT_MAP: Final[dict[str, str]] = {
	"image/png": ".png",
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

def locateOrCreateGridFolder(start: str) -> str:
	"""
	given a starting location, finds the grids folder. If it does not exist, it
	will be created.
	"""
	found: str | None = None
	for entry in os.scandir(start):
		if entry.is_dir():
			found = entry.path
	
	if found is None:
		raise FileNotFoundError("no steam user folders exist in the given directory")
	
	found = os.path.join(found, "config")
	if not os.path.isdir(found):
		raise FileNotFoundError("steam user directory does not contain 'config' dir")
	
	found = os.path.join(found, "grid")

	if not os.path.exists(found):
		os.mkdir(found)
	elif not os.path.isdir(found):
		raise FileExistsError(f"'{found}' exists but is not a directory")

	return found

def writeAsset(asset: Asset, id: int, dir: str):
	"""
	Writes the given asset to a steam grid file.
	"""
	fname = os.path.join(dir, f"{id}")
	if asset.width == 600 and asset.height == 900:
		fname = f"{fname}p"
	elif (asset.width == 3840 and asset.height == 1240) or (asset.width == 1920 and asset.height == 620):
		fname = f"{fname}_hero"
	elif (asset.width != 920 or asset.height != 430) and (asset.width != 460 or asset.height != 215):
		raise WriteAssetError(f"unsupported dimensions for game asset: {asset.height}x{asset.width}")
	
	try:
		fname = f"{fname}.{getExtFromMime(asset.mime)}"
	except TypeError as e:
		raise WriteAssetError(f"failed to get extension from mime type '{asset.mime}': {e}") from e
	
	try:
		data = requests.get(asset.url).content
	except (requests.exceptions.RequestException, IOError) as e:
		raise WriteAssetError(f"failed to fetch asset data: {e}") from e
	
	try:
		with open(fname, 'wb') as fd:
			fd.write(data)
	except OSError as e:
		raise WriteAssetError(f"failed to write game asset data to disk: {e}") from e
