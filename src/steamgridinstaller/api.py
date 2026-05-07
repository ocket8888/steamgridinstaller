from .model import Asset, AssetRequest, AssetResponse, SteamItem, SteamItemsResponse
import requests
import json
import sys

class RequestError(Exception):
	"""
	Represents an error that occurred making an API request - before parsing.
	"""

class ParseError(ValueError):
	"""
	Represents an error that occurred parsing a response from the API.
	"""

def getSteamGameInfo(name: str) -> SteamItem:
	"""
	gets the steam info for a game given its name
	"""
	try:
		response = requests.get(f"https://store.steampowered.com/api/storesearch/?term={name.replace(" ", "+")}&l=english&cc=US")
		parsed = SteamItemsResponse.fromJSON(response.json())
	except (requests.exceptions.RequestException, IOError) as e:
		raise RequestError(f"failed to request steam game infor for '{name}': {e}") from e
	except (ValueError, TypeError) as e:
		raise ParseError(f"failed to parse response for steam game info request for '{name}': {e}") from e

	item: SteamItem | None = None
	for itm in parsed.items:
		if itm.name == name:
			if item is not None:
				raise ValueError(f"duplicate items found with name '{name}'")
			item = itm

	if item is None:
		if len(parsed.items) > 0:
			print("selecting an arbitrary entry for game '", name, "' with no exact match found", sep="", file=sys.stderr)
			item = parsed.items[0]
		else:
			raise ValueError(f"no steam game found by name '{name}'")

	return item

def getAssets(collectionID: str) -> list[tuple[Asset, SteamItem | None]]:
	data = AssetRequest(collectionID, "grid", 0, 0, None, None)
	try:
		response = requests.post("https://www.steamgriddb.com/api/public/search/assets", json=data._asdict())
		raw = response.json()
	except (requests.exceptions.RequestException, IOError) as e:
		raise RequestError(f"failed to request grids: {e}") from e
		
	try:
		parsed = AssetResponse.fromJSON(raw)
	except (ValueError, TypeError) as e:
		raise ParseError(f"failed to parse asset response: {e}") from e

	assets = list[tuple[Asset, SteamItem | None]]()
	for asset in parsed.data.assets:
		item: SteamItem | None = None
		try:
			item = getSteamGameInfo(asset.game.name)
		except (ValueError) as e:
			print("skipping apparent non-steam game '", asset.game.name, "': ", e, file=sys.stderr, sep="")

		assets.append((asset, item))

	return assets