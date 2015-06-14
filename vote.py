# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

####################
## Mergeable Vote ##
####################

class MergeableVote:
	def __init__(self, iv, parent):
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
		self.sort()

	def sort(self):
		self.subs.sort(key=lambda v: -len(v.yea))

	def is_descendant_of(self, other):
		p = self
		while p:
			if p == other:
				return True
			p = p.parent
		return False

	def remove_self(self):
		if self.parent:
			self.parent.subs.remove(self)

	# copy the other vote's yeas/nays and text into this vote
	# this is used as part of a multimerge
	def copy(self, other):
		assert other != self
	
		self.yea.update(other.yea)
		self.nay.update(other.nay)
		self.nay.difference_update(self.yea)
		self.texts.update(other.texts)		

		if self.parent:
			self.parent.sort()

	def merge(self, other):
		assert other != self
		assert not self.is_descendant_of(other)
		if other.parent:
			other.parent.subs.remove(other)
	
		self.yea.update(other.yea)
		self.nay.update(other.nay)
		self.nay.difference_update(self.yea)
		self.texts.update(other.texts)

		for other_sub in other.subs:
			out = other_sub
			for my_sub in list(self.subs):
				if my_sub.primary_text == out.primary_text:
					out.merge(my_sub)
			out.parent = self
			self.subs.append(out)
		
		self.sort()
		if self.parent:
			self.parent.sort()

	def __repr__(self):
		return ('<MergeableVote +%d -%d ' % (len(self.yea), len(self.nay)))+	\
			repr(self.primary_text)+': '+ repr(self.subs)+'>'
