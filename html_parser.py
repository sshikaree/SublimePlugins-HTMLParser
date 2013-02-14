import sublime, sublime_plugin, re, sys


class HtmlParserCommand(sublime_plugin.TextCommand):
	def run(self, edit):

		settings = sublime.load_settings("HTMLParser.sublime-settings")
		self.spacing1 = settings.get("spacing1", " ")
		self.spacing2 = settings.get("spacing2", "\n\n")
		self.do_active = settings.get("do_active", False)


		self.cssviewlist = self.getCSSViews()
		self.class_selectors, self.id_selectors = self.getValues()

		if len(self.cssviewlist) == 0:
			sys.exit(0)
		elif len(self.cssviewlist) > 1:
			cssfiles = [v.file_name() for v in self.cssviewlist]
			sublime.active_window().show_quick_panel(cssfiles, self.setView)
		elif len(self.cssviewlist) == 1:
			self.selectedview = self.cssviewlist[0]
			self.parsCSS(self.selectedview, self.class_selectors, self.id_selectors)
			

		
		# print self.class_selectors, self.id_selectors

		

	def setView(self, val):
		if val == -1:
			sys.exit(0)
		self.selectedview = self.cssviewlist[val]
		# print self.selectedview
		self.parsCSS(self.selectedview, self.class_selectors, self.id_selectors)

	def getValues(self):
		sublime.status_message('Searching selectors...')
		selections = self.view.sel()
		class_patt = re.compile(r'class=\"(.+?)\"')
		id_patt = re.compile(r'id=\"(.+?)\"')

		class_selectors_set = set()
		id_selectors_set = set()

		for sel in selections:
			selection = self.view.substr(sel)
			class_selectors = class_patt.findall(selection)
			for selector in class_selectors:
				class_selectors_set.update(selector.split(' '))

			id_selectors_set.update(id_patt.findall(selection))
		
		return class_selectors_set, id_selectors_set

	def getCSSViews(self):
		cssviewlist = []
		for v in sublime.active_window().views():
			if v.file_name()[-3:] == 'css':
				# print v.file_name(), v.id()
				cssviewlist.append(v)
		return cssviewlist


	def parsCSS(self, selectedview, class_selectors, id_selectors):
		sublime.status_message('Parsing CSS files...')
		edit = None
		v = selectedview
		css_text = v.substr(sublime.Region(0, v.size()))
		# length = v.size()
		# print css_text
		for cl_sel in class_selectors:
			if not re.compile(r'\.%s(?:\b|\{)' % cl_sel).search(css_text):
				length = v.size()
				print cl_sel
				edit = v.begin_edit()
				v.insert(edit, length, '\n.' + cl_sel + self.spacing1 + '{' + self.spacing2 +'}')
				v.end_edit(edit)


		for id_sel in id_selectors:
			if not re.compile(r'\#%s(?:\b|\{)' % id_sel).search(css_text):
				length = v.size()
				print id_sel
				edit = v.begin_edit()
				v.insert(edit, length, '\n#' + id_sel + self.spacing1 + '{' + self.spacing2 + '}')
				v.end_edit(edit)
		if self.do_active:
			sublime.active_window().focus_view(v)

		sublime.status_message('Done!')
