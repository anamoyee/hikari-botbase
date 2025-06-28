from arc import Context, HookResult
from common import ACL
from hikari import MessageFlag

from ..db import GlobalDB
from ..lang import LANG


@ACL.add_hook
async def banned_hook(ctx: Context) -> HookResult:
	with GlobalDB() as gdb:  # NOTE: might be potential slowdown since it runs on *every /command*..., think it over some time and measure...
		# Edit to the note above: From my testing it takes ~2-10ms (just for the with __enter__), this isnt that bad but well.. i'll think about it later
		if ctx.author.id in gdb.banned_snowflakes:
			await ctx.respond(LANG.get_arc(ctx, "http.403.permbanned"), flags=MessageFlag.EPHEMERAL)

			return HookResult(abort=True)

		return HookResult()
