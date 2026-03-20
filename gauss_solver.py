#!/usr/bin/env python3
"""
Gaussian elimination solver for systems of linear equations.

Provides exact arithmetic using fractions.Fraction to avoid floating-point
rounding errors. Handles unique, inconsistent, and dependent systems.
"""

import fractions
import math
import random

#============================================


def _copy_matrix(
	m: list[list[fractions.Fraction]]
) -> list[list[fractions.Fraction]]:
	"""
	Deep copy a matrix of Fractions.

	Args:
		m: matrix to copy

	Returns:
		new matrix with copied values
	"""
	return [[fractions.Fraction(x) for x in row] for row in m]


#============================================


def _simplify_row(row: list[fractions.Fraction]) -> None:
	"""
	Divide all elements in a row by their GCD to keep numbers small.

	Modifies the row in place. Only simplifies if all elements are
	integers (denominator == 1). Also ensures the leading nonzero
	element is positive.

	Args:
		row: list of Fraction values to simplify
	"""
	# collect nonzero numerators
	nonzero_nums = [
		abs(x.numerator) for x in row
		if x.numerator != 0 and x.denominator == 1
	]
	if not nonzero_nums:
		return
	# check all elements are integers
	if not all(x.denominator == 1 for x in row):
		return
	# compute GCD of all nonzero values
	g = nonzero_nums[0]
	for val in nonzero_nums[1:]:
		g = math.gcd(g, val)
	if g > 1:
		for i in range(len(row)):
			row[i] = fractions.Fraction(row[i].numerator // g)
	# ensure leading nonzero is positive for cleaner display
	for x in row:
		if x != 0:
			if x < 0:
				for i in range(len(row)):
					row[i] = -row[i]
			break


#============================================


def get_variable_names(n: int) -> list[str]:
	"""
	Return list of variable names for n variables.

	Args:
		n: number of variables

	Returns:
		list of variable name strings
	"""
	if n == 1:
		return ['x']
	elif n == 2:
		return ['x', 'y']
	elif n == 3:
		return ['x', 'y', 'z']
	else:
		return [f'x{i+1}' for i in range(n)]

#============================================


def solve_system(
	matrix: list[list[fractions.Fraction]],
	var_names: list[str]
) -> dict:
	"""
	Solve system of linear equations using Gaussian elimination.

	Performs forward elimination with partial pivoting, then back
	substitution. Detects unique, inconsistent, and dependent systems.

	Args:
		matrix: augmented matrix as list of rows, each row is
		        [a1, a2, ..., an, b] where last column is constants
		var_names: list of variable name strings

	Returns:
		dict with keys:
		- "outcome": "unique", "inconsistent", or "dependent"
		- "steps": list of step dicts with keys "operation",
		          "explanation", "matrix"
		- "solution": dict {var: Fraction} if unique, None otherwise
		- "free_variables": list of free variable names
		- "message": human-readable description
	"""
	# deep copy to avoid modifying input
	m = [[fractions.Fraction(x) for x in row] for row in matrix]

	num_vars = len(var_names)
	num_equations = len(m)

	steps = []

	# forward elimination with partial pivoting
	# uses integer-preserving operations to avoid fractions
	for col in range(min(num_equations, num_vars)):
		# find pivot: row with largest absolute value in column col
		pivot_row = col
		max_val = abs(m[col][col])

		for row in range(col + 1, num_equations):
			if abs(m[row][col]) > max_val:
				max_val = abs(m[row][col])
				pivot_row = row

		# swap rows if needed
		if pivot_row != col:
			m[col], m[pivot_row] = m[pivot_row], m[col]
			op = f'Row {col+1} <-> Row {pivot_row+1}'
			steps.append({
				'operation': op,
				'explanation': (
					f'Swap rows {col+1} and {pivot_row+1} to '
					f'place the largest pivot value on the diagonal'
				),
				'matrix': _copy_matrix(m)
			})

		# check for zero pivot
		if m[col][col] == 0:
			continue

		# eliminate below pivot using integer-preserving method
		# Row_i = pivot * Row_i - m[i][col] * Row_pivot
		pivot_val = m[col][col]

		for row in range(col + 1, num_equations):
			if m[row][col] == 0:
				continue

			row_val = m[row][col]
			# integer-preserving: new Row_i = pivot * Row_i - row_val * Row_col
			for c in range(len(m[row])):
				m[row][c] = pivot_val * m[row][c] - row_val * m[col][c]

			# simplify row by dividing out GCD to keep numbers small
			_simplify_row(m[row])

			op = (
				f'Row {row+1} = {pivot_val} '
				f'* Row {row+1} - {row_val} * Row {col+1}'
			)
			steps.append({
				'operation': op,
				'explanation': (
					f'Eliminate {var_names[col]} from row {row+1} '
					f'using the pivot in row {col+1}'
				),
				'matrix': _copy_matrix(m)
			})

	# check for inconsistency: 0 = nonzero
	for row in range(num_equations):
		# all coefficient columns are zero
		all_zero = all(m[row][c] == 0 for c in range(num_vars))
		if all_zero and m[row][-1] != 0:
			return {
				'outcome': 'inconsistent',
				'steps': steps,
				'solution': None,
				'free_variables': [],
				'message': (
					f'Inconsistent system: row {row+1} gives '
					f'0 = {m[row][-1]} (impossible)'
				)
			}

	# identify pivot columns and free variables
	# map row -> pivot column index (or None if all zeros)
	row_pivot = {}

	for row in range(num_equations):
		# find first nonzero in this row
		pivot_col = None
		for col in range(num_vars):
			if m[row][col] != 0:
				pivot_col = col
				break
		row_pivot[row] = pivot_col

	pivot_cols = [col for col in row_pivot.values() if col is not None]
	free_var_indices = [
		i for i in range(num_vars) if i not in pivot_cols
	]
	free_var_names = [var_names[i] for i in free_var_indices]

	# check for dependent system (free variables exist)
	if free_var_indices:
		return {
			'outcome': 'dependent',
			'steps': steps,
			'solution': None,
			'free_variables': free_var_names,
			'message': (
				f'Dependent system with {len(free_var_names)} '
				f'free variable(s): {", ".join(free_var_names)}'
			)
		}

	# back substitution: eliminate above each pivot (integer-preserving)
	for row in range(min(num_equations, num_vars) - 1, 0, -1):
		pivot_col = row_pivot[row]
		if pivot_col is None:
			continue
		pivot_val = m[row][pivot_col]

		# eliminate entries above the pivot
		for target_row in range(row - 1, -1, -1):
			if m[target_row][pivot_col] == 0:
				continue
			target_val = m[target_row][pivot_col]
			# integer-preserving elimination
			for c in range(len(m[target_row])):
				m[target_row][c] = (
					pivot_val * m[target_row][c]
					- target_val * m[row][c]
				)
			_simplify_row(m[target_row])
			op = (
				f'Row {target_row+1} = {pivot_val} '
				f'* Row {target_row+1} - {target_val} '
				f'* Row {row+1}'
			)
			explanation = (
				f'Eliminate {var_names[pivot_col]} from row '
				f'{target_row+1} using the pivot in row {row+1}'
			)
			steps.append({
				'operation': op,
				'explanation': explanation,
				'matrix': _copy_matrix(m)
			})

	# read off solution: each row has pivot * var = constant
	# so var = constant / pivot
	solution = {}
	for row in range(min(num_equations, num_vars)):
		pivot_col = row_pivot[row]
		if pivot_col is None:
			continue
		pivot_val = m[row][pivot_col]
		solution[var_names[pivot_col]] = m[row][-1] / pivot_val

	# add any variables not found
	for name in var_names:
		if name not in solution:
			solution[name] = fractions.Fraction(0)

	return {
		'outcome': 'unique',
		'steps': steps,
		'solution': solution,
		'free_variables': [],
		'message': 'Unique solution found'
	}

#============================================


def matrix_to_latex(
	matrix: list[list[fractions.Fraction]],
	var_names: list[str]
) -> str:
	"""
	Render augmented matrix as LaTeX.

	Args:
		matrix: augmented matrix
		var_names: variable names for display

	Returns:
		LaTeX string for augmented matrix
	"""
	num_vars = len(var_names)

	# format each cell as frac or int
	def fmt_frac(f: fractions.Fraction) -> str:
		if f.denominator == 1:
			return str(f.numerator)
		return f'\\dfrac{{{f.numerator}}}{{{f.denominator}}}'

	# build rows
	rows = []
	for row in matrix:
		cells = [fmt_frac(row[i]) for i in range(num_vars)]
		# separator for augmented column
		cells.append(fmt_frac(row[-1]))
		rows.append(' & '.join(cells))

	# full LaTeX with extra row spacing for fraction readability
	latex = (
		'\\left[\\begin{array}{' +
		('c' * num_vars) + '|c' +
		'}\n' +
		' \\\\[8pt] \n'.join(rows) +
		'\n\\end{array}\\right]'
	)

	return latex

#============================================


def _format_fraction_inline(f: fractions.Fraction) -> str:
	"""
	Format a Fraction for inline display in operation strings.

	Args:
		f: Fraction value

	Returns:
		human-readable string like "3", "-2", or "1/3"
	"""
	if f.denominator == 1:
		return str(f.numerator)
	return f'{f.numerator}/{f.denominator}'


#============================================


def format_operation(
	target_row: int,
	source_row: int,
	multiplier: fractions.Fraction,
	op_type: str = 'eliminate'
) -> str:
	"""
	Build a human-readable row operation string.

	Args:
		target_row: 1-based row being modified
		source_row: 1-based row being used
		multiplier: scale factor applied to source row
		op_type: "eliminate", "swap", or "scale"

	Returns:
		formatted operation string
	"""
	mult_str = _format_fraction_inline(multiplier)
	if multiplier > 0:
		sign = '+'
		coeff = mult_str
	else:
		sign = '-'
		# remove leading minus for display after the sign
		coeff = _format_fraction_inline(abs(multiplier))

	op = (
		f'Row {target_row} = Row {target_row} '
		f'{sign} {coeff} * Row {source_row}'
	)
	return op


#============================================


def operation_to_latex(op_str: str) -> str:
	"""
	Render row operation in LaTeX notation.

	Converts "Row 2 = Row 2 + 3 * Row 1" into LaTeX with
	proper formatting using subscripts.

	Args:
		op_str: operation string

	Returns:
		LaTeX formatted operation string
	"""
	import re
	# convert "Row N" to "R_N" for LaTeX
	latex = op_str
	latex = re.sub(r'Row (\d+)', r'R_{\1}', latex)
	# convert "1/3" fractions to \dfrac{}{} in LaTeX
	latex = re.sub(
		r'(\d+)/(\d+)',
		r'\\dfrac{\1}{\2}',
		latex
	)
	# wrap arrows for swaps
	latex = latex.replace('<->', r'\leftrightarrow')
	# replace * with \cdot for multiplication
	latex = latex.replace('*', r'\cdot')
	return latex

#============================================


def _nonzero_randint(lo: int, hi: int) -> int:
	"""
	Return a random integer in [lo, hi] that is not zero.

	Args:
		lo: lower bound (inclusive)
		hi: upper bound (inclusive)

	Returns:
		nonzero random integer
	"""
	val = 0
	while val == 0:
		val = random.randint(lo, hi)
	return val


#============================================


def _determinant(matrix: list[list[fractions.Fraction]], n: int) -> fractions.Fraction:
	"""
	Compute determinant of an n x n matrix using Fraction arithmetic.

	Args:
		matrix: square matrix as list of lists
		n: dimension

	Returns:
		determinant as Fraction
	"""
	# copy to avoid mutation
	m = [[fractions.Fraction(x) for x in row[:n]] for row in matrix]
	det = fractions.Fraction(1)
	for col in range(n):
		# find pivot
		pivot_row = None
		for row in range(col, n):
			if m[row][col] != 0:
				pivot_row = row
				break
		if pivot_row is None:
			return fractions.Fraction(0)
		if pivot_row != col:
			m[col], m[pivot_row] = m[pivot_row], m[col]
			det = -det
		det *= m[col][col]
		for row in range(col + 1, n):
			if m[row][col] == 0:
				continue
			factor = m[row][col] / m[col][col]
			for c in range(col, n):
				m[row][c] -= factor * m[col][c]
	return det


#============================================


def generate_random_system(
	n: int,
	system_type: str
) -> tuple[list[list[fractions.Fraction]], list[str]]:
	"""
	Generate random augmented matrix for n variables.

	Args:
		n: number of variables (and equations)
		system_type: "unique", "inconsistent", "dependent", or "mixed"

	Returns:
		tuple of (augmented matrix, variable names)
	"""
	if system_type == 'mixed':
		system_type = random.choice(['unique', 'inconsistent', 'dependent'])

	var_names = get_variable_names(n)

	if system_type == 'unique':
		# build a non-singular system with all nonzero cells
		# choose a nonzero solution, generate coefficient rows,
		# then compute constants from dot product
		solution = [
			fractions.Fraction(_nonzero_randint(-5, 5))
			for _ in range(n)
		]
		# retry until we get a non-singular matrix with all nonzero
		while True:
			matrix = []
			for _ in range(n):
				# all coefficients are nonzero
				row = [
					fractions.Fraction(_nonzero_randint(-6, 6))
					for _ in range(n)
				]
				# constant = dot product of row with solution
				constant = fractions.Fraction(0)
				for j in range(n):
					constant += row[j] * solution[j]
				row.append(constant)
				matrix.append(row)
			# verify non-singular and all cells nonzero
			det = _determinant(matrix, n)
			all_nonzero = all(
				matrix[i][j] != 0
				for i in range(n) for j in range(n + 1)
			)
			if det != 0 and all_nonzero:
				break

		return (matrix, var_names)

	elif system_type == 'inconsistent':
		# build n-1 valid equations, then add a contradictory
		# equation as a linear combo of others with offset
		solution = [
			fractions.Fraction(_nonzero_randint(-5, 5))
			for _ in range(n)
		]
		matrix = []
		for _ in range(n - 1):
			row = [
				fractions.Fraction(_nonzero_randint(-6, 6))
				for _ in range(n)
			]
			constant = fractions.Fraction(0)
			for j in range(n):
				constant += row[j] * solution[j]
			row.append(constant)
			matrix.append(row)

		# last row: linear combo of existing rows + wrong constant
		combo_row = [fractions.Fraction(0)] * (n + 1)
		for existing_row in matrix:
			scale = fractions.Fraction(_nonzero_randint(1, 3))
			for j in range(n + 1):
				combo_row[j] += scale * existing_row[j]
		# offset the constant to make it inconsistent
		combo_row[-1] += fractions.Fraction(_nonzero_randint(1, 5))
		matrix.append(combo_row)

		return (matrix, var_names)

	elif system_type == 'dependent':
		# build n-1 independent equations, then make last row
		# a linear combination of existing rows (consistent)
		solution = [
			fractions.Fraction(_nonzero_randint(-5, 5))
			for _ in range(n)
		]
		matrix = []
		for _ in range(n - 1):
			row = [
				fractions.Fraction(_nonzero_randint(-6, 6))
				for _ in range(n)
			]
			constant = fractions.Fraction(0)
			for j in range(n):
				constant += row[j] * solution[j]
			row.append(constant)
			matrix.append(row)

		# last row: linear combo of existing rows (consistent)
		combo_row = [fractions.Fraction(0)] * (n + 1)
		for existing_row in matrix:
			scale = fractions.Fraction(
				_nonzero_randint(1, 3) * random.choice([-1, 1])
			)
			for j in range(n + 1):
				combo_row[j] += scale * existing_row[j]
		matrix.append(combo_row)

		# last row: copy first row (linearly dependent)
		for j in range(n + 1):
			matrix[n - 1][j] = matrix[0][j]

		return (matrix, var_names)

	else:
		raise ValueError(
			f'Unknown system_type: {system_type}'
		)

#============================================


def main() -> None:
	"""Test basic functionality."""
	# 2x2 unique system
	m = [
		[fractions.Fraction(1), fractions.Fraction(2), fractions.Fraction(5)],
		[fractions.Fraction(3), fractions.Fraction(1), fractions.Fraction(5)]
	]
	result = solve_system(m, ['x', 'y'])
	print('2x2 unique:')
	print('  outcome:', result['outcome'])
	print('  solution:', result['solution'])
	print('  steps:', len(result['steps']))

	# random unique
	m2, names2 = generate_random_system(3, 'unique')
	r2 = solve_system(m2, names2)
	print('\n3x3 random unique:')
	print('  outcome:', r2['outcome'])
	print('  solution:', r2['solution'])

	# random inconsistent
	m3, names3 = generate_random_system(3, 'inconsistent')
	r3 = solve_system(m3, names3)
	print('\n3x3 random inconsistent:')
	print('  outcome:', r3['outcome'])
	print('  message:', r3['message'])

	# random dependent
	m4, names4 = generate_random_system(3, 'dependent')
	r4 = solve_system(m4, names4)
	print('\n3x3 random dependent:')
	print('  outcome:', r4['outcome'])
	print('  free variables:', r4['free_variables'])

	# LaTeX test
	latex = matrix_to_latex(m, ['x', 'y'])
	print('\nLaTeX output:', latex[:80] + '...')


if __name__ == '__main__':
	main()
