import sublime, sublime_plugin, re, sys


class HtmlParserCommand(sublime_plugin.TextCommand):
	def run(self, edit):

		settings = sublime.load_settings("HTMLParser.sublime-settings")
		self.spacing1 = settings.get("spacing1", " ")
		self.spacing2 = settings.get("spacing2", "\n\n")
		self.do_active = settings.get("do_active", False)

		self.cssviewlist = self.getCSSViews()
		self.selectors_list = self.getValues()

		if len(self.cssviewlist) == 0:
			sys.exit(0)
		elif len(self.cssviewlist) > 1:
			cssfiles = [v.file_name() for v in self.cssviewlist]
			sublime.active_window().show_quick_panel(cssfiles, self.setView)
		elif len(self.cssviewlist) == 1:
			self.selectedview = self.cssviewlist[0]
			self.parsCSS(self.selectedview, self.selectors_list)
			
		

	def setView(self, val):
		if val == -1:
			sys.exit(0)
		self.selectedview = self.cssviewlist[val]
		# print self.selectedview
		self.parsCSS(self.selectedview, self.selectors_list)


	def getValues(self):
		sublime.status_message('Searching selectors...')
		selections = self.view.sel()
		all_patt = re.compile(r'(?:class=\"(.+?)\")|(?:id=\"(.+?)\")')

		selectors_list = []

		for sel in selections:
			selection = self.view.substr(sel)
			selectors = all_patt.findall(selection)
			for selector in selectors:
				# selector[0] - class, if exists
				# selector[1] - id, if exists
				if selector[1] != '' and ('#' + selector[1]) not in selectors_list:
					selectors_list.append(('#' + selector[1]))

				elif selector[0] != '':
					for class_sel in selector[0].split(' '):
						if ('.' + class_sel) not in selectors_list:
							selectors_list.append('.' + class_sel)		
		return selectors_list

	def getCSSViews(self):
		cssviewlist = []
		for v in sublime.active_window().views():
			if v.file_name()[-3:] == 'css':
				# print v.file_name(), v.id()
				cssviewlist.append(v)
		return cssviewlist


	def parsCSS(self, selectedview, selectors_list):
		sublime.status_message('Parsing CSS files...')
		edit = None
		v = selectedview
		css_text = v.substr(sublime.Region(0, v.size()))
		for selector in selectors_list:
			if not re.compile(r'%s(?:\b|\{)' % selector).search(css_text):
				length = v.size()
				print selector
				edit = v.begin_edit()
				v.insert(edit, length, '\n' + selector + self.spacing1 + '{' + self.spacing2 +'}')
				v.end_edit(edit)

		if self.do_active:
			sublime.active_window().focus_view(v)

		sublime.status_message('Done!')
