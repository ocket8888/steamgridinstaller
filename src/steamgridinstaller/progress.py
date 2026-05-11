# Copyright 2026 ocket8888
# This file is part of steamgridinstaller.
# steamgridinstaller is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# steamgridinstaller is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with steamgridinstaller. If not, see <https://www.gnu.org/licenses/>. 

from sys import stdout as _stdout
from os import get_terminal_size as _getTerminalSize

def printProgressBar(amt: int, total: int, debug: bool):
	"""
	Prints a progress bar to the console.
	"""
	if debug or not _stdout.isatty():
		print("processing", f"{amt}/{total}") 
		return

	lenDiff = len(str(total)) - len(str(amt))
	prefix = f"{' '*lenDiff}{amt}/{total} "
	windowSize = _getTerminalSize().columns - len(prefix)

	width = windowSize - 2 if windowSize < 100 - len(prefix) else 98 - len(prefix)
	progress = int((amt / total) * width)
	print("\x1bM\x1b[2K", prefix, "[", "#"*progress, "-"*(width - progress), "]", sep="")
