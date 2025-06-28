from miru.ext.menu import Menu


class ClearItemsOnTimeoutMenu(Menu):
	async def on_timeout(self) -> None:
		self.clear_items()

		return await super().on_timeout()


class DisableItemsOnTimeoutMenu(Menu):
	def disable_items(self) -> None:
		for item in self.children:
			item.disabled = True

	async def on_timeout(self) -> None:
		self.disable_items()

		return await super().on_timeout()
