#!/usr/bin/env python

import sys

from dustcleaner import Processor

def example():
	print('example\n')
	p = Processor((('bootstrap_example',None),('example','/home/kriss/code/projects/css-dust-cleaner/static/example')))
	p.start()



if __name__ == '__main__':
    sys.exit(example())
