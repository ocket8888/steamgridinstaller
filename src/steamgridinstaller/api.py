from .model import Asset, AssetRequest, AssetResponse
import requests
import json

class RequestError(Exception):
	"""
	Represents an error that occurred making an API request - before parsing.
	"""

class ParseError(ValueError):
	"""
	Represents an error that occurred parsing a response from the API.
	"""

def getAssets(collectionID: str) -> list[Asset]:
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

	return parsed.data.assets