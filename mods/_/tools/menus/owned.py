from functools import wraps

import miru
from hikari import MessageFlag, User
from miru import ViewContext
from miru.ext.menu import Menu, ScreenButton, ScreenChannelSelect, ScreenRoleSelect, ScreenTextSelect, ScreenUserSelect

from ...config import S
from ...lang import LANG


class OwnedMenu(Menu):
	owner: User

	def __init__[**P](self, *args: P.args, owner: User, **kwargs: P.kwargs) -> None:
		self.owner = owner
		super().__init__(*args, **kwargs)


class _OwnedScreenItemBase:
	"""Refuses to be interacted with for non-owner of that menu, relies on being attached to a `OwnedMenu`."""

	menu: OwnedMenu

	async def callback(self, ctx: ViewContext) -> bool:
		"""## IMPORTANT: Add a `super().callback()` at the TOP of your callback like this.

		```
		class SomeScreenButton(OwnedScreenButton):
			def callback(self, ...) -> None:
				if async def callback(self, ctx: ViewContext) -> bool:
					return

				... # your button functionality - user is authorised to be the menu owner.
		```
		## Alternatively you can use the decorator on the callback method:
		```
		@enforce_owned_callback
		class SomeScreenButton(OwnedScreenButton):
			def callback(self, ...) -> None:
				... # your code straightaway - user is authorised to be the menu owner by the decorator.
		```

		### This will ctx.respond() to the user, you dont have to worry about that as the `ScreenItem()` functionality implementer.
		"""
		if self.menu.owner.id != ctx.author.id:
			if S.PERMISSION_DENIED_ERROR_IS_MEGU_BUTTON_PNG:
				await ctx.respond(attachment=S.FILE.megu_button, flags=MessageFlag.EPHEMERAL)
			else:
				await ctx.respond(LANG.get_arc(ctx, f"http.403.{'select' if isinstance(self, miru.abc.SelectBase) else 'button'}"), flags=MessageFlag.EPHEMERAL)

			return True

		return False  # dont abort


class OwnedScreenButton(_OwnedScreenItemBase, ScreenButton): ...


class OwnedScreenTextSelect(_OwnedScreenItemBase, ScreenTextSelect): ...


class OwnedScreenUserSelect(_OwnedScreenItemBase, ScreenUserSelect): ...


class OwnedScreenChannelSelect(_OwnedScreenItemBase, ScreenChannelSelect): ...


class OwnedScreenRoleSelect(_OwnedScreenItemBase, ScreenRoleSelect): ...


def enforce_owned_callback[T: _OwnedScreenItemBase](cls: T) -> T:
	"""Decorate a callback on an `Owned{ScrenItem}` to skip the boilerplate. Usage below.

	```
	@enforce_owned_callback
	class SomeScreenButton(OwnedScreenButton):
		def callback(self, ctx: ViewContext) -> None:
			... # your code straightaway - user is authorised to be the menu owner by the decorator.
	```
	"""

	if not issubclass(cls, _OwnedScreenItemBase):
		raise TypeError("enforce_owned_callback: this decorator only works on `Owned{ScreenItem}` classes, are you sure you inherited from the correct class?")

	original_callback = getattr(cls, "callback", None)

	if original_callback is None:
		raise RuntimeError(f"@enforce_owned_callback: {cls!r} does not seem to defined a callback method...?")

	@wraps(original_callback)
	async def wrapped_callback(self, ctx):
		if await super(cls, self).callback(ctx):
			return None

		return await original_callback(self, ctx)

	cls.callback = wrapped_callback
	return cls
