CSS Dust Cleaner
================

Tool that removes unused CSS selectors by searching through definied directories


Install 
--------------
```sh
pip install --upgrade git+https://github.com/mkriss/css-dust-cleaner

```




Example
--------------
```sh
from dustcleaner import Processor

p = Processor(('bootstrap_example','/home/ubuntu/www/example'))
p.start()

Cleaned css paths

/home/kriss/code/tests/css-cleaner/example/subdir/dist/subpage.css
/home/kriss/code/tests/css-cleaner/example/dist/page.css
/home/kriss/code/tests/css-cleaner/bootstrap_example/css/dist/style.css
/home/kriss/code/tests/css-cleaner/bootstrap_example/css/dist/bootstrap.css
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
Dust cleaning finished. Now your files are 6% of original css files size 


```





Inspired and partly forked from By Peter Bengtsson, 2012-2014 
https://github.com/peterbe/mincss