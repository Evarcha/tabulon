# Tabulon
# Copyright (c) 2015 BeaconHill <theageofnewstars@gmail.com>
# See `LICENSE.txt` for license terms.

####################
## Mergeable Vote ##
####################

from copy import copy, deepcopy

class IVSet(object):
	def __init__(self, ivs=[]):
		self.set = set(ivs)

	def __deepcopy__(self, memo):
		new = IVSet.__new__(IVSet)
		new.set = set()

		for entry in self.set:
			if isinstance(entry, IVSet) or isinstance(entry, IVInverter):
				new.set.add(deepcopy(entry, memo))
			else:
				# it must be a ParsedVote, don't copy it
				new.set.add(entry)

		return new

	def empty(self):
		return len(self.set) <= 0

	def invert(self):
		if self.empty():
			return self
		return IVInverter(self)

	# this returns something new
	def add(self, other):
		if self.empty():
			return other
		if isinstance(other, IVSet):
			return IVSet(self.set | other.set)
		elif not other.empty():
			return IVSet(self.set | set(other))
		else:
			return self

	def get_votes(self):
		yea = set()
		nay = set()

		for sub in self.set:
			sub_yea, sub_nay = sub.get_votes()
			yea.update(sub_yea)
			nay.update(sub_nay)

		nay.difference_update(yea)
		return yea, nay


class IVInverter(object):
	def __init__(self, ivset):
		self.ivset = ivset

	def get_votes(self):
		yeas, nays = self.ivset.get_votes()
		return nays, yeas

	# this returns something new
	def add(self, other):
		if other.empty():
			return self
		return IVSet([self, other])

	def empty(self):
		return False

	def invert(self):
		return self.ivset

class MergeableVote(object):
	# pass either text or iv, but not both
	def __init__(self, iv=None, parent=None, text=None):
		self.stack = None
		self.hidden = False
		if text is not None:
			self.parent = parent
			self.primary_text = text
			self.texts = set(text)
			self.subs = []
			self.yea = set()
			self.nay = set()
			self.primary_ivs = set()
			self.vote_ivs = IVSet()
		else:
			self.parent = parent
			self.yea = iv.yea
			self.nay = iv.nay
			self.primary_text = iv.text
			self.texts = set([iv.text])
			self.subs = [ MergeableVote(sub, self) for sub in iv.subs.values() ]
			self.primary_ivs = set([iv])		# these IVs' children appear under this MV
			self.vote_ivs = IVSet([iv])		# these IVs contribute votes to this MV
				# the wrapper class is used to ensure that inversions work correctly
			self._sort()

	# should only be called from UndoStack
	def _set_stack(self, stack):
		self.stack = stack

	def hide(self):
		self.dirty()
		self.hidden = True
		for sub in self.subs:
			sub.hide()

	def unhide(self):
		self.dirty()
		self.hidden = False
		if self.parent:
			self.parent.unhide()

	def recompute_votes(self):
		self.dirty()

		all_subs_hidden = True
		for sub in self.subs:
			sub.recompute_votes()
			if not sub.hidden:
				all_subs_hidden = False
		self._sort()

		new_yea, new_nay = self.vote_ivs.get_votes()

		if not len(new_yea) and not len(new_nay) and all_subs_hidden:
			self.hidden = True
		elif self.hidden and ( new_yea != self.yea or new_nay != self.nay ):
			self.unhide()

		self.yea, self.nay = new_yea, new_nay

	# should only be called from iv_setup_mv_mode
	def _mark_ivs(self):
		for iv in self.primary_ivs:
			iv._set_mv(self)
		for sub in self.subs:
			sub._mark_ivs()

	def dirty(self):
		if self.parent:
			self.parent.dirty()
		elif self.stack:
			self.stack.dirty()

	def _sort(self):
		self.subs.sort(key=lambda v: -len(v.yea))

	def rename(self, new_text):
		self.dirty()
		self.unhide()
		self.texts.add(new_text)
		self.primary_text = new_text

	def _trickle(self, other):
		self.yea.update(other.yea)
		self.nay.update(other.nay)
		self.vote_ivs = self.vote_ivs.add(other.vote_ivs)
		for sub in other.subs:
			self._trickle(sub)

	def trickle(self):
		self.dirty()
		self.unhide()
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
		self.hidden = False
		if self.parent:
			self.parent.subs.remove(self)
			self.parent = None

	def add(self, other):
		self.dirty()
		self.unhide()
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
		self.unhide()
		assert other != self

		self.yea.update(other.yea)
		self.nay.update(other.nay)
		self.nay.difference_update(self.yea)
		self.texts.update(other.texts)

		self.vote_ivs = self.vote_ivs.add(other.vote_ivs)

		if self.parent:
			self.parent._sort()

	def invert(self):
		self.dirty()
		self.yea, self.nay = self.nay, self.yea
		self.vote_ivs = self.vote_ivs.invert()
		if self.parent:
			self.parent._sort()

	def merge(self, other):
		self.dirty()
		self.unhide()
		assert other != self
		assert not self.is_descendant_of(other)
		other.remove_self()

		self.yea.update(other.yea)
		self.nay.update(other.nay)
		self.nay.difference_update(self.yea)
		self.texts.update(other.texts)

		self.vote_ivs = self.vote_ivs.add(other.vote_ivs)
		self.primary_ivs.update(other.primary_ivs)

		for other_sub in list(other.subs):
			self.add(other_sub)

		self._sort()
		if self.parent:
			self.parent._sort()

	def __repr__(self):
		return ('<MergeableVote +%d -%d ' % (len(self.yea), len(self.nay)))+	\
			repr(self.primary_text)+': '+ repr(self.subs)+'>'

	def __deepcopy__(self, memo):
		new = MergeableVote.__new__(MergeableVote)
		for key, value in self.__dict__.items():
			if key in [ 'primary_ivs' ]:
				new.__dict__[key] = copy(value)
			else:
				new.__dict__[key] = deepcopy(value, memo)
		return new
