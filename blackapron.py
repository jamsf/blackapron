import sys
import io
import argparse



def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--action")

    args = parser.parse_args()

if __name__ == '__main__':
	input_str = raw_input('What do you want?\n> ')
	print input_str
	input_str = raw_input('are you sure?\n> ')
	if input_str == 'yes':
		print 'ok!'
	else:
		print 'ok nvm thdn'
	#main()