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
```python
from dustcleaner import Processor

p = Processor((('bootstrap_example',None),
			   ('example','/home/kriss/wwwpage/static/example')),
			     verbose=False)
p.start()

```

Example output
--------------
```sh
Cleaned css paths

/home/kriss/wwwpage/static/example/page.css
/home/kriss/wwwpage/static/example/subdir/subpage.css
/home/kriss/wwwpage/bootstrap_example/css/dist/style.css
/home/kriss/wwwpage/bootstrap_example/css/dist/bootstrap.css
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
Dust cleaning finished. Now your files are 6% of original css files size 


```


ToDo
--------------

* Add Javascript selector search for jquery and js.
* Fix media querie bug. ( Commenting inside media querie, before selector all the styles are lost. )

<br />
<br />
<br />

Inspired and partly forked from By Peter Bengtsson, 2012-2014 
https://github.com/peterbe/mincss