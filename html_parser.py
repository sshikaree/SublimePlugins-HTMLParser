import sublime, sublime_plugin, re

class HtmlParserCommand(sublime_plugin.TextCommand):
	def run(self, edit):

		settings = sublime.load_settings("HTMLParser.sublime-settings")
		self.spacing1 = settings.get("spacing1", " ")
		self.spacing2 = settings.get("spacing2", "\n\n")
		# self.view.insert(edit, 0, "Hello, World!")
		# sublime.message_dialog("Hello!")
		sublime.status_message('Searching selectors...')
		class_selectors, id_selectors = self.getValues()
		print class_selectors, id_selectors

		cssviewlist = self.getCSSViews()
		self.parsCSS(cssviewlist, class_selectors, id_selectors)
		
		

	def getValues(self):
		selections = self.view.sel()
		# selection = self.view.substr(self.view.sel()[0])
		class_patt = re.compile(r'class=\"(.+?)\"')
		id_patt = re.compile(r'id=\"(.+?)\"')

		class_selectors_set = set()
		id_selectors_set = set()

		for sel in selections:
			selection = self.view.substr(sel)
			# class_selectors_set = set()
			class_selectors = class_patt.findall(selection)
			for selector in class_selectors:
				class_selectors_set.update(selector.split(' '))

			id_selectors_set.update(id_patt.findall(selection))
		
		# class_selectors = class_selectors_set


		return class_selectors_set, id_selectors_set

	def getCSSViews(self):
		cssviewlist = []
		for v in sublime.active_window().views():
			if v.file_name()[-3:] == 'css':
				# print v.file_name(), v.id()
				cssviewlist.append(v)
		return cssviewlist


	def parsCSS(self, cssveiwlist, class_selectors, id_selectors):
		for v in cssveiwlist:
			css_text = v.substr(sublime.Region(0, v.size()))
			length = v.size()
			# print css_text
			for cl_sel in class_selectors:
				# if ('.' + cl_sel) not in css_text:
				if not re.compile(r'\.%s(?:\b|\{)' % cl_sel).search(css_text):
					print cl_sel
					edit = v.begin_edit()
					v.insert(edit, length, '\n.' + cl_sel + self.spacing1 + '{' + self.spacing2 +'}')
					length = length + len(cl_sel) + len(self.spacing1 + '{' + self.spacing2 +'}') + 2

					# v.end_edit()

			for id_sel in id_selectors:
				# if ('#' + id_sel) not in css_text:
				if not re.compile(r'\#%s(?:\b|\{)' % id_sel).search(css_text):
					print id_sel
					edit = v.begin_edit()
					v.insert(edit, length, '\n#' + id_sel + self.spacing1 + '{' + self.spacing2 + '}')
					length = length + len(id_sel) + len(self.spacing1 + '{' + self.spacing2 + '}') + 2
		if edit:
			self.view.end_edit(edit)
