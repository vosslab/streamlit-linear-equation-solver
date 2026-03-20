#!/usr/bin/env python3
"""
Streamlit UI for the linear equation solver.

Provides an interactive interface to solve systems of linear equations
using Gaussian elimination with exact rational arithmetic.
"""

import streamlit
import fractions
import gauss_solver

#============================================


def initialize_session_state(num_vars: int) -> None:
	"""
	Initialize session state for a given number of variables.

	Creates matrix, variable names, and solution tracking in session state.

	Args:
		num_vars: number of variables (2-6)
	"""
	# Check if we need to initialize or reset
	needs_init = 'num_vars' not in streamlit.session_state
	needs_reset = (
		not needs_init
		and streamlit.session_state.num_vars != num_vars
	)

	if needs_init or needs_reset:
		# Clear old widget keys when resizing
		if needs_reset:
			old_n = streamlit.session_state.num_vars
			for eq_idx in range(old_n):
				for var_idx in range(old_n + 1):
					widget_key = f'input_{eq_idx}_{var_idx}'
					if widget_key in streamlit.session_state:
						del streamlit.session_state[widget_key]

		streamlit.session_state.num_vars = num_vars
		streamlit.session_state.var_names = (
			gauss_solver.get_variable_names(num_vars)
		)
		# Initialize augmented matrix (num_vars x (num_vars+1))
		streamlit.session_state.matrix = [
			[fractions.Fraction(0) for _ in range(num_vars + 1)]
			for _ in range(num_vars)
		]
		streamlit.session_state.solve_result = None
		streamlit.session_state.current_step = 0
		streamlit.session_state.all_steps_shown = False


#============================================


def format_fraction(f: fractions.Fraction) -> str:
	"""
	Format a Fraction for display.

	Args:
		f: Fraction value

	Returns:
		string representation (integer or fraction)
	"""
	if f.denominator == 1:
		return str(f.numerator)
	return f'{f.numerator}/{f.denominator}'


#============================================


def parse_input_value(text: str) -> fractions.Fraction:
	"""
	Parse a text input string into a Fraction.

	Accepts integers, decimals, and fraction notation like 3/4.

	Args:
		text: user input string

	Returns:
		parsed Fraction value, or Fraction(0) if invalid
	"""
	cleaned = text.strip()
	if not cleaned:
		return fractions.Fraction(0)
	# Handle fraction notation like "3/4" or "-1/3"
	if '/' in cleaned:
		parts = cleaned.split('/')
		if len(parts) == 2:
			numer = int(parts[0])
			denom = int(parts[1])
			if denom != 0:
				return fractions.Fraction(numer, denom)
		return fractions.Fraction(0)
	# Handle integers and decimals
	value = float(cleaned)
	return fractions.Fraction(value).limit_denominator(1000)


#============================================


def render_matrix_input(num_vars: int, var_names: list[str]) -> None:
	"""
	Render input grid for augmented matrix coefficients.

	Uses text inputs for a cleaner, more compact layout.

	Args:
		num_vars: number of variables
		var_names: list of variable names
	"""
	streamlit.subheader('Coefficient Matrix')

	# Build column layout: vars + separator + constant
	# Column widths: variable columns + narrow separator + constant
	col_widths = [1] * num_vars + [0.15, 1]
	header_cols = streamlit.columns(col_widths)

	# Column headers
	for i in range(num_vars):
		with header_cols[i]:
			streamlit.markdown(f'**{var_names[i]}**')
	# Separator column (the augmented bar)
	with header_cols[num_vars]:
		streamlit.markdown('**|**')
	with header_cols[num_vars + 1]:
		streamlit.markdown('**=**')

	# Input rows for each equation
	for eq_idx in range(num_vars):
		row_cols = streamlit.columns(col_widths)

		for var_idx in range(num_vars):
			with row_cols[var_idx]:
				widget_key = f'input_{eq_idx}_{var_idx}'
				# Initialize widget key if not set
				if widget_key not in streamlit.session_state:
					streamlit.session_state[widget_key] = '0'
				text_val = streamlit.text_input(
					label=f'Eq{eq_idx + 1} {var_names[var_idx]}',
					key=widget_key,
					label_visibility='collapsed'
				)
				# Parse and store
				streamlit.session_state.matrix[eq_idx][var_idx] = (
					parse_input_value(text_val)
				)

		# Separator column
		with row_cols[num_vars]:
			streamlit.markdown(
				'<div style="text-align:center; '
				'padding-top:8px; font-size:1.2em;">|</div>',
				unsafe_allow_html=True
			)

		# Constant column
		with row_cols[num_vars + 1]:
			widget_key = f'input_{eq_idx}_{num_vars}'
			if widget_key not in streamlit.session_state:
				streamlit.session_state[widget_key] = '0'
			text_val = streamlit.text_input(
				label=f'Eq{eq_idx + 1} constant',
				key=widget_key,
				label_visibility='collapsed'
			)
			streamlit.session_state.matrix[eq_idx][num_vars] = (
				parse_input_value(text_val)
			)

	streamlit.caption(
		'Enter integers, decimals, or fractions (e.g. 3/4)'
	)


#============================================


def randomize_system(num_vars: int, system_type: str) -> None:
	"""
	Generate random system and populate matrix in session state.

	Also updates the individual input widget keys so the displayed
	values reflect the new random coefficients on rerun.

	Args:
		num_vars: number of variables
		system_type: "unique", "inconsistent", "dependent", or "mixed"
	"""
	matrix, var_names = gauss_solver.generate_random_system(
		num_vars, system_type
	)
	streamlit.session_state.matrix = matrix
	streamlit.session_state.var_names = var_names
	streamlit.session_state.solve_result = None
	streamlit.session_state.current_step = 0
	streamlit.session_state.all_steps_shown = False
	# Push values into widget keys as strings for text_input
	for eq_idx in range(num_vars):
		for var_idx in range(num_vars + 1):
			widget_key = f'input_{eq_idx}_{var_idx}'
			streamlit.session_state[widget_key] = str(
				int(matrix[eq_idx][var_idx])
			)


#============================================


def render_solution_unique(solution: dict) -> None:
	"""
	Display unique solution with success message.

	Args:
		solution: dict mapping variable names to Fraction values
	"""
	streamlit.success('Unique Solution Found')
	cols = streamlit.columns(len(solution))

	for i, (var_name, value) in enumerate(sorted(solution.items())):
		with cols[i]:
			streamlit.metric(
				label=var_name,
				value=format_fraction(value)
			)


#============================================


def render_solution_inconsistent(message: str) -> None:
	"""
	Display inconsistent system message.

	Args:
		message: explanation of inconsistency
	"""
	streamlit.error('No Solution (Inconsistent System)')
	streamlit.write(message)


#============================================


def render_solution_dependent(
	free_variables: list[str],
	message: str
) -> None:
	"""
	Display dependent system with free variables.

	Args:
		free_variables: list of free variable names
		message: explanation of the system
	"""
	streamlit.warning('Infinitely Many Solutions (Dependent System)')
	streamlit.write(message)
	streamlit.write(f'Free variables: {", ".join(free_variables)}')


#============================================


def render_outcome(result: dict) -> None:
	"""
	Display outcome banner based on system type.

	Args:
		result: solution dict from gauss_solver.solve_system
	"""
	outcome = result['outcome']

	if outcome == 'unique':
		render_solution_unique(result['solution'])
	elif outcome == 'inconsistent':
		render_solution_inconsistent(result['message'])
	elif outcome == 'dependent':
		render_solution_dependent(
			result['free_variables'],
			result['message']
		)


#============================================


def render_step_controls(
	key_suffix: str,
	can_advance: bool,
	is_showing_all: bool,
	total_steps: int
) -> str:
	"""
	Render Next Step / Show All / Reset buttons.

	Args:
		key_suffix: unique suffix for button keys (top/bottom)
		can_advance: whether Next Step should be enabled
		is_showing_all: whether all steps are shown
		total_steps: total number of steps

	Returns:
		action string if a button was pressed, empty string otherwise
	"""
	action = ''
	col1, col2, col3 = streamlit.columns(3)

	with col1:
		if streamlit.button(
			'Next Step',
			key=f'next_step_{key_suffix}',
			disabled=not can_advance,
			use_container_width=True
		):
			action = 'next'

	with col2:
		if streamlit.button(
			'Show All Steps',
			key=f'show_all_{key_suffix}',
			disabled=is_showing_all,
			use_container_width=True
		):
			action = 'show_all'

	with col3:
		if streamlit.button(
			'Reset',
			key=f'reset_{key_suffix}',
			use_container_width=True
		):
			action = 'reset'

	return action


#============================================


def handle_step_action(action: str, total_steps: int) -> None:
	"""
	Update session state based on step control action.

	Args:
		action: "next", "show_all", or "reset"
		total_steps: total number of steps
	"""
	if action == 'next':
		streamlit.session_state.current_step += 1
		streamlit.rerun()
	elif action == 'show_all':
		streamlit.session_state.all_steps_shown = True
		streamlit.session_state.current_step = total_steps
		streamlit.rerun()
	elif action == 'reset':
		streamlit.session_state.current_step = 0
		streamlit.session_state.all_steps_shown = False
		streamlit.rerun()


#============================================


def render_steps(result: dict, detail_level: str) -> None:
	"""
	Render progressive steps with matrices and operations.

	Args:
		result: solution dict from gauss_solver.solve_system
		detail_level: "Matrix Steps" or "Steps with Explanations"
	"""
	steps = result['steps']
	total_steps = len(steps)

	if total_steps == 0:
		render_outcome(result)
		return

	# Compute display state
	current = streamlit.session_state.current_step
	is_showing_all = streamlit.session_state.all_steps_shown
	visible = total_steps if is_showing_all else current
	can_advance = not is_showing_all and current < total_steps

	streamlit.write(f'**Showing {visible} of {total_steps} steps**')

	# Top controls
	top_action = render_step_controls(
		'top', can_advance, is_showing_all, total_steps
	)

	# Show the initial matrix before any operations
	with streamlit.container(border=True):
		streamlit.write('**Initial System**')
		initial_matrix = streamlit.session_state.matrix
		initial_latex = gauss_solver.matrix_to_latex(
			initial_matrix, streamlit.session_state.var_names
		)
		streamlit.latex(initial_latex)

	# Display steps up to current visible count
	for step_idx in range(visible):
		step = steps[step_idx]

		# Compact layout: header + operation on one line
		op_latex = gauss_solver.operation_to_latex(
			step['operation']
		)
		header = f'**Step {step_idx + 1}.** $\\;{op_latex}$'
		if detail_level == 'Steps with Explanations':
			header += f' &mdash; *{step["explanation"]}*'
		streamlit.markdown(header, unsafe_allow_html=True)

		# Matrix after this operation
		matrix_latex = gauss_solver.matrix_to_latex(
			step['matrix'],
			streamlit.session_state.var_names
		)
		streamlit.latex(matrix_latex)

	# Bottom controls (duplicate for easy access after scrolling)
	bottom_action = render_step_controls(
		'bottom', can_advance, is_showing_all, total_steps
	)

	# Handle any button press (top or bottom)
	action = top_action or bottom_action
	if action:
		handle_step_action(action, total_steps)

	# Show final outcome after all steps are revealed
	if is_showing_all or current >= total_steps:
		streamlit.divider()
		render_outcome(result)


#============================================


def main() -> None:
	"""Main Streamlit application."""
	streamlit.set_page_config(
		page_title='Linear Equation Solver',
		page_icon='equal',
		layout='wide'
	)

	streamlit.title('Linear Equation Solver')
	streamlit.write(
		'Solve systems of linear equations using Gaussian elimination '
		'with exact rational arithmetic.'
	)

	# Sidebar controls
	with streamlit.sidebar:
		streamlit.header('Settings')

		# Number of variables slider
		num_vars = streamlit.slider(
			label='Number of variables',
			min_value=2,
			max_value=6,
			value=3,
			step=1
		)

		# Detail level radio
		detail_level = streamlit.radio(
			label='Detail level',
			options=[
				'Final Answer Only',
				'Matrix Steps',
				'Steps with Explanations'
			],
			index=2
		)

		# System type radio
		system_type = streamlit.radio(
			label='System type (for random generation)',
			options=['Unique', 'Inconsistent', 'Dependent', 'Mixed'],
			index=0
		)

		# Randomize button
		system_type_value = system_type.lower()
		if streamlit.button(
			'Randomize', use_container_width=True
		):
			randomize_system(num_vars, system_type_value)
			streamlit.rerun()

	# Initialize session state
	initialize_session_state(num_vars)

	# Main area - coefficient input
	render_matrix_input(num_vars, streamlit.session_state.var_names)

	streamlit.divider()

	# Solve button
	if streamlit.button(
		'Solve', type='primary', use_container_width=True
	):
		result = gauss_solver.solve_system(
			streamlit.session_state.matrix,
			streamlit.session_state.var_names
		)
		streamlit.session_state.solve_result = result
		# Start with first step visible
		streamlit.session_state.current_step = 1
		streamlit.session_state.all_steps_shown = False
		streamlit.rerun()

	# Display solution based on detail level
	if streamlit.session_state.get('solve_result') is not None:
		result = streamlit.session_state.solve_result

		if detail_level == 'Final Answer Only':
			render_outcome(result)
		else:
			render_steps(result, detail_level)


#============================================


if __name__ == '__main__':
	main()
