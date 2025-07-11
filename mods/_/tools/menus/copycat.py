from collections.abc import Callable
from typing import Self

import hikari
from hikari import Embed
from miru.ext.menu import Menu, Screen
from miru.ext.menu.screen import ScreenContent
from tcrutils.console import c


class ScreenContent2(ScreenContent):
	def _fix_embeds(self):
		if not self.embed:
			return

		self.embeds = [*self.embeds, self.embed]
		self.embed = hikari.UNDEFzINED

	def prepend_embed(self, embed: Embed) -> Self:
		"""Add an embed to the start of the embeds."""
		self._fix_embeds()
		self.embeds = [embed, *self.embeds]
		return self

	def append_embed(self, embed: Embed) -> Self:
		"""Add an embed to the end of the embeds."""
		self._fix_embeds()
		self.embeds = [*self.embeds, embed]
		return self

	def with_content(self, content_fn: Callable[[str], str]) -> Self:
		"""Set the content of the last embed, if no embeds found, raise RuntimeError."""
		self.content = content_fn(self.content)
		return self

	def with_footer(self, footer_fn: Callable[[str | None], str]) -> Self:
		"""Set the footer of the last embed, if no embeds found, raise RuntimeError."""
		self._fix_embeds()

		if not self.embeds:
			raise ValueError("Cannot add footer to ScreenContent2 without an embed.")

		self.embeds[-1].set_footer(footer_fn(self.embeds[-1].footer.text if self.embeds[-1].footer is not None else None))
		return self


class CopycatScreen(Screen):
	"""Act like the screen under this screen, this can be used to overlay additional embeds like "Success" embed and all the contens like informational content stays (or you can slightly or entirely modify it).

	Override the `build_content` method to add additional functionality, by default this will behave exactly like the underlying screen
	"""

	def __init__(self, menu: Menu, *, copycat_items: bool = True) -> None:
		super().__init__(menu)

		if copycat_items:
			for item in menu.current_screen.children:  # Not using blueprint_screen because in init it's the menu.current_screen that will become blueprint_screen
				self.add_item(item)

	async def build_content(self) -> ScreenContent2:
		blueprint_sc = await self.blueprint_screen.build_content()

		return ScreenContent2(**blueprint_sc._build_payload())

	@property
	def blueprint_screen(self):
		"""Retrieve this CopycatScreen's copycated screen."""
		#   He couldn't see beyond
		# the red shade he was aware.
		#  He never caught a glimpse,
		# Of the screen I had to share
		return self.menu._stack[-2]  # assuming there's a -2 screen since otherwise it'd error on __init__
