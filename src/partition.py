# -*- coding: utf-8 -*-
from sage.all import *

# HELPERS
def k_rectangle_dimension_list(k):
    return [(k-i+1, i) for i in range(1, k+1)]


# Partition stuff
def boundary(ptn):
    """ The boundary of a partition is the set { NE(d) | for all d diagonal }.  That is, for every diagonal, we find the northeasternmost (NE) point on that diagonal which is also in the ferrer's diagram.  Finally, we restrict to only integer coordinates.

    The boundary will go from bottom-right to top-left in the French notation.
    """
    def horizontal_piece((start_x, start_y), bdy):
        if not bdy:
            h_piece = [(start_x, start_y)]
        else:
            stop_x = bdy[-1][0]
            y = start_y # y never changes
            h_piece = [(x, y) for x in range(start_x, stop_x)]
        h_piece = list(reversed(h_piece))
        return h_piece
    bdy = []
    for i, part in enumerate(ptn):
        (cell_x, cell_y) = (part - 1, i)
        (x, y) = (cell_x + 1, cell_y + 1)
        bdy += horizontal_piece((x, y - 1), bdy)
        bdy.append((x, y))
    # add final "top-left" horizontal piece
    (top_left_x, top_left_y) = (0, len(ptn))
    bdy += horizontal_piece((top_left_x, top_left_y), bdy)
    # claim victory
    return bdy

def k_rim(ptn, k):
    """ The k-rim of a partition is the "line between" (or "intersection of") the k-boundary and the k-interior.

    It will be outputted as an ordered list of integer coordinates, where the origin is (0,0).  It will start at the top-left of the k-rim (under French depiction) and end at the bottom-right. """
    interior_rim = boundary(ptn.k_interior(k))
    # get leftmost vertical line
    interior_top_left_y = interior_rim[-1][1]
    v_piece = [(0, y) for y in range(interior_top_left_y + 1, len(ptn) + 1)]
    # get bottommost horizontal line
    interior_bottom_right_x = interior_rim[0][0]
    if ptn:
        ptn_bottom_right_x = ptn[0]
    else:
        ptn_bottom_right_x = 0
    h_piece = [(x, 0) for x in range(ptn_bottom_right_x, interior_bottom_right_x, -1)]
    # glue together with boundary
    rim = h_piece + interior_rim + v_piece
    return rim

def k_row_lengths(ptn, k):
    return ptn.k_boundary(k).row_lengths()

def k_column_lengths(ptn, k):
    return ptn.k_boundary(k).column_lengths()

def has_rectangle(ptn, h, w):
    """ A partition has an `h` x `w` rectangle if it's Ferrer's diagram has `h` (*or more*) rows of length `w` (*exactly*).
    """
    assert h >= 1
    assert w >= 1
    num_rows_of_len_w = 0
    for part in ptn:
        if part == w:
            num_rows_of_len_w += 1
    return num_rows_of_len_w >= h

def has_k_rectangle(ptn, k):
    """ A partition has a k-rectangle if it's Ferrer's diagram contains k-i+1 rows (or more) of length i (exactly) for any i in [1, k].
    """
    return any(has_rectangle(ptn, a, b) for (a, b) in k_rectangle_dimension_list(k))

def is_k_bounded(ptn, k):
    """ Returns True iff the partition is bounded by k. """
    if ptn.is_empty():
        least_upper_bound = 0
    else:
        least_upper_bound = max(ptn)
    return least_upper_bound <= k

def is_k_reducible(ptn, k):
    """ A k-bounded partition is __k-reducible__ if it has a k-rectangle. """
    # We only talk about k-reducible / k-irreducible for k-bounded partitions.
    assert is_k_bounded(ptn, k)
    return has_k_rectangle(ptn, k)

def is_k_irreducible(ptn, k):
    return not is_k_reducible(ptn, k)

def is_symmetric(ptn):
    """Given a partition λ, detect if λ = λ'.

    This function runs in LINEAR time of order length(λ).
    """
    for j in range(0, len(ptn)):
        for k in range(ptn[-j], ptn[-j-1]):
            if ptn[k] != len(ptn) - j:
                return False
    return True

def next(p, min=[], max=None, type=None):
    """
    Get the next partition lexigraphically that contains min and is contained in max.
    ptn: The Partition.
    min: The 'minimum partition' that next_advanced(ptn) must contain.
    max: The 'maximum partition' that next_advanced(ptn) must be contained in.
    type: The type of partitions allowed.  For example, 'strictly decreasing'.
    """
    # make sure min <= p <= max
    if max is not None:
        assert Partition(max).contains(Partition(p))
    assert Partition(p).contains(Partition(min))
    # check for empty max
    if max is not None and Partition(max).is_empty():
        return None
    # convert partitions to lists to make them mutable
    p = list(p)
    min = list(min)
    # if there is no max, the next partition just tacks a '1' on to the end!
    if max is None:
        return Partition(p + [1])
    # extend p and min to include 0's at the end
    p = p + [0] * (len(max) - len(p))
    min = min + [0] * (len(max) - len(min))
    # finally, run the algo to find next_p
    next_p = copy(p)
    def condition(a, b):
        if type == 'strictly decreasing':
            return a < b - 1
        elif type is None:
            return a < b
        else:
            raise ValueError('Unrecognized partition type.')
    for r in range(len(p) - 1, -1, -1):
        if r == 0:
            if (max is None or p[r] < max[r]):
                next_p[r] += 1
                break
            else:
                return None
        else:
            if (max is None or p[r] < max[r]) and condition(p[r], p[r-1]):
                next_p[r] += 1
                break
            else:
                next_p[r] = min[r]
                continue
    return Partition(next_p)