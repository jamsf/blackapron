import sys
import io
import argparse
import logging

import bluescraper

ACTIONS = ['interactive', 'thisweek', 'random']

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--action', required=True, help='Options: {0}'.format(ACTIONS))

    args = parser.parse_args()
    action = args.action
    if not action in ACTIONS:
    	logging.error('"{0}" not an accaptable action, Please use: {1}'.format(action, ACTIONS))
    	exit(1)

    if action == 'interactive':
    	interactive_mode()
    elif action == 'thisweek':
    	get_meals_this_week()
    elif action == 'random':
    	get_random_meals()

def generate_shopping_list():
	bar_print('Generating Shopping List...')

	print 'Not implemented yet...'

def get_meals_this_week():
	bar_print('Generating This Week\'s Meal Plan!')
	print 'Loading meals for this week...'
	recipes = bluescraper.get_recipes_this_week()
	print 'Loading Complete!'

	confirmed = False
	while not confirmed:
		print '\nPlease pick as many meals as you want below (comma-separated numbers):'
		num = 1
		for r in recipes:
			print '{0} - {1}'.format(str(num), r.name)
			num += 1

		recipe_choices = []
		valid_numbers = False
		while not valid_numbers:
			valid_numbers = True
			recipe_choices = []
			input_str = raw_input('\n> ')
			try:
				choices = input_str.split(',')
				choices = [int(x)-1 for x in choices]
			except:
				print 'Invalid input'
				valid_numbers = False
				continue
			for choice in choices:
				if choice > len(recipes) or choice < 0:
					valid_numbers = False
					print 'Please enter valid numbers'
					break
				recipe_choices.append(recipes[choice])
		print '\nYou chose these recipes:\n'
		for r in recipe_choices:
			print '\t' + r.name
		confirmed = yes_no_question('\nAre you sure this is what you want to eat?')

	print 'Congrats! You have a meal plan for the week!'

def interactive_mode():
	logging.error('Random meal plans not implemented yet.')
	exit(1)


def get_random_meals():
	logging.error('Random meal plans not implemented yet.')
	exit(1)

def bar_print(msg):
	print '\n------------------------------------------'
	print msg
	print '------------------------------------------\n'


def yes_no_question(ques):
	input_str = raw_input('{0}? (y/n)\n> '.format(ques))
	if input_str.lower() == 'yes' or input_str.lower() == 'y':
		return True
	return False

if __name__ == '__main__':
	main()