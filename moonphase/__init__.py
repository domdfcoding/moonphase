#!/usr/bin/env python3
#
#  __init__.py
"""
Python library to calculate the moon phase angle and illuminated fraction for a given time.

Python port of `moonPhase-esp32`_ 1.0.3 by Cellie.

.. _moonPhase-esp32: https://github.com/CelliesProjects/moonPhase-esp32
"""
#
#  Copyright © 2026 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import math

try:
	# stdlib
	import datetime
except ImportError:
	# 3rd party
	import adafruit_datetime as datetime

TYPE_CHECKING = False

if TYPE_CHECKING:
	# stdlib
	from typing import TypeVar
	T = TypeVar('T', bound=float)
	T2 = TypeVar("T2", bound=float)

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2026 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "1.0.3"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["MoonData", "get_phase"]


def _map_time(val: "T2", in_min: "T2", in_max: "T2", out_min: 'T', out_max: 'T') -> float:
	return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


try:
	# stdlib
	from typing import NamedTuple

	class MoonData(NamedTuple):
		#: The moon phase angle as an int (0-360)
		angle: int

		#: The moon percentage that is lit as a real number (0-1)
		percentLit: float

except ImportError:
	# stdlib
	from collections import namedtuple

	MoonData = namedtuple("MoonData", ("angle", "percentLit"))


def get_phase(date: datetime.datetime) -> MoonData:
	"""
	Calculates the phase of the moon at the given epoch.

	:param date:

	:returns: The moon phase angle as an int (0-360) and
		the moon percentage that is lit as a real number (0-1).
	"""

	return _getPhase(date.year, date.month, date.day, _fhour(date))


def _fhour(t: datetime.datetime) -> float:
	"""
	Returns the time component of the given datetime as a float hour.
	"""

	return t.hour + _map_time((t.minute * 60) + t.second, 0, 3600, 0.0, 1.0)


def _getPhase(year: int, month: int, day: int, hour: float) -> MoonData:
	"""
	Calculates the phase of the moon at the given epoch.

	:param date:

	:returns: The moon phase angle as an int (0-360) and
		the moon percentage that is lit as a real number (0-1).
	"""

	j: float = _julian(year, month, float(day) + hour / 24.0) - 2444238.5
	ls: float = _sun_position(j)
	lm: float = _moon_position(j, ls)
	angle: float = lm - ls

	if (angle < 0):  # TODO: use mod?
		angle += 360

	return MoonData(int(angle), (1.0 - math.cos(math.radians(lm - ls))) / 2)


def _julian(year: int, month: int, day: float) -> float:
	b: int = 0

	if (month < 3):
		year -= 1
		month += 12

	if (year > 1582 or (year == 1582 and month > 10) or (year == 1582 and month == 10 and day > 15)):
		a: int = year // 100
		b = 2 - a + a // 4

	c: int = int(365.25 * year)
	e: int = int(30.6001 * (month + 1))

	return b + c + e + day + 1720994.5


def _sun_position(j: float) -> float:
	dl: float = 0.0

	n: float = 360 / 365.2422 * j
	i: int = int(n // 360)
	n = n - i * 360.0
	x: float = n - 3.762863

	if (x < 0):
		x += 360

	x = math.radians(x)
	e: float = x

	while (math.fabs(dl) >= 1e-12):
		dl = e - .016718 * math.sin(e) - x
		e = e - dl / (1 - .016718 * math.cos(e))

	v = 360 // math.pi * math.atan(1.01686011182 * math.tan(e / 2))
	l: float = v + 282.596403
	i = int(l // 360)
	l = l - i * 360.0

	return l


def _moon_position(j: float, ls: float) -> float:
	ms: float = 0.0
	l: float = 0.0
	mm: float = 0.0
	ev: float = 0.0
	sms: float = 0.0
	ae: float = 0.0
	ec: float = 0.0
	i: int = 0

	ms = 0.985647332099 * j - 3.762863

	if (ms < 0):
		ms += 360.0

	l = 13.176396 * j + 64.975464
	i = int(l // 360)
	l = l - i * 360.0

	if (l < 0):
		l += 360

	mm = l - 0.1114041 * j - 349.383063
	i = int(mm // 360)
	mm -= i * 360.0
	ev = 1.2739 * math.sin(math.radians(2 * (l - ls) - mm))
	sms = math.sin(math.radians(ms))
	ae = 0.1858 * sms
	mm += ev - ae - 0.37 * sms
	ec = 6.2886 * math.sin(math.radians(mm))
	l += ev + ec - ae + 0.214 * math.sin(math.radians(2 * mm))
	l = 0.6583 * math.sin(math.radians(2 * (l - ls))) + l
	return l
