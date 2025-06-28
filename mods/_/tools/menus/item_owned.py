from hikari import MessageFlag
from miru import ViewContext
from miru.ext.menu import ScreenButton, ScreenChannelSelect, ScreenRoleSelect, ScreenTextSelect, ScreenUserSelect

from ...lang import LANG
from .owned_menu import OwnedMenu


class _OwnedScreenItemBase(ScreenButton):
	"""Refuses to be interacted with for non-owner of that menu, relies on being attached to a `.m_owned.OwnedMenu`."""

	menu: OwnedMenu

	async def callback(self, ctx: ViewContext) -> bool:
		"""## IMPORTANT: Add a `super().callback()` at the TOP of your callback like this.

		```
		def callback(self, ctx: ViewContext) -> None:
			if async def callback(self, ctx: ViewContext) -> bool:
				return

			... # your button functionality - user is authorised to be the menu owner.
		```

		This will ctx.respond() to the user, you dont have to worry about that as the button functionality implementer.
		"""
		if self.menu.owner.id != ctx.author.id:
			await ctx.respond(LANG.get_arc(ctx, "http.403.button"), flags=MessageFlag.EPHEMERAL)
			return True

		return False  # dont abort


class OwnedScreenButton(_OwnedScreenItemBase, ScreenButton): ...


class OwnedScreenTextSelect(_OwnedScreenItemBase, ScreenTextSelect): ...


class OwnedScreenUserSelect(_OwnedScreenItemBase, ScreenUserSelect): ...


class OwnedScreenChannelSelect(_OwnedScreenItemBase, ScreenChannelSelect): ...


class OwnedScreenRoleSelect(_OwnedScreenItemBase, ScreenRoleSelect): ...
