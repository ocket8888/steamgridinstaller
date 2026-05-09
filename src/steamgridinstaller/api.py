import json
import sys
from typing import Final, Literal
from difflib import SequenceMatcher

import requests

from .model import Asset, AssetRequest, AssetResponse, SteamItem, SteamItemsResponse, SteamPlatforms

class RequestError(Exception):
	"""
	Represents an error that occurred making an API request - before parsing.
	"""

class ParseError(ValueError):
	"""
	Represents an error that occurred parsing a response from the API.
	"""

def _editDistance(a: str, b: str) -> int:
	"""
	Calculates the edit distance between a and b.
	"""
	dist = 0
	for code in SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
		if code[0] != "equal":
			++dist
	
	return dist

_STEAM_CACHE: Final[dict[str, SteamItem]] = {}

def getSteamGameInfo(name: str, overrides: dict[str, int]) -> SteamItem:
	"""
	gets the steam info for a game given its name
	"""
	if name in _STEAM_CACHE:
		return _STEAM_CACHE[name]

	if name in overrides:
		ret = SteamItem(
			"app",
			name,
			overrides[name],
			None,
			"OVERRIDDEN",
			"",
			SteamPlatforms(False, False, False),
			False,
			None,
		)
		_STEAM_CACHE[name] = ret
		return ret

	try:
		response = requests.get(f"https://store.steampowered.com/api/storesearch/?term={name.replace(" ", "+")}&l=english&cc=US")
		parsed = SteamItemsResponse.fromJSON(response.json())
	except (requests.exceptions.RequestException, IOError) as e:
		raise RequestError(f"failed to request steam game infor for '{name}': {e}") from e
	except (ValueError, TypeError) as e:
		raise ParseError(f"failed to parse response for steam game info request for '{name}': {e}") from e

	nm = name.casefold()
	item: SteamItem | None = None
	minDist = float("inf")
	for itm in parsed.items:
		iname = itm.name.casefold()
		if iname == nm:
			if item is not None and item.name.casefold() == nm:
				raise ValueError(f"duplicate items found with name '{name}'")
			item = itm
			minDist = -1
		else:
			editDist = _editDistance(iname, nm)
			if editDist < minDist:
				minDist = editDist
				item = itm

	if item is None:
		raise ValueError(f"no steam game found by name '{name}'")
	
	if item.name.casefold() != nm:
		print("Warning: selecting best match for", f"'{name}':", item.name)

	_STEAM_CACHE[name] = item

	return item

def getAssets(collectionID: str, typ: Literal["grid", "logo", "hero"], overrides: dict[str, int]) -> list[tuple[Asset, SteamItem | None]]:
	data = AssetRequest(collectionID, typ, 0, 0, None, None)
	try:
		response = requests.post("https://www.steamgriddb.com/api/public/search/assets", json=data._asdict())
		raw = response.json()
	except (requests.exceptions.RequestException, IOError) as e:
		raise RequestError(f"failed to request grids: {e}") from e
		
	try:
		parsed = AssetResponse.fromJSON(raw)
	except (ValueError, TypeError) as e:
		raise ParseError(f"failed to parse asset response: {e}") from e

	print("found", len(parsed.data.assets), f"{typ}{'es' if typ == 'hero' else 's'}")

	assets = list[tuple[Asset, SteamItem | None]]()
	for asset in parsed.data.assets:
		item: SteamItem | None = None
		try:
			item = getSteamGameInfo(asset.game.name, overrides)
		except (ValueError) as e:
			print("skipping apparent non-steam game '", asset.game.name, "': ", e, file=sys.stderr, sep="")

		assets.append((asset, item))

	return assets