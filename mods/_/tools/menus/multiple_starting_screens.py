import miru
from miru.ext.menu import Menu, Screen


class MultipleStartingScreenStackMenu(Menu):
	async def build_response_async(self, MCL: miru.Client, *screen_stack: Screen):
		"""Build a partially explored response from a stack of screens.

		A small wrapper around Menu().build_response_async() that reaches into private API since theres no way to do it with public API afaik.
		"""
		*inner_screens, topmost_screen = screen_stack

		self._stack.extend(inner_screens)

		return await super().build_response_async(MCL, topmost_screen)
