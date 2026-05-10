# Copyright 2026 ocket8888
# This file is part of steamgridinstaller.
# steamgridinstaller is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# steamgridinstaller is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with steamgridinstaller. If not, see <https://www.gnu.org/licenses/>. 

import json
import sys
from typing import Final, Literal
from difflib import SequenceMatcher
from re import Match, compile as compileRegExp

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

_ARABIC_TO_ROMAN: Final[dict[str, str]] = {
	 "1": "I",
	 "2": "II",
	 "3": "III",
	 "4": "IV",
	 "5": "V",
	 "6": "VI",
	 "7": "VII",
	 "8": "VIII",
	 "9": "IX",
	"10": "X",
	"11": "XI",
	"12": "XII",
	"13": "XIII",
	"14": "XIV",
	"15": "XV",
	"16": "XVI",
	"17": "XVII",
	"18": "XVIII",
	"19": "XIX",
	"20": "XX",
	# if i truly need more than this i should just write a parser
}

_NUMERAL_PATTERN = compileRegExp(r"\b\d+\b")
def _replacer(match: Match) -> str:
	span = match.span()
	arabic = match.string[span[0]:span[1]]
	if arabic in _ARABIC_TO_ROMAN:
		return _ARABIC_TO_ROMAN[arabic]
	return arabic

def _replaceNumerals(title: str) -> tuple[str, bool]:
	"""
	Replaces all numerals found in the title with their Roman equivalent.
	Reports the string after replacement along with whether any replacement was actually done.
	Only considers numerals which are their own word - e.g. 'Arma 2' will become 'Arma II',
	but 'Se7en' will be given back as `('Se7en', False)`.
	"""
	out, count = _NUMERAL_PATTERN.subn(_replacer, title)
	return out, count > 0

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

def getSteamGameInfo(name: str, overrides: dict[str, int], alreadyReplaced: bool = False) -> SteamItem:
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
		if not alreadyReplaced:
			replaced, didReplace = _replaceNumerals(name)
			if didReplace:
				print(f"Warning: no matches found for steam game by name '{name}' - trying '{replaced}' instead", file=sys.stderr)
				return getSteamGameInfo(replaced, overrides, True)
		raise ValueError(f"no steam game found by name '{name}'")
	
	if item.name.casefold() != nm:
		print("Warning: selecting best match for", f"'{name}':", item.name, file=sys.stderr)

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
