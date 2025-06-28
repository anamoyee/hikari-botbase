import random as rng
from collections.abc import Iterable
from enum import StrEnum

from prelude import *

from ..models import HashEq_by

logger = get_logger(__name__)

if True:  # ProfileID

	class ProfileID(StrEnum):
		"""An ID to differenciate multiple profiles on a single account while also being able to target/select them.

		Variants prefixed with `_` are considered 'restricted', that means they will not be chosen as a candidate for `ProfileID.get_random()`.
		"""

		_ROBO = 'robo'  # fmt: skip # The robo profile is 100% 'not needed' in this rewrite since the whole point of there being profiles from the start makes it pointless, however i couldn't have just left it out!!
		_KITSUNE = "kitsune"

		if True:  # Common Animals
			OX = "ox"
			DOG = "dog"
			FLY = "fly"
			PIG = "pig"
			CAT = "cat"
			BAT = "bat"
			COW = "cow"
			FOX = "fox"
			DUCK = "duck"
			CRAB = "crab"
			FISH = "fish"
			FROG = "frog"
			BEAR = "bear"
			DOVE = "dove"
			WORM = "worm"
			SEAL = "seal"
			MOUSE = "mouse"
			SLOTH = "sloth"
			HIPPO = "hippo"
			SHEEP = "sheep"
			SKUNK = "skunk"
			SQUID = "squid"
			SNAIL = "snail"
			KOALA = "koala"
			CHICK = "chick"
			WHALE = "whale"
			ZEBRA = "zebra"
			HORSE = "horse"
			CAMEL = "camel"
			RABBIT = "rabbit"
			LIZARD = "lizard"
			BEAVER = "beaver"
			PARROT = "parrot"
			SPIDER = "spider"
			SHRIMP = "shrimp"
			BEETLE = "beetle"
			TURKEY = "turkey"
			GORILLA = "gorilla"
			LEOPARD = "leopard"
			PENGUIN = "penguin"
			CHICKEN = "chicken"
			GIRAFFE = "giraffe"
			SNOWMAN = "snowman"
			HAMSTER = "hamster"
			CRICKET = "cricket"
			ELEPHANT = "elephant"
			DINOSAUR = "dinosaur"
			HEDGEHOG = "hedgehog"
			CROCODILE = "crocodile"
			CATERPILLAR = "caterpillar"

		@classmethod
		def get_random(cls, excluded: Iterable["ProfileID"] = ()) -> "ProfileID":
			"""Get a random ProfileID enum variant, excluding those in `excluded`.

			Raise a ValueError when excluded contains all available ProfileIDs.
			"""
			restricted_union_excluded = {member for member in cls if member.name.startswith("_")}.union(excluded)

			if not set(cls).difference(restricted_union_excluded):
				raise ValueError("Unable to get a new ProfileID due to none being available (all non-restricted ProfileIDs were provided as `excluded`).")

			while (chosen := cls(rng.choice(list(cls)))) in restricted_union_excluded:
				pass

			return chosen

		@property
		def emoji(self):
			return self.__class__._profile_id_to_emoji_lookup[self]

	ProfileID._profile_id_to_emoji_lookup = {
		ProfileID._ROBO: "🤖",
		ProfileID._KITSUNE: "🦊",
		ProfileID.OX: "🐂",
		ProfileID.DOG: "🐶",
		ProfileID.FLY: "🪰",
		ProfileID.PIG: "🐷",
		ProfileID.CAT: "🐱",
		ProfileID.BAT: "🦇",
		ProfileID.COW: "🐄",
		ProfileID.FOX: "🦊",
		ProfileID.DUCK: "🦆",
		ProfileID.CRAB: "🦀",
		ProfileID.FISH: "🐟",
		ProfileID.FROG: "🐸",
		ProfileID.BEAR: "🐻",
		ProfileID.DOVE: "🕊️",
		ProfileID.WORM: "🪱",
		ProfileID.SEAL: "🦭",
		ProfileID.MOUSE: "🐭",
		ProfileID.SLOTH: "🦥",
		ProfileID.HIPPO: "🦛",
		ProfileID.SHEEP: "🐑",
		ProfileID.SKUNK: "🦨",
		ProfileID.SQUID: "🦑",
		ProfileID.SNAIL: "🐌",
		ProfileID.KOALA: "🐨",
		ProfileID.CHICK: "🐥",
		ProfileID.WHALE: "🐋",
		ProfileID.ZEBRA: "🦓",
		ProfileID.HORSE: "🐴",
		ProfileID.CAMEL: "🐫",
		ProfileID.RABBIT: "🐰",
		ProfileID.LIZARD: "🦎",
		ProfileID.BEAVER: "🦫",
		ProfileID.PARROT: "🦜",
		ProfileID.SPIDER: "🕷️",
		ProfileID.SHRIMP: "🦐",
		ProfileID.BEETLE: "🪲",
		ProfileID.TURKEY: "🦃",
		ProfileID.GORILLA: "🦍",
		ProfileID.LEOPARD: "🐆",
		ProfileID.PENGUIN: "🐧",
		ProfileID.CHICKEN: "🐔",
		ProfileID.GIRAFFE: "🦒",
		ProfileID.SNOWMAN: "⛄",
		ProfileID.HAMSTER: "🐹",
		ProfileID.CRICKET: "🦗",
		ProfileID.ELEPHANT: "🐘",
		ProfileID.DINOSAUR: "🦕",
		ProfileID.HEDGEHOG: "🦔",
		ProfileID.CROCODILE: "🐊",
		ProfileID.CATERPILLAR: "🐛",
	}

	if _unmapped_profile_ids := set(ProfileID) - set(ProfileID._profile_id_to_emoji_lookup.keys()):
		logger.error(f"Missing emoji lookup(s) for ProfileID. This WILL cause random crashes. This affects the following ProfileID(s):\n" + "\n".join([f"  - {x!r}" for x in _unmapped_profile_ids]))


@HashEq_by("id")
class Profile(BM):
	id: ProfileID
	"""The ProfileID of this profile, that is: `fox`, `cat`, `kitsune`, etc. encapsulated in a StrEnum."""

	display_name: str = "Unnamed profile"
	"""The display name of this profile"""

	@property
	def emoji(self) -> str:
		return self.id.emoji

	def sort_key(self):
		return self.id.value

	def make_ident_name(self) -> str:
		"""Name used for identification (since two profiles can have the same name, this guarantees uniqueness by appending profile id)."""
		return f"[{self.id}] {self.display_name}"

	def make_md_ident_name(self) -> str:
		"""Display name used in a markdown-supporting display box."""
		return f"{self.emoji} [`{self.id}`] {self.display_name}"
