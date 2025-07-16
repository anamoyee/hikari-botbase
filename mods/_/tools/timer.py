import time
from asyncio import iscoroutinefunction
from collections.abc import Callable
from functools import wraps
from typing import Self


class TimerMeta(type):
	def __enter__(cls):
		cls.a = time.perf_counter()

	def __exit__(cls, exc_type, exc_value, traceback):
		cls.b = time.perf_counter()

		print(f"took {cls.b - cls.a:.4f}s")


class Timer(metaclass=TimerMeta):
	def __new__(cls, name: str | Callable) -> Self:
		self = super().__new__(cls)

		if not callable(name):
			return self

		if iscoroutinefunction(name):

			@wraps(name)
			async def wrapper(*args, **kwargs):
				with Timer(name.__name__):
					return await name(*args, **kwargs)

		else:

			@wraps(name)
			def wrapper(*args, **kwargs):
				with Timer(name.__name__):
					return name(*args, **kwargs)

		return wrapper

	def __init__(self, name: str = "unnamed") -> None:
		self.name = name

	def __enter__(self):
		self.a = time.perf_counter()

	def __exit__(self, exc_type, exc_value, traceback):
		self.b = time.perf_counter()

		print(f"{self.name!r} took {self.b - self.a:.4f}s")
