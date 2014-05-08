#!/usr/bin/env python
import sys, os, fnmatch, re, random, time, datetime

import ntpath


from lxml import etree
from lxml.cssselect import CSSSelector, SelectorSyntaxError, ExpressionError

try:
    unicode
except NameError:
    unicode = str


try:
	from urllib.parse import urljoin
	from urllib.request import urlopen
except ImportError:
	from urlparse import urljoin
	from urllib import urlopen



RE_FIND_MEDIA = re.compile('(@media.+?)(\{)', re.DOTALL | re.MULTILINE)
RE_NESTS = re.compile('@(-|keyframes).*?({)', re.DOTALL | re.M)
RE_CLASS_DEF = re.compile('\.([\w-]+)')
RE_ID_DEF = re.compile('#([\w-]+)')

EXCEPTIONAL_SELECTORS = (
    'html',
)

def _get_random_string():
    p = 'abcdefghijklmopqrstuvwxyz'
    pl = list(p)
    random.shuffle(pl)
    return ''.join(pl)

def main():
	print('\nExample\n')
	print("p = Processor(('bootstrap_example','/home/ubuntu/www/example')) # Clean directories")
	print("p.start()\n\n")


class Processor(object):
	def __init__(self, base_dirs, patterns = ('*.html','*.js','*.css'), clean_dir_name='dist' , verbose=False, debug=False, optimize_lookup=True):
		self.debug = debug
		self.file_paths = []
		self.base_dirs = []
		for d in base_dirs:
			self.base_dirs.append(os.path.abspath(d))

		self.patterns = patterns
		self.clean_dir_name = clean_dir_name
		self.ignore_dir = [clean_dir_name,]
		self.blocks = {}
		self.pages = []
		self.css = []
		self._bodies = []
		self.optimize_lookup = optimize_lookup
		self._all_ids = set()
		self._all_classes = set()
		self.verbose = verbose
		self.ITERA = 0

	def start(self):
		self._get_paths()
		if self.verbose:
			self.print_paths()
		self.analyze()
		self.write()

	def write(self):
		if self.verbose:
			print("HTML FILES ".ljust(79, '-'))
			for each in self.pages:
				print("File %s" % each.path)
				print("On line %s" % each.line)
				print('- ' * 40)
				print("BEFORE")
				print(each.before)
				print('- ' * 40)
				print("AFTER:")
				print(each.after)
				print("\n")

		if self.verbose:
			print("CSS ".ljust(79, '-'))

		total_size_before = 0
		total_size_after = 0

		new_css_paths = []

		for each in self.css:
			if len(each.before.strip()) != 0:
				print('- ' * 40)
				print("\nFile %s" % each.path)
				beforesize = len(each.before)
				aftersize = len(each.after)
				total_size_before = total_size_before + beforesize
				total_size_after = total_size_after + aftersize

				smaller = ((100*aftersize) / beforesize)
				print(str(smaller) +"% of original css file \n")
				print('- ' * 40)

			if self.verbose:
				print("BEFORE")
				print(each.before)
				print('- ' * 40)
				print("AFTER:")
				print(each.after)


			dist_dir = ntpath.dirname(each.path) + '/' + self.clean_dir_name + '/'
			if not os.path.exists(dist_dir):
				os.makedirs(dist_dir)

			new_path = dist_dir + ntpath.basename(each.path)
			file = open(new_path, "w")
			file.write(each.after)
			file.close()
			new_css_paths.append(new_path)

		print('Cleaned css paths\n')
		for p in new_css_paths:
			print(p)

		print('- ' * 40)
		smaller = ((100*total_size_after) / total_size_before)
		print('Dust cleaning finished. Now your files are '+ str(smaller) +"% of original css files size \n")


	def make_timestamp(self):
		ct = datetime.datetime.now()
		timestamp = time.mktime(ct.timetuple())
		return timestamp

	def find_files(self, directory):
		for root, dirs, files in os.walk(directory):
			if ntpath.split(root)[1].strip() in self.ignore_dir:
				#'ignore this dir'
				continue
			for basename in files:
				for pattern in self.patterns:
					if fnmatch.fnmatch(basename, pattern):
						filename = os.path.join(root, basename)
						yield File(filename,pattern)

	def _get_paths(self):
		for base_dir in self.base_dirs:
			for f in self.find_files(base_dir):
				self.file_paths.append(f)

	def print_paths(self):
		print('PATHS\n')
		for p in self.file_paths:
			print(p.path)

	def analyze(self):

		for f in self.file_paths:
			file = open(f.path, 'r')
			content = file.read()
			if f.pattern == '*.html':
				self.process_html(content.strip(), f.path)

		for f in self.file_paths:
			file = open(f.path, 'r')
			content = file.read()
			if f.pattern == '*.css':
				key = ('css',f.path)
				self.blocks[key] = content

		for identifier in sorted(self.blocks.keys(), key=lambda x: str(x[0])):
			content = self.blocks[identifier]
			# print 'identifier', identifier[1]
			processed = self._process_content(content, self._bodies )
			self.ITERA = self.ITERA + 1

			if isinstance(identifier[0], int):
				line, path = identifier
				self.pages.append(
				    PageResult(
				        line,
				        path,
				        content,
				        processed
				    )
				)
			else:
				filetype, path = identifier
				self.css.append(
				    CssResult(
				        path,
				        content,
				        processed
				    )
				)
		

	def process_html(self, html, path):
		parser = etree.HTMLParser(encoding='utf-8')
		tree = etree.fromstring(html.encode('utf-8'), parser).getroottree()
		page = tree.getroot()

		if page is None:
			print(repr(html))
			raise ParserError('Could not parse the html')

		lines = html.splitlines()
		body, = CSSSelector('body')(page)
		self._bodies.append(body)
		if self.optimize_lookup:
			for each in body.iter():
				identifier = each.attrib.get('id')
				if identifier:
				    self._all_ids.add(identifier)
				classes = each.attrib.get('class')
				if classes:
				    for class_ in classes.split():
				        self._all_classes.add(class_)

		for style in CSSSelector('style')(page):
		    first_line = style.text.strip().splitlines()[0]
		    for i, line in enumerate(lines):
				if line.count(first_line):
					key = (i + 1, path)
					self.blocks[key] = style.text
					break

		# for link in CSSSelector('link')(page):
		# 	if (
		# 	    link.attrib.get('rel', '') == 'stylesheet' or
		# 	    link.attrib['href'].lower().split('?')[0].endswith('.css')
		# 	):
		# 	    link_url = self.make_absolute_url(url, link.attrib['href'])
		# 	    key = (link_url, link.attrib['href'])
		# 	    self.blocks[key] = self._download(link_url)
		# 	    if self.preserve_remote_urls:
		# 	        self.blocks[key] = self._rewrite_urls(
		# 	            self.blocks[key],
		# 	            link_url
		# 	        )

	def _process_content(self, content, bodies, is_improved_inner=False):
		# Find all of the unique media queries



		comments = []
		_css_comments = re.compile(r'/\*.*?\*/', re.MULTILINE | re.DOTALL)
		no_mincss_blocks = []

		def commentmatcher(match):
			whole = match.group()
			# are we in a block or outside
			nearest_close = content[:match.start()].rfind('}')
			nearest_open = content[:match.start()].rfind('{')
			next_close = content[match.end():].find('}')
			next_open = content[match.end():].find('{')

			outside = False
			if nearest_open == -1 and nearest_close == -1:
			    # it's at the very beginning of the file
			    outside = True
			elif next_open == -1 and next_close == -1:
			    # it's at the very end of the file
			    outside = True
			elif nearest_close == -1 and nearest_open > -1:
			    outside = False
			elif nearest_close > -1 and nearest_open > -1:
			    outside = nearest_close > nearest_open
			else:
			    raise Exception('can this happen?!')

			if outside:
			    temp_key = '@%scomment{}' % _get_random_string()
			else:
			    temp_key = '%sinnercomment' % _get_random_string()
			    if re.findall(r'\bno mincss\b', match.group()):
			        no_mincss_blocks.append(temp_key)

			comments.append(
			    (temp_key, whole)
			)
			return temp_key

		content = _css_comments.sub(commentmatcher, content)


		if no_mincss_blocks:
		    no_mincss_regex = re.compile(
		        '|'.join(re.escape(x) for x in no_mincss_blocks)
		    )
		else:
		    no_mincss_regex = None

		nests = [(m.group(1), m) for m in RE_NESTS.finditer(content)]
		_nests = []

		for _, m in nests:
		    __, whole = self._get_contents(m, content)
		    _nests.append(whole)

		# once all nests have been spotted, temporarily replace them


		queries = [(m.group(1), m) for m in RE_FIND_MEDIA.finditer(content)]
		inner_improvements = []

		for nest in _nests:
		    temp_key = '@%snest{}' % _get_random_string()
		    inner_improvements.append(
		        (temp_key, nest, nest)
		    )




		

		# Consolidate the media queries
		for (query, m) in queries:

			inner, whole = self._get_contents(m, content)

			# print 'query inner ', query, ' ', inner, ' \n'

			improved_inner = self._process_content(inner, bodies, is_improved_inner=True)

			# print 'query improved_inner ', query, ' ', improved_inner, ' '

			if improved_inner.strip():
				improved = query.rstrip() + ' {' + improved_inner + '}'
			else:
				improved = ''
			temp_key = '@%s{}' % _get_random_string()
			inner_improvements.append(
				(temp_key, whole, improved)
			)

		for temp_key, old, __ in inner_improvements:
		    assert old in content
		    content = content.replace(old, temp_key)

		_regex = re.compile('((.*?){(.*?)})', re.DOTALL | re.M)

		# print 'new queries ', queries


		_already_found = set()
		_already_tried = set()

		def matcher(match):
		    whole, selectors, bulk = match.groups()
		    selectors = selectors.split('*/')[-1].lstrip()

		    

		    if selectors.strip().startswith('@'):
		        return whole
		    if no_mincss_regex and no_mincss_regex.findall(bulk):
		        return no_mincss_regex.sub('', whole)

		    improved = selectors


		    

		    perfect = True
		    selectors_split = []

		    for x in selectors.split(','):
		    	# if is_improved_inner:
		    	# 	for z in x.split(' '):
		    	# 		if z.strip() and not z.strip().startswith(':'):
		    	# 			selectors_split.append(z.strip())
		    	# else:
	        	if x.strip() and not x.strip().startswith(':'):
	        		selectors_split.append(x.strip())
		    #   	if is_improved_inner:
		    #    	for z in x.split(' '):
		    #    		if z.strip() and not z.strip().startswith(':'):
		    #     		selectors_split.append(z.strip())
		    # else:


		    
		    for selector in selectors_split:
		        s = selector.strip()
		        if s in EXCEPTIONAL_SELECTORS:
		            continue

		        if s in _already_found:
		            found = True
		            # print ' _already_found '
		        elif s in _already_tried:
		            found = False
		            # print ' _already_tried '
		        else:
		            found = self._found(bodies, s)
		            # print 'searching .. ', s, found

		        if found:
		       	    # if is_improved_inner:
		               # print ' foundfoundfoundfound', s
		            _already_found.add(s)
		        else:
		            # if is_improved_inner:
			           # print 'NOT NOT  foundfoundfoundfound', s
		            _already_tried.add(s)
		            perfect = False
		            improved = re.sub(
		                '%s,?\s*' % re.escape(s),
		                '',
		                improved,
		                count=1
		            )

		  #   if is_improved_inner:
				# print 'is_improved_inner improved', improved


		    if perfect:
		        return whole
		    if improved != selectors:
		        if not improved.strip():
		            return ''
		        else:
		            improved = re.sub(',\s*$', ' ', improved)
		            whole = whole.replace(selectors, improved)
		    return whole

		fixed = _regex.sub(matcher, content)



		for temp_key, __, improved in inner_improvements:
		    assert temp_key in fixed
		    fixed = fixed.replace(temp_key, improved)
		for temp_key, whole in comments:
		    # note, `temp_key` might not be in the `fixed` thing because the
		    # comment could have been part of a selector that is entirely
		    # removed
		    fixed = fixed.replace(temp_key, whole)

		return fixed

	def _get_contents(self, match, original_content):
		# we are starting the character after the first opening brace
		open_braces = 1
		position = match.end()
		content = ''
		while open_braces > 0:
		    c = original_content[position]
		    if c == '{':
		        open_braces += 1
		    if c == '}':
		        open_braces -= 1
		    content += c
		    position += 1
		return (
		    content[:-1].strip(),
		    # the last closing brace gets captured, drop it
		    original_content[match.start():position]
		)

	def _found(self, bodies, selector):
		if self._all_ids:
		    try:
		        id_ = RE_ID_DEF.findall(selector)[0]
		        if id_ not in self._all_ids:
		            # don't bother then
		            return False
		    except IndexError:
		        pass

		if self._all_classes:
		    for class_ in RE_CLASS_DEF.findall(selector):
		        if class_ not in self._all_classes:
		            # don't bother then
		            return False

		r = self._selector_query_found(bodies, selector)
		return r

	def _selector_query_found(self, bodies, selector):
		selector = selector.split(':')[0]

		if '}' in selector:
		    # XXX does this ever happen any more?
		    return

		for body in bodies:
			try:
				for _ in CSSSelector(selector)(body):
					return True
			except SelectorSyntaxError:
				pass
				print('TROUBLEMAKER', sys.stderr)
				print(repr(selector), sys.stderr)
			except ExpressionError:
				pass
				print('EXPRESSIONERROR', sys.stderr)
				print(repr(selector), sys.stderr)
		return False

	@staticmethod
	def make_absolute_url(url, href):
		return urljoin(url, href)


class _Result(object):

    def __init__(self, before, after):
        self.before = before
        self.after = after


class PageResult(_Result):

    def __init__(self, line, path, *args):
        self.line = line
        self.path = path
        super(PageResult, self).__init__(*args)


class CssResult(_Result):

    def __init__(self, path, *args):
        self.path = path
        super(CssResult, self).__init__(*args)


def get_charset(response, default='utf-8'):
    """Return encoding."""
    try:
        # Python 3.
        return response.info().get_param('charset', default)
    except AttributeError:
        # Python 2.
        content_type = response.headers['content-type']
        split_on = 'charset='
        if split_on in content_type:
            return content_type.split(split_on)[-1]
        else:
            return default





	

class File(object):
	"""docstring for File"""
	def __init__(self, path, pattern):
		super(File, self).__init__()
		self.path = path
		self.pattern = pattern
		





if __name__ == '__main__':
    sys.exit(main())
