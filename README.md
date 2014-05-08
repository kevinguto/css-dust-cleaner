CSS Dust Cleaner
================

Tool that removes unused CSS selectors by searching through definied directories


Example
--------------
```sh

p = Processor(('bootstrap_example','example'))
p.start()

Cleaned css paths

/home/kriss/code/tests/css-cleaner/example/subdir/dist/subpage.css
/home/kriss/code/tests/css-cleaner/example/dist/page.css
/home/kriss/code/tests/css-cleaner/bootstrap_example/css/dist/style.css
/home/kriss/code/tests/css-cleaner/bootstrap_example/css/dist/bootstrap.css
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
Dust clean finished. Now your files are 6% of original css files size 


```



Prerequisites
--------------
```sh
pip install -r requirements.txt
```



Inspired and partly forked from By Peter Bengtsson, 2012-2014 
https://github.com/peterbe/mincss