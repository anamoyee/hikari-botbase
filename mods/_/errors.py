import traceback
from dataclasses import dataclass as _dataclass

from common.bot import ACL, BOT, MCL
from common.errors import ThisError
from prelude import *
from tcrutils import discord_ifys as IFYs
from tcrutils.codeblock import codeblocks
from tcrutils.extract_error import extract_error, extract_traceback

from .config import S


class ModError(ThisError):
	"""Common base class for all errors coming from mods."""


class UserGetsDetailsError(ModError):
	"""Any error happend but also user gets to see an error message if this isnt caught. This is supposed to be subclassed since user also gets to see this errors `.__class__.__name__`. If this class is not subclassed, the class name will not be shown (annonymous error type).

	You can disable this functionality `'_'`-mod-wide in the config.
	"""

	user_details: str
	"""The details given to the user."""

	display_class_name: bool = True
	"""When a class inherits from UserGetsDetailsError and is raised: whether to display its name or just 'Error!'. (The details are still displayed)"""

	silent: bool = False
	"""Whether to NOT print the error traceback in the console, only respond to user (functional exception, like when it's entirely user's fault)."""

	def __init__(self, /, user_details: str, *, display_class_name: bool = True, silent: bool = False) -> None:
		self.user_details = user_details
		self.display_class_name = display_class_name
		self.silent = silent
		super().__init__(user_details)

	def display_to_user(self) -> str:
		"""Return the error message to display to the user."""

		if self.__class__ is UserGetsDetailsError:  # No fish? No pass
			base_message = self.user_details
		else:
			base_message = f"**{self.__class__.__name__ if self.display_class_name else 'Error'}!** {self.user_details}"

		return f"{base_message}\nIf you want, you can report this to the bot developer to get this solved (maybe), {S.AUTHOR.get_developer_contact_info()}"  # TODO: find a better way of getting developer info from callstack maybe? Since it does not take into account errors from mods.


@ACL.set_error_handler
async def handle_uncaught_errors(ctx: arc.GatewayContext, e: BaseException) -> None:
	if S.ENABLE_USER_GETS_DETAILS_ERRORS and isinstance(e, UserGetsDetailsError):
		await ctx.respond(e.display_to_user())
	else:
		await ctx.respond("**Error!**")  # If the error is not of type UserGetsDetailsError, dont give details.

	if e.silent:
		return

	if S.ERROR_CHANNEL:
		msg = f"## Unhandled command error in `{ctx.command.display_name}` triggered by {IFYs.userify(ctx.author.id)}\n" + codeblocks(
			extract_error(e),
			extract_traceback(e),
			langcodes=("py", "py"),
			max_length=1800,
		)

		await BOT.rest.create_message(S.ERROR_CHANNEL, msg)

	raw_msg = f"Unhandled command error in {ctx.command.display_name!r} triggered by {ctx.author.id}"
	c.error(raw_msg)

	traceback.print_exception(type(e), e, e.__traceback__)


async def handle_uncaught_interactions(inter: hikari.ComponentInteraction) -> None:
	await inter.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, f"{S.NO} This message is too old to be interacted with or there's a bug in the code, try spawning a new one!")


if not TESTMODE:  # Will throw a big red application did not respond during testing - intended of course
	MCL.set_unhandled_component_interaction_hook(handle_uncaught_interactions)
	MCL.set_unhandled_modal_interaction_hook(handle_uncaught_interactions)
