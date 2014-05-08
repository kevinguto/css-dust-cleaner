#!/usr/bin/env python

from dustcleaner import Processor

def example():
	print('example\n')
	p = Processor(('bootstrap_example','example'))
	p.start()



if __name__ == '__main__':
    sys.exit(example())
