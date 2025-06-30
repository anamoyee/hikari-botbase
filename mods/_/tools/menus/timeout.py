from miru.ext.menu import Menu, ScreenContent


class _BruteForceFixTimeoutEditMenu(Menu):
	"""Fix the bug, where on_timeout() will edit any ctx.respond() response message and not the first message, which breaks on_timeout()."""

	def _client_start_hook(self, *args, **kwargs) -> None:
		if self.is_bound is None:
			raise RuntimeError("Cannot start an unbound _BruteForceFixTimeoutEditMenu, add bound_to= keyword argument to miru.Client().start_view(...).")

		super()._client_start_hook(*args, **kwargs)

	async def on_timeout(self) -> None:  # replicate the original on_timeout() but with self.update_original_message() instead
		for item in self.children:
			item.disabled = True

		await self.update_original_message()

	async def update_original_message(self, new_content: ScreenContent | None = None) -> None:
		"""Update always the first, bound, as opposed to the ctx.respond()-ed, message, which is not what .update_message() does."""
		if self.message is None:
			raise RuntimeError("Unable to find original message to update on an unbound (unstarted) Menu.")

		if new_content is not None:
			self._payload = new_content._build_payload()

		await self.message.edit(components=self, **self._payload)


class ClearItemsOnTimeoutMenu(_BruteForceFixTimeoutEditMenu):
	async def on_timeout(self) -> None:
		self.clear_items()

		return await super().on_timeout()


class DisableItemsOnTimeoutMenu(_BruteForceFixTimeoutEditMenu):
	def disable_items(self) -> None:
		for item in self.children:
			item.disabled = True

	async def on_timeout(self) -> None:
		self.disable_items()

		return await super().on_timeout()
