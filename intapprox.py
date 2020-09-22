#!/usr/bin/env python3
#	intapprox - Embedded real value multiplication using integer arithmetic
#	Copyright (C) 2020-2020 Johannes Bauer
#
#	This file is part of intapprox.
#
#	intapprox is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	intapprox is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with intapprox; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import sys
import math
from FriendlyArgumentParser import FriendlyArgumentParser, baseint

parser = FriendlyArgumentParser(description = "Approximate multiplication by a float value using integer arithmetic and system constraints.")
parser.add_argument("-b", "--bits", metavar = "bits", type = int, default = 32, help = "Ensure that the topmost value never exceeds the register width.")
parser.add_argument("-m", "--max-input-value", metavar = "int", type = baseint, required = True, help = "Maximum input value that is expected.")
parser.add_argument("-e", "--max-error", metavar = "epsilon", type = float, default = 1e-6, help = "Error at which to abort. Defaults to %(default).1e.")
parser.add_argument("--fast-multiplication", action = "store_true", help = "Only accept multiplication values that can be executed quickly (i.e., by shifting left)")
parser.add_argument("--fast-division", action = "store_true", help = "Only accept divisor values that can be executed quickly (i.e., by shifting right)")
parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increases verbosity. Can be specified multiple times to increase.")
parser.add_argument("expression", help = "Target expression to evaluate, which is the value that the input is multiplied with. Must not include any symbols.")
args = parser.parse_args(sys.argv[1:])

target_value = eval(args.expression)
max_multiplier = math.floor(((1 << args.bits) - 1) / args.max_input_value)
print("Approximating target value: %f" % (target_value))
if args.verbose >= 1:
	print("Maximum input value       : %d" % (args.max_input_value))
	print("Register width            : %d bits" % (args.bits))
	print("Maximum multiplier        : %d" % (max_multiplier))

def is_power_of_two(value):
	return (x != 0) and ((value & (value - 1)) == 0)

def round_to_power_of_two(value):
	if value <= 0:
		return 1
	lower = 1 << (value.bit_length() - 1)
	upper = 1 << value.bit_length()
	if abs(value - lower) <= abs(value - upper):
		return lower
	else:
		return upper

if not args.fast_multiplication:
	multiplier_range = range(1, max_multiplier + 1)
else:
	multiplier_range = [ 1 << bit for bit in range(max_multiplier.bit_length()) ]

min_error = None
best_approximation = None
for multiplier in multiplier_range:
	divisor = round(multiplier / target_value)
	if args.fast_division:
		divisor = round_to_power_of_two(divisor)
	if divisor == 0:
		continue
	approximation = multiplier / divisor
	error = (approximation - target_value) / target_value
	if args.verbose >= 2:
		print("Approximation: x * %d / %d = %f (error %.2e)" % (multiplier, divisor, approximation, error))
	abserror = abs(error)
	if (min_error is None) or (abserror < abs(min_error)):
		min_error = error
		best_approximation = (multiplier, divisor)
		if args.verbose >= 2:
			print("Found: x * %d / %d with error %.3e" % (best_approximation[0], best_approximation[1], min_error))
	if abs(min_error) < args.max_error:
		break

print("Best approximation        : x * %d / %d" % (best_approximation[0], best_approximation[1]))
print("Resulting error           : %.4f%%" % (min_error * 100))
