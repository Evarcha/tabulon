from termutil import *

class BBNode(object):
	def format(self, sgrs):
		return ''

	@staticmethod
	def hasChildren():
		return False
		
	@staticmethod
	def hasArgument():
		return False
	
	def __repr__(self):
		return '['+self.__class__.__name__+': '+self.format([])+']'

class BBTextNode(BBNode):
	def __init__(self, text):
		self.text = text
	def format(self, sgrs):
		return self.text

class BBOmNomNode(BBNode):
	def setChildren(self, children):
		pass
	@staticmethod
	def hasChildren(self):
		return True	

class BBParentNode(BBNode):
	def format(self, sgrs=None):
		if sgrs is None:
			sgrs = []
	
		try:
			out = ''
			for child in self.children:
				out += child.format(sgrs)
			return out
		except AttributeError:
			pass # I have no children
	def setChildren(self, children):
		self.children = children
	
	@staticmethod
	def hasChildren():
		return True

class BBSGRNode(BBParentNode):
	def format(self, sgrs=None):
		if sgrs is None:
			sgrs = []
	
		mysgrs = self.getSGRs()
		allsgrs = sgrs+mysgrs
		if mysgrs:
			return sgr(*mysgrs)+BBParentNode.format(self, allsgrs)+sgr()+sgr(*sgrs)
		else:
			return BBParentNode.format(self, sgrs)

class BBBoldNode(BBSGRNode):
	def getSGRs(self):
		return [BOLD]

class BBItalicNode(BBSGRNode):
	def getSGRs(self):
		return [INVERSE]

class BBUnderlineNode(BBSGRNode):
	def getSGRs(self):
		return [UNDERLINE]

class BBStrikeNode(BBSGRNode):
	def getSGRs(self):
		return [FG_HRED]

class BBColorNode(BBSGRNode):
	def __init__(self, arg):
		self.transparent = arg.lower().strip() in ['transparent']

	def getSGRs(self):
		if self.transparent:
			return [BLINK]
		return []

	@staticmethod
	def hasArgument():
		return True	

class BBLinkNode(BBParentNode):
	def __init__(self, arg):
		self.url = arg
	def format(self, sgrs=None):
		if sgrs is None:
			sgrs = []
		
		return \
			sgr(FG_HCYN, BOLD)+BBParentNode.format(self, sgrs+[FG_HCYN, BOLD])+' '+\
			sgr(FG_LBLU, BOLD)+'['+self.url+']'+\
			sgr()+sgr(*sgrs)

	@staticmethod
	def hasArgument():
		return True

class BBQuoteNode(BBParentNode):
	def __init__(self, arg):
		items = arg.split(',')
		self.poster = items[0].strip()
		self.postno = None
		try:
			kvs = {
				k.strip().lower(): v.strip().lower()
				for k, v
				in [ item.split(':', 2) for item in items[1:] ]
			}
			self.postno = int(kvs['post'])
		except (ValueError, IndexError, KeyError):
			pass
	
	def __repr__(self):
		return '['+self.__class__.__name__+': '+self.poster+' p'+str(self.postno)+\
			' '+self.format([])+']'

	@staticmethod
	def hasArgument():
		return True

bb_normal_nodes = {
	'b': BBBoldNode,
	'i': BBItalicNode,
	'u': BBUnderlineNode,
	's': BBStrikeNode,
	'spoiler': BBParentNode,
	'url': BBLinkNode,
	'color': BBColorNode,
	'font': BBParentNode,
	'size': BBParentNode
}

bb_quoteseparate_nodes = {
	'quote': BBQuoteNode
}

def bb_normal_parse(input):
	return bb_custom_parse(input, bb_normal_nodes)

def bb_format_sgr(input):
	return bb_normal_parse(input).format()

def bb_read_quote_elements(input):
	main_node = bb_custom_parse(input, bb_quoteseparate_nodes)
	return [
		(quote.poster, quote.postno, quote.format().strip())
			for quote in
		filter(lambda x: x.__class__ is BBQuoteNode, main_node.children)
	]

def bb_custom_parse(input, node_types):
	node = BBParentNode()
	tagname = None
	children = []
	
	stack = []
	
	text_start = 0
	
	i = -1
	while True:
		i += 1
		if i >= len(input):
			break
		
		if input[i] == '[':
			# we got the start of a tag here!
			
			end_of_tag = input.find(']', i)
			
			if end_of_tag < 0:
				continue
			
			interior = input[i+1:end_of_tag].strip()
			
			if interior[0] == '/':
				# Closing tag
			
				if len(stack) < 1:
					# It's the root node! We can't close that!
					continue
				
				# What tag do we think we're closing?
				closing_tagname = interior[1:].strip().lower()

				if closing_tagname != tagname:
					# That's not the current tag name. Don't do anything, output it as a
					# literal.
					continue
				
				# Close the current tag.
				if text_start != i:
					# There's text here, add it.
					children.append(BBTextNode(input[text_start:i]))
				
				# Set the node's children.
				node.setChildren(children)

				# Pop the stack.
				node, tagname, children = stack.pop()
				
				# Skip past the end of the close tag.
				i = end_of_tag
				text_start = end_of_tag+1
			else:
				# We're an opening tag of some sort.				
				arg = None
			
				equals_pos = interior.find('=')
			
				if equals_pos >= 0:
					# We got an arg!
					arg = interior[equals_pos+1:].strip()
					interior = interior[:equals_pos]

					if arg[0] in ['"', "'"]:
						arg = arg[1:]
					if arg[-1] in ['"', "'"]:
						arg = arg[:-1]
				
				newtagname = interior.lower()
							
				if newtagname not in node_types:	
					# don't know this tag
					continue
			
				newtagclass = node_types[newtagname]
			
				if text_start != i:
					# There's text here, add it.
					children.append(BBTextNode(input[text_start:i]))
			
				if newtagclass.hasArgument():
					newnode = newtagclass(arg)
				else:
					newnode = newtagclass()

				children.append(newnode)
						
				if newtagclass.hasChildren():
					# We don't need to add anything to the stack for nodes that don't
					# have children.
					
					stack.append((node, tagname, children))
					node = newnode
					tagname = newtagname
					children = []
			
				i = end_of_tag
				text_start = end_of_tag+1
	
	# It's over!
	# Add any dangling text.
	if text_start != i:
		children.append(BBTextNode(input[text_start:i]))
				
	# Close any unclosed tags.
	while stack:
		# Set the node's children.
		node.setChildren(children)
		
		# Pop the stack.
		node, tagname, children = stack.pop()
	
	# Set the root's children.
	node.setChildren(children)
		
	return node