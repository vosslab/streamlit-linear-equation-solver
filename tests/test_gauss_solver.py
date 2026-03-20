#!/usr/bin/env python3
"""
Unit tests for gauss_solver module.

Tests cover unique, inconsistent, and dependent systems, as well as
utility functions for variable names, LaTeX output, and random system generation.
"""

import sys
import fractions

import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)

import gauss_solver

#============================================


def test_unique_2x2():
	"""
	Test a known 2x2 system with a unique solution.

	System:
	  x + 2y = 5
	  3x + y = 5

	Solution: x = 1, y = 2
	"""
	matrix = [
		[fractions.Fraction(1), fractions.Fraction(2), fractions.Fraction(5)],
		[fractions.Fraction(3), fractions.Fraction(1), fractions.Fraction(5)]
	]
	result = gauss_solver.solve_system(matrix, ['x', 'y'])

	assert result['outcome'] == 'unique'
	assert result['solution'] is not None
	assert result['solution']['x'] == fractions.Fraction(1)
	assert result['solution']['y'] == fractions.Fraction(2)
	assert result['free_variables'] == []

#============================================


def test_unique_3x3():
	"""
	Test a known 3x3 system with a unique solution.

	System:
	  x + y + z = 6
	  2x - y + z = 3
	  x + y - z = 0

	Solution: x = 1, y = 2, z = 3
	"""
	matrix = [
		[fractions.Fraction(1), fractions.Fraction(1), fractions.Fraction(1), fractions.Fraction(6)],
		[fractions.Fraction(2), fractions.Fraction(-1), fractions.Fraction(1), fractions.Fraction(3)],
		[fractions.Fraction(1), fractions.Fraction(1), fractions.Fraction(-1), fractions.Fraction(0)]
	]
	result = gauss_solver.solve_system(matrix, ['x', 'y', 'z'])

	assert result['outcome'] == 'unique'
	assert result['solution'] is not None
	assert result['solution']['x'] == fractions.Fraction(1)
	assert result['solution']['y'] == fractions.Fraction(2)
	assert result['solution']['z'] == fractions.Fraction(3)
	assert result['free_variables'] == []

#============================================


def test_inconsistent_detection():
	"""
	Test that an inconsistent system is detected correctly.

	System:
	  x + y = 1
	  x + y = 2

	This is inconsistent (no solution exists).
	"""
	matrix = [
		[fractions.Fraction(1), fractions.Fraction(1), fractions.Fraction(1)],
		[fractions.Fraction(1), fractions.Fraction(1), fractions.Fraction(2)]
	]
	result = gauss_solver.solve_system(matrix, ['x', 'y'])

	assert result['outcome'] == 'inconsistent'
	assert result['solution'] is None
	assert result['free_variables'] == []
	assert 'inconsistent' in result['message'].lower() or '0 =' in result['message']

#============================================


def test_dependent_detection():
	"""
	Test that a dependent system is detected correctly.

	System:
	  x + 2y = 5
	  2x + 4y = 10

	This is dependent (infinitely many solutions).
	"""
	matrix = [
		[fractions.Fraction(1), fractions.Fraction(2), fractions.Fraction(5)],
		[fractions.Fraction(2), fractions.Fraction(4), fractions.Fraction(10)]
	]
	result = gauss_solver.solve_system(matrix, ['x', 'y'])

	assert result['outcome'] == 'dependent'
	assert result['solution'] is None
	assert len(result['free_variables']) > 0
	assert 'dependent' in result['message'].lower() or 'free' in result['message'].lower()

#============================================


def test_step_count_positive():
	"""
	Test that a non-trivial system produces steps during elimination.
	"""
	matrix = [
		[fractions.Fraction(1), fractions.Fraction(2), fractions.Fraction(5)],
		[fractions.Fraction(3), fractions.Fraction(1), fractions.Fraction(5)]
	]
	result = gauss_solver.solve_system(matrix, ['x', 'y'])

	# A non-trivial 2x2 system should have at least one elimination step
	assert len(result['steps']) > 0
	assert all('operation' in step for step in result['steps'])
	assert all('explanation' in step for step in result['steps'])
	assert all('matrix' in step for step in result['steps'])

#============================================


def test_fraction_output():
	"""
	Test that solutions are fractions.Fraction, not floats.
	"""
	matrix = [
		[fractions.Fraction(2), fractions.Fraction(1), fractions.Fraction(5)],
		[fractions.Fraction(1), fractions.Fraction(2), fractions.Fraction(5)]
	]
	result = gauss_solver.solve_system(matrix, ['x', 'y'])

	assert result['outcome'] == 'unique'
	assert result['solution'] is not None
	for var, val in result['solution'].items():
		assert isinstance(val, fractions.Fraction), \
			f'Expected Fraction, got {type(val).__name__} for {var}'

#============================================


def test_random_unique():
	"""
	Test that generate_random_system with 'unique' produces a unique outcome.
	"""
	# Run a few times to ensure consistency
	for _ in range(3):
		matrix, var_names = gauss_solver.generate_random_system(3, 'unique')
		result = gauss_solver.solve_system(matrix, var_names)

		assert result['outcome'] == 'unique'
		assert result['solution'] is not None
		assert len(result['solution']) == 3
		assert result['free_variables'] == []

#============================================


def test_random_inconsistent():
	"""
	Test that generate_random_system with 'inconsistent' produces an inconsistent outcome.
	"""
	# Run a few times to ensure consistency
	for _ in range(3):
		matrix, var_names = gauss_solver.generate_random_system(3, 'inconsistent')
		result = gauss_solver.solve_system(matrix, var_names)

		assert result['outcome'] == 'inconsistent'
		assert result['solution'] is None
		assert result['free_variables'] == []

#============================================


def test_random_dependent():
	"""
	Test that generate_random_system with 'dependent' produces a dependent outcome.
	"""
	# Run a few times to ensure consistency
	for _ in range(3):
		matrix, var_names = gauss_solver.generate_random_system(3, 'dependent')
		result = gauss_solver.solve_system(matrix, var_names)

		assert result['outcome'] == 'dependent'
		assert result['solution'] is None
		assert len(result['free_variables']) > 0

#============================================


def test_random_mixed():
	"""
	Test that generate_random_system with 'mixed' produces a valid outcome.
	"""
	# Run a few times to ensure consistency
	for _ in range(5):
		matrix, var_names = gauss_solver.generate_random_system(3, 'mixed')
		result = gauss_solver.solve_system(matrix, var_names)

		# Outcome should be one of the three valid types
		assert result['outcome'] in ['unique', 'inconsistent', 'dependent']
		# Solution should be None unless outcome is unique
		if result['outcome'] != 'unique':
			assert result['solution'] is None
		else:
			assert result['solution'] is not None

#============================================


def test_variable_names_small():
	"""
	Test that get_variable_names returns correct names for small n.
	"""
	assert gauss_solver.get_variable_names(1) == ['x']
	assert gauss_solver.get_variable_names(2) == ['x', 'y']
	assert gauss_solver.get_variable_names(3) == ['x', 'y', 'z']

#============================================


def test_variable_names_large():
	"""
	Test that get_variable_names returns indexed names for large n.
	"""
	names = gauss_solver.get_variable_names(5)
	assert len(names) == 5
	assert names == ['x1', 'x2', 'x3', 'x4', 'x5']

#============================================


def test_latex_output():
	"""
	Test that matrix_to_latex returns a LaTeX string with 'begin{array}'.
	"""
	matrix = [
		[fractions.Fraction(1), fractions.Fraction(2), fractions.Fraction(5)],
		[fractions.Fraction(3), fractions.Fraction(1), fractions.Fraction(5)]
	]
	latex = gauss_solver.matrix_to_latex(matrix, ['x', 'y'])

	assert isinstance(latex, str)
	assert 'begin{array}' in latex
	assert 'end{array}' in latex
	assert '\\left[' in latex
	assert '\\right]' in latex

#============================================
