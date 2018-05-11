#!/usr/bin/env sage
from sage.all import *
from sage.combinat.partition import _Partitions
from sage.combinat.skew_partition import SkewPartition, SkewPartitions
from sage.structure.unique_representation import CachedRepresentation

# HELPERS (only exist as helper functions for other things):
def is_weakly_decreasing(li):
    return all(li[i] >= li[i+1] for i in range(len(li)-1))


# MAIN:


class SkewPartition2 (SkewPartition):
    @staticmethod
    def __classcall_private__(cls, skp):
        skp = [_Partitions(_) for _ in skp]
        if skp not in SkewPartitions():
            raise ValueError("invalid skew partition: %s"%skp)
        return SkewPartitions()(skp)

    def is_skew_linked_diagram(self):
        """
        A __skew-linked diagram__ is a skew-shape `s` where both the row-shape and column-shape of `s` are partitions.

        TESTS:
            # empty skew
            sage: sp = SkewPartition2([[], []])
            sage: sp.is_skew_linked_diagram()
            True
            # # valid row shape but invalid col shape
            # sage: sp = SkewPartition2([[3, 2], [1, 0]])
            # sage: sp.is_skew_linked_diagram()
            # False
            # sage: assert False




        """
        return is_weakly_decreasing(self.row_lengths()) and is_weakly_decreasing(self.column_lengths())

    # DOESN"T MAKE SENSE BECAUSE OUR SKEWPARTITION ARE JUST OUTER AND INNER PART ALREADY DEFINED.
    # def minimal_containing_partition(self):
    #   """ Returns the smallest possible partition that could contain this skew shape.
    #   Simply go down and left of all cells in skew_shape
    #   """
    #   current_row_len = 0
    #   partition_reversed = []
    #   for row in reversed(skew_shape.rows()):
    #       current_row_len = max(current_row_len, rightmost(row))
    #       partition_reversed.append(current_row_len)
    #   partition = list(reversed(partition_reversed))
    #   return partition

def row_col_to_skew_partition(rs, cs):
    outer = []
    inner = []
    current_cs = [0] * len(cs)
    row_index = 0
    for col_coindex, col_length in enumerate(list(reversed(cs))):
        current_col_length = list(reversed(current_cs))[col_coindex]
        num_rows_to_slide = col_length - current_col_length
        if num_rows_to_slide < 0:
            raise ValueError('The inputted (row-shape, col-shape) pair has no possible corresponding skew-shape.')
        # 'col_num' is 1-based index of cols
        col_num = len(cs) - col_coindex
        while num_rows_to_slide > 0:
            if row_index > len(rs) - 1:
                raise ValueError('error more')
            # slide a row
            outer.append(col_num)
            inner.append(col_num - rs[row_index])
            # update params/info
            for c in range(col_num - rs[row_index], col_num):
                current_cs[c] += 1
            row_index += 1
            num_rows_to_slide -= 1
    return SkewPartition([outer, inner])


class kBoundary (SkewPartition2, CachedRepresentation):
    """
    Given a partition l and a positive integer k, the __k-boundary__ of l is the skew-shape obtained from the shape of l by removing all cells of hook-length greater than k.
    """
    @staticmethod
    def __classcall_private__(cls, l, k):
        """ Normalize input to ensure unique representation. """
        l = Partition2(l)
        k = NN(k)
        # this BELOW should fail because SkewPartition(l, k) would fail.
        return super(kBoundary, cls).__classcall__(cls, l, k)

    def __init__(self, l, k):
        # NOTE: THIS FUNCTION IS REDUNDANT WITH Permutation.k_boundary AND THIS SHOULD BE ADDRESSED
        """
        l: the partition
        k: the largest allowed hook length
        """
        # to make a SkewPartition, we must calculate the inner and outer partitions
        outer_partition = l.to_list()
        # we could make more efficient, but it's simple to get the tableau of all hook lengths and pick out the inner partition from it
        inner_partition = []
        for row_hook_lengths in l.hook_lengths():
            inner_row_length = len([x for x in row_hook_lengths if x > k])
            inner_partition.append(inner_row_length)
        # finally, make the SkewPartition
        SkewPartition2.__init__(self, [outer_partition, inner_partition])

    def partition(self):
        """ Return the partition whose k-boundary is self. """
        return k_boundary_to_partition(self, strict=False)

    # def __eq__(self):



"""
Given a skew-linked diagram, is it a k-boundary?  (That is, does there exist some partition which - when cells of hook-length > k are removed - becomes the skew-linked diagram.)
"""

def k_boundary_to_partition(skew_shape, strict=True):
    """
    skew_shape: The skew-shape (a k-boundary) to find the corresponding partition for.
    strict: If true, assert that the skew-shape really is a k-boundary.
    """
    if strict:
        assert is_k_boundary(skew_shape)
    # return minimal_containing_partition()
    return skew_shape.outer()

def is_k_boundary(skew_shape, k):
    if k == 0:
        # the only valid 0-boundary is the empty shape
        return skew_shape.outer() == skew_shape.inner()
    else:
        """We go down and left of each cell to create the only possible partition that could have led to this potential k-boundary

        (Any other partition containing this skew_shape would necessarily have a northeast corner that the skew_shape does *not have*.  But in order for the skew-shape to be a k-boundary, it *must have* that northeast corner.)
        """
        l = k_boundary_to_partition(skew_shape, strict=False)
        """now that we have the partition, we simply compute it's hook-length for each cell and verify that for each cell of values k or less, it appears in the skew_shape"""
        correct_k_boundary = l.k_boundary(k)
        return skew_shape == correct_k_boundary


class Partition2 (Partition):
    def is_k_irreducible(self, k):
        """
        See if the partition is `k`-irreducible for the provided natural number `k`.

        TESTS:

            # sage: p = Partition2([])
            # sage: p.is_k_irreducible(0)
            # False

            # # 3-rectangles are NOT 3-irreducible
            # sage: p = Partition2([1, 1, 1])
            # sage: p.is_k_irreducible(3)
            # False
            # sage: p = Partition2([2, 2])
            # sage: p.is_k_irreducible(3)
            # False
            # sage: p = Partition2([3])
            # sage: p.is_k_irreducible(3)
            # False


        """
        # k must be a natural number
        k = NN(k)
        if k == 0:
            # do anything speciall???
            # return is_empty(l) ?
            # TODO: edit this
            return True
        # if there's more than k-i rows of length i, it fails the condition
        l_reversed = list(reversed(l))
        i = 1
        num_rows_of_len_i = 0
        index = 0
        while True:
            if index == len(l_reversed) or l_reversed[index] > i:
                # check for failure, move on to next i
                if num_rows_of_len_i > k-i:
                    return False
                i += 1
                num_rows_of_len_i = 0
            else:
                # add to the count, keep going
                assert l_reversed[index] == i # sanity check
                num_rows_of_len_i += 1
                index += 1
        return True


class kIrreduciblePartition (Partition2, CachedRepresentation):
    """
    Definition: A partition is __k-irreducible__ if its shape has at most k-i rows of length i for all 1 \leq i < k, and no rows of length \geq k.
    """
    def _validate(self, l, k):
        assert l.is_k_irreducible(k)

    @staticmethod
    def __classcall_private__(cls, l, k):
        """ Normalize input to ensure a unique representation. """
        l = Partition2(l)
        k = NN(k)
        # I DONT THINK WE ALLOW k=0.  NOT SURE.  I THINK THE DEFINITION IS WRONG.
        return super(kIrreduciblePartition, cls).__classcall__(cls, l, k)

    # def __init__(self, l, k):


def get_k_irreducible_partition_lists(k):
	"""matt
	Since there are n! such partitions, the big-O time can't be better than that.
	We could have a yeild in the function to be an iterator.
	"""
	k = NN(k)
	k_irr_ptns = [[]]
	# NO rows of length k
	for i in range(1, k):
		new_k_irr_ptns = []
		for ptn in k_irr_ptns:
			# at most i rows of length k-i where 1 <= i < k
			for num_rows in range(0, i+1):
				new_ptn = ptn + [k-i]*num_rows
				new_k_irr_ptns.append(new_ptn)
		k_irr_ptns = new_k_irr_ptns
	return k_irr_ptns

def n_to_number_of_linked_partition_self_pairs(n):
	""" Given a natural number n, count how many partitions l of size n have the property that (l, l) has a corresponding linked-skew-diagram. """
	ps = Partitions(n)
	count = 0
	for p in ps:
		try:
			row_col_to_skew_partition(p, p)
		except:
			pass
		else:
			count += 1
	return count

def skew_partition_to_selected_rows(sp):
	# actually this may ONLY WORK for catty-connected skew-partitions, because i'm not sure how we deal with 'missing' rows
	# arguably we should call it a linked_skew_partition
	def bump_path_piece(sp, start_row_index, blocked_rows):
		# this algo find the correct "L" piece of the path, where the bottom right cell is cell1, the bottom left is cell2, and the top left is cell3
		# Returns (top_row_index, is_end) which are the row index of cell3 and whether or not we 'broke free' out of the top left cell of the skew-partition, respectively.
		cell2 = left(start_row_index)
		col_index2 = cell2[1]
		cell_under3 = top(col_index2)
		row_index3 = cell_under3[0]
		while row_index3 in blocked_rows:
			row_index3 += 1
		# CATTY-CORNER ONLY line:
		max_row_index = len(sp.outer()) - 1
		if row_index3 > max_row_index:
			return None, True
		else:
			return row_index3, False
	def bump_path(sp, row_index, blocked_rows):
		new_blocked_rows = {row_index}
		# is_end says if you reached the end of the path
		while True:
			row_index, is_end = bump_path_piece(sp, row_index, blocked_rows)
			if is_end:
				break
			else:
				new_blocked_rows.add(row_index)
		return new_blocked_rows
	# record the indices of rows that have been used up
	blocked_rows = set()
	for row_index, outer_row in enumerate(sp.outer()):
		new_blocked_rows = bump_path(sp, row_index, blocked_rows)
		blocked_rows += new_blocked_rows
	# CATTY-CORNER ONLY line:
	all_rows = set(range(0, len(sp.outer())))
	selected_rows = sorted(all_rows - blocked_rows)
	return selected_rows

def selected_rows_to_root_ideal(n, selected_rows):
	"""matt
	Given the dimension of the square n and the selected rows, output the root ideal """
	pass

def is_symmetric(l):
	"""matt
	Given a partition l, detect if l = l'.

	This function runs in LINEAR time of order length(l).
	"""
	for j in range(0, len(l)):
		for k in range(l[-j], l[-j-1]):
			if l[k] != len(l) - j:
				return False
	return True





