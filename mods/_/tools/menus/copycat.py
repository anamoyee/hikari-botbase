from collections.abc import Callable
from typing import Self

from hikari import Embed
from miru.ext.menu import Menu, Screen
from miru.ext.menu.screen import ScreenContent
from tcrutils.console import c


class ScreenContent2(ScreenContent):
	def _fix_embeds(self):
		self.embeds = [*self.embeds, *((self.embed,) if self.embed else ())]

	def prepend_embed(self, embed: Embed) -> Self:
		self._fix_embeds()
		self.embeds = [embed, *self.embeds]
		return self

	def append_embed(self, embed: Embed) -> Self:
		self._fix_embeds()
		self.embeds = [*self.embeds, embed]
		return self

	def with_content(self, content_fn: Callable[[str], str]) -> Self:
		self.content = content_fn(self.content)
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
