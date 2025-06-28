import re as _regex
from typing import Self

from prelude import *
from tcrutils import discord_ifys as IFYs

if True:  # Author

	class Author(BM):
		discord_id: int
		discord_username: str

		def make_discord_mention(self) -> str:
			return IFYs.userify(self.discord_id)

		def get_developer_contact_info(self) -> str:
			return f"{self.make_discord_mention()} (ID: {self.discord_id})"


if True:  # CustomEmoji & stuff

	class CustomEmoji(BM):
		name: str
		id: str
		animated: bool

		def __str__(self) -> str:
			return IFYs.emojify(self.name, self.id, animated=self.animated)

		@classmethod
		def into(cls, emoji_str: str) -> Self:
			"""Create a CustomEmoji from the given string, like `'<:fluff:123412341234>'`."""
			pattern = r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>\d+)>"
			# <a?:[a-zA-Z0-9_]{2,32}:[0-9]>

			match = _regex.match(pattern, emoji_str)

			if match:
				name = match.group("name")
				id_ = match.group("id")
				animated = match.group("animated")
				return cls(
					name=name,
					id=id_,
					animated=bool(animated),
				)
			else:
				raise ValueError(f"Invalid Discord markdown custom emoji format: {emoji_str!r}")

	class CustomEmojiStaticBase(BM):
		"""Contains a converter ("validator") for all fields to convert them into CustomEmoji types."""

		@pd.field_validator("*", mode="before")
		@classmethod
		def convert_emoji_str(cls, value: str | CustomEmoji) -> CustomEmoji:
			if isinstance(value, str):
				return CustomEmoji.into(value)

			return value


if True:  # Color Palette

	class ColorPaletteStatic(BM):
		# fmt: off
		COLON:   int = 0xFF8000
		PRIMARY: int = 0x8000FF  # ROL #$FF8000, #8

		SUCCESS: int = 0x00FF00
		FAILURE: int = 0xFF0000
		INFO:    int = 0x0000FF
		# fmt: on


if True:  # File Palette

	class HikariFileStatic(BM):
		megu_button: hikari.File = hikari.File(ROOT_PATH / "mods/_/assets/megu_button.png")
