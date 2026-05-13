# Copyright 2026 ocket8888
# This file is part of steamgridinstaller.
# steamgridinstaller is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# steamgridinstaller is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with steamgridinstaller. If not, see <https://www.gnu.org/licenses/>.

from typing import NamedTuple, Literal
from datetime import datetime
import json

class AssetRequest(NamedTuple):
	"""
	Specification for the request of an asset or list of assets.
	"""
	collection_id: str
	asset_type: Literal["grid", "logo", "hero"]
	page: int
	limit: int
	user_steam64: None
	user_steam64_likes: None

class Badge(NamedTuple):
	id: int
	name: str
	description: str
	date: datetime
	isHidden: bool

	@staticmethod
	def fromJSON(raw: object) -> Badge:
		if not isinstance(raw, dict):
			raise TypeError("non-object was given as asset author badge")
		if len(raw) != 5:
			raise ValueError(f"incorrect number of properties in asset author badge; expected: 5, got: {len(raw)}")

		if "id" not in raw:
			raise ValueError("asset author badge missing required property 'id'")
		if not isinstance(raw["id"], int):
			raise TypeError("invalid type for asset author badge property 'id'")

		if "name" not in raw:
			raise ValueError("asset author badge missing required property 'name'")
		if not isinstance(raw["name"], str):
			raise TypeError("invalid type for asset author badge property 'name'")

		if "description" not in raw:
			raise ValueError("asset author badge missing required property 'description'")
		if not isinstance(raw["description"], str):
			raise TypeError("invalid type for asset author badge property 'description'")

		if "date" not in raw:
			raise ValueError("asset author badge missing required property 'date'")
		if not isinstance(raw["date"], int):
			raise TypeError("invalid type for asset author badge property 'date'")
		date = datetime.fromtimestamp(raw["date"])

		if "isHidden" not in raw:
			raise ValueError("asset author badge missing required property 'isHidden'")
		if not isinstance(raw["isHidden"], bool):
			raise TypeError("invalid type for asset author badge property 'isHidden'")

		return Badge(
			raw["id"],
			raw["name"],
			raw["description"],
			date,
			raw["isHidden"],
		)

class AssetAuthor(NamedTuple):
	name: str
	steam64: str
	avatar: str
	badges: list[Badge]

	@staticmethod
	def fromJSON(raw: object) -> AssetAuthor:
		if not isinstance(raw, dict):
			raise TypeError("non-object was given as asset author")
		if len(raw) != 4:
			raise ValueError(f"incorrect number of properties in asset author; expected: 4, got: {len(raw)}")

		if "name" not in raw:
			raise ValueError("asset author missing required property 'name'")
		if not isinstance(raw["name"], str):
			raise TypeError("incorrect type for 'name' property of asset author")

		if "steam64" not in raw:
			raise ValueError("asset author missing required property 'steam64'")
		if not isinstance(raw["steam64"], str):
			raise TypeError("incorrect type for 'steam64' property of asset author")

		if "avatar" not in raw:
			raise ValueError("asset author missing required property 'avatar'")
		if not isinstance(raw["avatar"], str):
			raise TypeError("incorrect type for 'avatar' property of asset author")

		if "badges" not in raw:
			raise ValueError("asset author missing required property 'badges'")
		if not isinstance(raw["badges"], list):
			raise TypeError("incorrect type for 'badges' property of asset author")
		badges = list[Badge]()
		for i, badge in enumerate(raw["badges"]):
			try:
				badges.append(Badge.fromJSON(badge))
			except (ValueError, TypeError) as e:
				raise TypeError(f"invalid badge in asset author at index {i}: {e}")

		return AssetAuthor(
			raw["name"],
			raw["steam64"],
			raw["avatar"],
			badges,
		)

class GameInfo(NamedTuple):
	id: int
	name: str
	releaseDate: datetime
	types: list[None]
	verified: bool

	def withName(self: GameInfo, name: str) -> GameInfo:
		"""
		Returns a copy of the game with its name changed to the given value - to hopefully match Steam's name for it better.

		>>> import datetime
		>>> gi = GameInfo(1, "test", datetime.datetime(1, 1, 1, 0, 0), [], False)
		>>> gi = gi.withName("quest")
		>>> gi.id
		1
		>>> gi.name
		'quest'
		>>> gi.releaseDate
		datetime.datetime(1, 1, 1, 0, 0)
		>>> gi.types
		[]
		>>> gi.verified
		False
		"""
		return GameInfo(
			self.id,
			name,
			self.releaseDate,
			self.types,
			self.verified,
		)

	@staticmethod
	def fromJSON(raw: object) -> GameInfo:
		if not isinstance(raw, dict):
			raise TypeError("non-object was given as asset gameinfo")
		if len(raw) != 5:
			raise ValueError(f"incorrect number of properties in asset gameinfo; expected: 5, got: {len(raw)}")

		if "id" not in raw:
			raise ValueError("game info missing required property 'id'")
		if not isinstance(raw["id"], int):
			raise TypeError("invalid type for game info property 'id'")

		if "name" not in raw:
			raise ValueError("game info missing required property 'name'")
		if not isinstance(raw["name"], str):
			raise TypeError("invalid type for game info property 'name'")

		if "release_date" not in raw:
			raise ValueError("game info missing required property 'release_date'")
		if not isinstance(raw["release_date"], int):
			raise TypeError("invalid type for game info property 'release_date'")
		releaseDate = datetime.fromtimestamp(raw["release_date"])

		if "types" not in raw:
			raise ValueError("game info missing required property 'types'")
		if not isinstance(raw["types"], list):
			raise TypeError("invalid type for game info property 'types'")
		types = list[None]()
		for i, t in enumerate(raw["types"]):
			if t is not None:
				raise ValueError(f"found a type value at index {i} in game info types")
			types.append(t)

		if "verified" not in raw:
			raise ValueError("game info missing required property 'verified'")
		if not isinstance(raw["verified"], bool):
			raise TypeError("invalid type for game info property 'verified'")

		return GameInfo(
			raw["id"],
			raw["name"],
			releaseDate,
			types,
			raw["verified"],
		)

class Asset(NamedTuple):
	id: int
	style: str
	width: int
	height: int
	nsfw: bool
	humor: bool
	notes: None | str
	language: str
	url: str
	thumb: str
	lock: bool
	epilepsy: bool
	upvotes: int
	downvotes: int
	downloads: int
	hearts: int
	canVote: bool
	date: datetime
	mime: str
	isAnimated: bool
	isDeleted: bool
	animationType: None | str
	processing: bool
	showBoop: bool
	author: AssetAuthor
	game: GameInfo
	fakePng: str | None
	isUpvoted: bool | None
	isDownvoted: bool | None
	isHearted: bool | None
	canReport: bool | None
	canCollect: bool | None

	def withName(self: Asset, name: str) -> Asset:
		"""
		Returns a copy of the Asset with the game name changed - to hopefully match Steam's name for it better.

		>>> import datetime
		>>> gi = GameInfo(1, "test", datetime.datetime.now(), [], False)
		>>> a = Asset(1, "", 1, 1, False, False, None, "", "", "", False, False, 0, 0, 0, 0, False, datetime.datetime.now(), "", False, False, None, False, False, AssetAuthor("", "", "", []), gi, None, None, None, None, None, None)
		>>> a = a.withName("quest")
		>>> a.game.name
		'quest'
		"""
		return Asset(
			self.id,
			self.style,
			self.width,
			self.height,
			self.nsfw,
			self.humor,
			self.notes,
			self.language,
			self.url,
			self.thumb,
			self.lock,
			self.epilepsy,
			self.upvotes,
			self.downvotes,
			self.downloads,
			self.hearts,
			self.canVote,
			self.date,
			self.mime,
			self.isAnimated,
			self.isDeleted,
			self.animationType,
			self.processing,
			self.showBoop,
			self.author,
			self.game.withName(name),
			self.fakePng,
			self.isUpvoted,
			self.isDownvoted,
			self.isHearted,
			self.canReport,
			self.canCollect,
		)

	@staticmethod
	def fromJSON(raw: object) -> Asset:
		if not isinstance(raw, dict):
			raise TypeError("non-object given as an asset")
		if len(raw) not in {26, 27, 31, 32}:
			raise ValueError(f"incorrect number of properties in asset; expected: 26 or 27 or 31 or 322, got: {len(raw)}")

		if "id" not in raw:
			raise ValueError("asset missing required property 'id'")
		if not isinstance(raw["id"], int):
			raise TypeError("invalid type for 'id' property of asset")

		if "style" not in raw:
			raise ValueError("asset missing required property 'style'")
		if not isinstance(raw["style"], str):
			raise TypeError("invalid type for 'style' property of asset")

		if "width" not in raw:
			raise ValueError("asset missing required property 'width'")
		if not isinstance(raw["width"], int):
			raise TypeError("invalid type for 'width' property of asset")

		if "height" not in raw:
			raise ValueError("asset missing required property 'height'")
		if not isinstance(raw["height"], int):
			raise TypeError("invalid type for 'height' property of asset")

		if "nsfw" not in raw:
			raise ValueError("asset missing required property 'nsfw'")
		if not isinstance(raw["nsfw"], bool):
			raise TypeError("invalid type for 'nsfw' property of asset")

		if "humor" not in raw:
			raise ValueError("asset missing required property 'humor'")
		if not isinstance(raw["humor"], bool):
			raise TypeError("invalid type for 'humor' property of asset")

		if "notes" not in raw:
			raise ValueError("asset missing required property 'notes'")
		if raw["notes"] is not None and not isinstance(raw["notes"], str):
			raise TypeError("invalid type for 'notes' property of asset")

		if "language" not in raw:
			raise ValueError("asset missing required property 'language'")
		if not isinstance(raw["language"], str):
			raise TypeError("invalid type for 'language' property of asset")

		if "url" not in raw:
			raise ValueError("asset missing required property 'url'")
		if not isinstance(raw["url"], str):
			raise TypeError("invalid type for 'url' property of asset")

		if "thumb" not in raw:
			raise ValueError("asset missing required property 'thumb'")
		if not isinstance(raw["thumb"], str):
			raise TypeError("invalid type for 'thumb' property of asset")

		if "lock" not in raw:
			raise ValueError("asset missing required property 'lock'")
		if not isinstance(raw["lock"], bool):
			raise TypeError("invalid type for 'lock' property of asset")

		if "epilepsy" not in raw:
			raise ValueError("asset missing required property 'epilepsy'")
		if not isinstance(raw["epilepsy"], bool):
			raise TypeError("invalid type for 'epilepsy' property of asset")

		if "upvotes" not in raw:
			raise ValueError("asset missing required property 'upvotes'")
		if not isinstance(raw["upvotes"], int):
			raise TypeError("invalid type for 'upvotes' property of asset")

		if "downvotes" not in raw:
			raise ValueError("asset missing required property 'downvotes'")
		if not isinstance(raw["downvotes"], int):
			raise TypeError("invalid type for 'downvotes' property of asset")

		if "downloads" not in raw:
			raise ValueError("asset missing required property 'downloads'")
		if not isinstance(raw["downloads"], int):
			raise TypeError("invalid type for 'downloads' property of asset")

		if "hearts" not in raw:
			raise ValueError("asset missing required property 'hearts'")
		if not isinstance(raw["hearts"], int):
			raise TypeError("invalid type for 'hearts' property of asset")

		if "can_vote" not in raw:
			raise ValueError("asset missing required property 'can_vote'")
		if not isinstance(raw["can_vote"], bool):
			raise TypeError("invalid type for 'can_vote' property of asset")

		if "date" not in raw:
			raise ValueError("asset missing required property 'date'")
		if not isinstance(raw["date"], int):
			raise TypeError("invalid type for 'date' property of asset")
		date = datetime.fromtimestamp(raw["date"])

		if "mime" not in raw:
			raise ValueError("asset missing required property 'mime'")
		if not isinstance(raw["mime"], str):
			raise TypeError("invalid type for 'mime' property of asset")

		if "is_animated" not in raw:
			raise ValueError("asset missing required property 'is_animated'")
		if not isinstance(raw["is_animated"], bool):
			raise TypeError("invalid type for 'is_animated' property of asset")

		if "is_deleted" not in raw:
			raise ValueError("asset missing required property 'is_deleted'")
		if not isinstance(raw["is_deleted"], bool):
			raise TypeError("invalid type for 'is_deleted' property of asset")

		if "animation_type" not in raw:
			raise ValueError("asset missing required property 'animation_type'")
		if raw["animation_type"] is not None and not isinstance(raw["animation_type"], str):
			raise ValueError(f"got a value for 'animation_type': {raw['animation_type']}")

		if "processing" not in raw:
			raise ValueError("asset missing required property 'processing'")
		if not isinstance(raw["processing"], bool):
			raise TypeError("invalid type for 'processing' property of asset")

		if "show_boop" not in raw:
			raise ValueError("asset missing required property 'show_boop'")
		if not isinstance(raw["show_boop"], bool):
			raise TypeError("invalid type for 'show_boop' property of asset")

		if "author" not in raw:
			raise ValueError("asset missing required property 'author'")

		fakePng: None | str = None
		if "fake_png" in raw:
			if not isinstance(raw["fake_png"], str):
				raise TypeError("invalid type for 'fake_png' property of asset")
			fakePng = raw["fake_png"]

		isUpvoted: None | bool = None
		if "is_upvoted" in raw:
			if not isinstance(raw["is_upvoted"], bool):
				raise TypeError("invalid type for 'is_upvoted' property of asset")
			isUpvoted = raw["is_upvoted"]

		isDownvoted: None | bool = None
		if "is_downvoted" in raw:
			if not isinstance(raw["is_downvoted"], bool):
				raise TypeError("invalid type for 'is_downvoted' property of asset")
			isDownvoted = raw["is_downvoted"]

		isHearted: None | bool = None
		if "is_hearted" in raw:
			if not isinstance(raw["is_hearted"], bool):
				raise TypeError("invalid type for 'is_hearted' property of asset")
			isHearted = raw["is_hearted"]

		canReport: None | bool = None
		if "can_report" in raw:
			if not isinstance(raw["can_report"], bool):
				raise TypeError("invalid type for 'can_report' property of asset")
			canReport = raw["can_report"]

		canCollect: None | bool = None
		if "can_collect" in raw:
			if not isinstance(raw["can_collect"], bool):
				raise TypeError("invalid type for 'can_collect' property of asset")
			canCollect = raw["can_collect"]

		if "game" not in raw:
			raise ValueError("asset missing required property 'game'")

		return Asset(
			raw["id"],
			raw["style"],
			raw["width"],
			raw["height"],
			raw["nsfw"],
			raw["humor"],
			raw["notes"],
			raw["language"],
			raw["url"],
			raw["thumb"],
			raw["lock"],
			raw["epilepsy"],
			raw["upvotes"],
			raw["downvotes"],
			raw["downloads"],
			raw["hearts"],
			raw["can_vote"],
			date,
			raw["mime"],
			raw["is_animated"],
			raw["is_deleted"],
			raw["animation_type"],
			raw["processing"],
			raw["show_boop"],
			AssetAuthor.fromJSON(raw["author"]),
			GameInfo.fromJSON(raw["game"]),
			fakePng,
			isUpvoted,
			isDownvoted,
			isHearted,
			canReport,
			canCollect,
		)

class FilterStyleMeta(NamedTuple):
	count: int

	@staticmethod
	def fromJSON(raw: object) -> FilterStyleMeta:
		if not isinstance(raw, dict):
			raise TypeError("non-object given as response data filters style-type metadata")
		if len(raw) != 1:
			raise ValueError(f"incorrect number of properties in style-type filter metadata; expected: 1, got: {len(raw)}")

		if "count" not in raw:
			raise ValueError("style-type filter metadata missing required 'count' property")
		if not isinstance(raw["count"], int):
			raise TypeError("invalid type for 'count' property of style-type filter metadata")

		return FilterStyleMeta(raw["count"])

class FilterDimensionsMeta(NamedTuple):
	ratio: tuple[int, int]
	count: int

	@staticmethod
	def fromJSON(raw: object) -> FilterDimensionsMeta:
		if not isinstance(raw, dict):
			raise TypeError("non-object given as response data filters dimensions-type metadata")
		if len(raw) != 2:
			raise ValueError(f"incorrect number of properties in dimensions-type filters metadata; expected: 2, got: {len(raw)}")

		if "count" not in raw:
			raise ValueError("dimensions-type filter metadata missing required 'count' property")
		if not isinstance(raw["count"], int):
			raise TypeError("invalid type for 'count' property of dimensions-type filter metadata")

		if "ratio" not in raw:
			raise ValueError("dimensions-type filter metadata missing required 'ratio' property")
		if not isinstance(raw["ratio"], list):
			raise TypeError("invalid type for 'ratio' property of dimensions-type filter metadata")
		if len(raw["ratio"]) != 2:
			raise ValueError(f"incorrect number of elements in dimension-style filter metadata 'ratio' property: {len(raw['ratio'])}")
		for i, r in enumerate(raw["ratio"]):
			if not isinstance(r, int):
				raise TypeError(f"invalid type for element of dimensions-style filter metadata 'ratio' property at index {i}")

		return FilterDimensionsMeta((raw["ratio"][0], raw["ratio"][1]), raw["count"])

class Filter(NamedTuple):
	style: dict[str, FilterStyleMeta]
	dimensions: dict[str, FilterDimensionsMeta] | None
	language: dict[str, FilterStyleMeta]
	mime: dict[str, FilterStyleMeta]

	@staticmethod
	def fromJSON(raw: object) -> Filter:
		if not isinstance(raw, dict):
			raise TypeError("non-object given as response data filters")
		if len(raw) != 4:
			raise ValueError(f"incorrect number of properties in response data filters; expected: 6, got: {len(raw)}")

		if "style" not in raw:
			raise ValueError("response data filters missing required property 'style'")
		if not isinstance(raw["style"], dict):
			raise TypeError("invalid type for 'style' property of response data filters")
		style = dict[str, FilterStyleMeta]()
		for s, meta in raw["style"].items():
			if not isinstance(s, str):
				raise TypeError(f"found non-string property key in response data filters style: {s}")
			try:
				style[s] = FilterStyleMeta.fromJSON(meta)
			except (TypeError, ValueError) as e:
				raise TypeError(f"found invalid metadata for style filter '{s}': {meta}")

		if "dimensions" not in raw:
			raise ValueError("response data filters missing required property 'dimensions'")

		dimensions: None | dict[str, FilterDimensionsMeta] = None
		# for logos, 'dimensions' will be an empty list (instead of an empty object?)
		if isinstance(raw["dimensions"], list):
			if len(raw["dimensions"]) != 0:
				raise ValueError(f"found non-empty list dimensions filter: {raw['dimensions']}")
		elif not isinstance(raw["dimensions"], dict):
			raise TypeError("invalid type for 'dimensions' property of response data filters")
		else:
			dimensions = dict[str, FilterDimensionsMeta]()
			for dim, meta in raw["dimensions"].items():
				if not isinstance(dim, str):
					raise TypeError(f"found non-string property key in response data filters dimensions: {dim}")
				try:
					dimensions[dim] = FilterDimensionsMeta.fromJSON(meta)
				except (TypeError, ValueError) as e:
					raise TypeError(f"found invalid metadata for dimension filter '{dim}': {e}") from e

		if "language" not in raw:
			raise ValueError("response data filters missing required property 'language'")
		if not isinstance(raw["language"], dict):
			raise TypeError("invalid type for 'language' property of response data filters")
		languages = dict[str, FilterStyleMeta]()
		for lang, meta in raw["language"].items():
			if not isinstance(lang, str):
				raise TypeError(f"found non-string property key in response data filters languages: {lang}")
			try:
				languages[lang] = FilterStyleMeta.fromJSON(meta)
			except (TypeError, ValueError) as e:
				raise TypeError(f"found invalid metadata for language filter '{lang}': {e}") from e

		if "mime" not in raw:
			raise ValueError("response data filters missing required property 'mime'")
		if not isinstance(raw["mime"], dict):
			raise TypeError("invalid type for 'mime' property of response data filters")
		mime = dict[str, FilterStyleMeta]()
		for m, meta in raw["mime"].items():
			if not isinstance(m, str):
				raise TypeError(f"found non-string property key in response data filters mime: {lang}")
			try:
				mime[m] = FilterStyleMeta.fromJSON(meta)
			except (TypeError, ValueError) as e:
				raise TypeError(f"found invalid metadata for mime filter '{m}': {e}") from e

		return Filter(style, dimensions, languages, mime)

class AssetResponseData(NamedTuple):
	hasHiddenAssets: bool
	game: None
	assets: list[Asset]
	total: int
	filters: Filter
	limit: int
	currentPage: int

	@staticmethod
	def fromJSON(raw: object) -> AssetResponseData:
		if not isinstance(raw, dict):
			raise TypeError("non-object given as asset response data")
		if len(raw) != 7:
			raise ValueError(f"invalid number of properties in response data; expected: 5, got: {len(raw)}")

		if "has_hidden_assets" not in raw:
			raise ValueError("response data missing required property 'has_hidden_assets'")
		if not isinstance(raw["has_hidden_assets"], bool):
			raise TypeError("invalid type for 'has_hidden_assets' property of response data")

		if "game" not in raw:
			raise ValueError("response data missing required property 'game'")
		if raw["game"] is not None:
			raise ValueError("got a value for 'game'")

		if "assets" not in raw:
			raise ValueError("response data missing required property 'assets'")
		if not isinstance(raw["assets"], list):
			raise TypeError("invalid type for 'assets' property of response data")

		if "total" not in raw:
			raise ValueError("response data missing required property 'total'")
		if not isinstance(raw["total"], int):
			raise TypeError("invalid type for 'total' property of response data")

		if "filters" not in raw:
			raise ValueError("response data missing required property 'filters'")

		if "limit" not in raw:
			raise ValueError("response data missing required property 'limit'")
		if not isinstance(raw["limit"], int):
			raise TypeError("invalid type for 'limit' property of response data")

		if "current_page" not in raw:
			raise ValueError("response data missing required property 'current_page'")
		if not isinstance(raw["current_page"], int):
			raise TypeError("invalid type for 'current_page' property of response data")

		assets = list[Asset]()
		for i, a in enumerate(raw["assets"]):
			try:
				assets.append(Asset.fromJSON(a))
			except (TypeError, ValueError) as e:
				raise TypeError(f"invalid asset at index {i}: {e}") from e

		return AssetResponseData(raw["has_hidden_assets"], raw["game"], assets, raw["total"], Filter.fromJSON(raw["filters"]), raw["limit"], raw["current_page"])

class AssetResponse(NamedTuple):
	"""
	SteamgridDB's response to an AssetRequest.
	"""
	success: bool
	data: AssetResponseData

	@staticmethod
	def fromJSON(raw: object) -> AssetResponse:
		"""
		constructs an AssetResponse from a raw JSON response
		"""
		if not isinstance(raw, dict):
			raise TypeError("non-object given as asset response")
		if len(raw) != 2:
			raise ValueError(f"invalid number of properties in response; expected: 2, got: {len(raw)}")

		if "success" not in raw:
			raise ValueError("asset response missing required property 'success'")
		if not isinstance(raw["success"], bool):
			raise TypeError("invalid type for 'success' property of asset response")

		if "data" not in raw:
			raise ValueError("asset response missing required property 'data'")

		return AssetResponse(raw["success"], AssetResponseData.fromJSON(raw["data"]))

class SteamPrice(NamedTuple):
	currency: str
	initial: int
	final: int

	@staticmethod
	def fromJSON(raw: object) -> SteamPrice:
		if not isinstance(raw, dict):
			raise TypeError("non-object given as steam game price")
		if len(raw) != 3:
			raise ValueError(f"invalid number of properties in steam game price; expected: 3, got: {len(raw)}")

		if "currency" not in raw:
			raise ValueError("steam game price missing required property 'currency'")
		if not isinstance(raw["currency"], str):
			raise TypeError("invalid type for 'currency' property of steam game price")

		if "initial" not in raw:
			raise ValueError("steam game price missing required property 'initial'")
		if not isinstance(raw["initial"], int):
			raise TypeError("invalid type for 'initial' property of steam game price")

		if "final" not in raw:
			raise ValueError("steam game price missing required property 'final'")
		if not isinstance(raw["final"], int):
			raise TypeError("invalid type for 'final' property of steam game price")

		return SteamPrice(raw["currency"], raw["initial"], raw["final"])

class SteamPlatforms(NamedTuple):
	windows: bool
	mac: bool
	linux: bool

	@staticmethod
	def fromJSON(raw: object) -> SteamPlatforms:
		if not isinstance(raw, dict):
			raise TypeError("non-object given as steam game platforms")
		if len(raw) != 3:
			raise ValueError(f"invalid number of properties in steam game platforms; expected: 3, got: {len(raw)}")

		if "windows" not in raw:
			raise ValueError("steam game platforms missing required property 'windows'")
		if not isinstance(raw["windows"], bool):
			raise TypeError("invalid type for 'windows' property of steam game platforms")

		if "mac" not in raw:
			raise ValueError("steam game platforms missing required property 'mac'")
		if not isinstance(raw["mac"], bool):
			raise TypeError("invalid type for 'mac' property of steam game platforms")

		if "linux" not in raw:
			raise ValueError("steam game platforms missing required property 'linux'")
		if not isinstance(raw["linux"], bool):
			raise TypeError("invalid type for 'linux' property of steam game platforms")

		return SteamPlatforms(raw["windows"], raw["mac"], raw["linux"])

class SteamItem(NamedTuple):
	type: str
	name: str
	id: int
	price: SteamPrice | None
	tinyImage: str
	metascore: str
	platforms: SteamPlatforms
	streamingVideo: bool
	controllerSupport: str | None

	@staticmethod
	def fromJSON(raw: object) -> SteamItem:
		if not isinstance(raw, dict):
			raise TypeError("non-object given as steam item")
		if len(raw) not in {7, 8, 9}:
			raise ValueError(f"invalid number of properties in steam item; expected: 7 or 8 or 9, got: {len(raw)}")

		if "type" not in raw:
			raise ValueError("steam item missing required property 'type'")
		if not isinstance(raw["type"], str):
			raise TypeError("invalid type for 'type' property of steam item")

		if "name" not in raw:
			raise ValueError("steam item missing required property 'name'")
		if not isinstance(raw["name"], str):
			raise TypeError("invalid type for 'name' property of steam item")

		if "id" not in raw:
			raise ValueError("steam item missing required property 'id'")
		if not isinstance(raw["id"], int):
			raise TypeError("invalid type for 'id' property of steam item")

		price: SteamPrice | None = None
		if "price" in raw:
			try:
				price = SteamPrice.fromJSON(raw["price"])
			except (ValueError, TypeError) as e:
				raise TypeError(f"invalid 'price' property on Steam Item: {e}") from e

		if "tiny_image" not in raw:
			raise ValueError("steam item missing required property 'tiny_image'")
		if not isinstance(raw["tiny_image"], str):
			raise TypeError("invalid type for 'tiny_image' property of steam item")

		if "metascore" not in raw:
			raise ValueError("steam item missing required property 'metascore'")
		if not isinstance(raw["metascore"], str):
			raise TypeError("invalid type for 'metascore' property of steam item")

		if "platforms" not in raw:
			raise ValueError("steam item missing required property 'platforms'")

		if "streamingvideo" not in raw:
			raise ValueError("steam item missing required property 'streamingvideo'")
		if not isinstance(raw["streamingvideo"], bool):
			raise TypeError("invalid type for 'streamingvideo' property of steam item")

		controllerSupport: str | None = None
		if "controller_support" in raw:
			if not isinstance(raw["controller_support"], str):
				raise TypeError("invalid type for 'controller_support' property of steam item")
			controllerSupport = raw["controller_support"]

		return SteamItem(
			raw["type"],
			raw["name"],
			raw["id"],
			price,
			raw["tiny_image"],
			raw["metascore"],
			SteamPlatforms.fromJSON(raw["platforms"]),
			raw["streamingvideo"],
			controllerSupport
		)

class SteamItemsResponse(NamedTuple):
	total: int
	items: list[SteamItem]

	@staticmethod
	def fromJSON(raw: object) -> SteamItemsResponse:
		if not isinstance(raw, dict):
			raise TypeError("non-object given as asset response")
		if len(raw) != 2:
			raise ValueError(f"invalid number of properties in response; expected: 2, got: {len(raw)}")

		if "total" not in raw:
			raise ValueError("steam items response missing required property 'total'")
		if not isinstance(raw["total"], int):
			raise TypeError("invalid type for 'total' property of steam items response")

		if "items" not in raw:
			raise ValueError("steam items response missing required property 'items'")
		if not isinstance(raw["items"], list):
			raise TypeError("invalid type for 'items' property of steam items response")
		items = list[SteamItem]()
		for i, item in enumerate(raw["items"]):
			try:
				items.append(SteamItem.fromJSON(item))
			except (ValueError, TypeError) as e:
				raise TypeError(f"invalid steam item at index {i}: {e}") from e

		return SteamItemsResponse(raw["total"], items)
