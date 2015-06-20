# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

####################
## Mergeable Vote ##
####################

class MergeableVote:
	def __init__(self, iv=None, parent=None, text=None):
		self.stack = None
		if text is not None:
			self.parent = parent
			self.primary_text = text
			self.texts = set(text)
			self.subs = []
			self.yea = set()
			self.nay = set()
		else:
			self.parent = parent
			self.yea = iv.yea
			self.nay = iv.nay
			self.primary_text = iv.text
			self.texts = set([iv.text])
			self.subs = [
				MergeableVote(sub, self)
					for sub in iv.subs.values()
					if len(sub.yea) or len(sub.nay)
			]
			self._sort()

	# should only be called from UndoStack
	def _set_stack(self, stack):
		self.stack = stack

	def dirty(self):
		if self.parent:
			self.parent.dirty()
		elif self.stack:
			self.stack.dirty()

	def _sort(self):
		self.subs.sort(key=lambda v: -len(v.yea))

	def defrost(self):
		# eventually, this will contain logic to help MergeableVote "awaken" from a
		# deep copy operation, and then call defrost on its children, for instance
		#for sub in self.subs:
		#	sub.defrost()
		# but for now there's nothing to do but
		pass

	def rename(self, new_text):
		self.dirty()
		self.texts.add(new_text)
		self.primary_text = new_text

	def _trickle(self, other):
		self.yea.update(other.yea)
		self.nay.update(other.nay)
		for sub in other.subs:
			self._trickle(sub)

	def trickle(self):
		self.dirty()
		for sub in self.subs:
			self._trickle(sub)
		self.nay.difference_update(self.yea)
		self.parent._sort()

	def recursive_children(self):
		out = list(self.subs)
		for sub in self.subs:
			out += sub.recursive_children()
		return out

	def is_descendant_of(self, other):
		p = self
		while p:
			if p == other:
				return True
			p = p.parent
		return False

	def remove_self(self):
		self.dirty()
		if self.parent:
			self.parent.subs.remove(self)
			self.parent = None

	def add(self, other):
		self.dirty()
		other.remove_self()

		merged = False
		for sub in self.subs:
			if sub.primary_text == other.primary_text:
				merged = True
				sub.merge(other)
				break

		if not merged:
			other.parent = self
			self.subs.append(other)
			self._sort()

	# copy the other vote's yeas/nays and text into this vote
	# this is used as part of a multimerge
	def copy(self, other):
		self.dirty()
		assert other != self

		self.yea.update(other.yea)
		self.nay.update(other.nay)
		self.nay.difference_update(self.yea)
		self.texts.update(other.texts)

		if self.parent:
			self.parent._sort()

	def invert(self):
		self.dirty()
		self.yea, self.nay = self.nay, self.yea
		if self.parent:
			self.parent._sort()

	def merge(self, other):
		self.dirty()
		assert other != self
		assert not self.is_descendant_of(other)
		other.remove_self()

		self.yea.update(other.yea)
		self.nay.update(other.nay)
		self.nay.difference_update(self.yea)
		self.texts.update(other.texts)

		for other_sub in list(other.subs):
			self.add(other_sub)

		self._sort()
		if self.parent:
			self.parent._sort()

	def __repr__(self):
		return ('<MergeableVote +%d -%d ' % (len(self.yea), len(self.nay)))+	\
			repr(self.primary_text)+': '+ repr(self.subs)+'>'
