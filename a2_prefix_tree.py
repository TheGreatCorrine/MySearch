"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2023 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the definition of an Abstract Data Type (Autocompleter) and two
implementations of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any
from python_ta.contracts import check_contracts


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: list) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this autocompleter
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
        - weight > 0
        - the given value is either:
            1) not in this Autocompleter, or
            2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: list,
                     limit: int | None = None) -> list[tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        sorted by non-increasing weight. You can decide how to break ties.

        If limit is None, return *every* match for the given prefix.

        Preconditions:
        - limit is None or limit > 0
        """
        raise NotImplementedError

    def remove(self, prefix: list) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
@check_contracts
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    Instance Attributes:
    - root:
        The root of this prefix tree.
        - If this tree is empty, <root> equals [].
        - If this tree is a leaf, <root> represents a value stored in the Autocompleter
          (e.g., 'cat').
        - If this tree is not a leaf and non-empty, <root> is a list representing a prefix
          (e.g., ['c', 'a']).
    - subtrees:
        A list of subtrees of this prefix tree.
    - weight:
        The weight of this prefix tree.
        - If this tree is empty, this equals 0.0.
        - If this tree is a leaf, this stores the weight of the value stored in the leaf.
        - If this tree is not a leaf and non-empty, this stores the *total weight* of
          the leaf weights in this tree.

    Representation invariants:
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0.0, then self.root == [] and self.subtrees == [].
        This represents an empty prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, then this tree is a leaf.
        (self.root is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If self.subtrees != [], then self.root is a list (representing a prefix),
        and self.weight is equal to the sum of the weights of all leaves in self.

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of weight.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a weight
      attribute.
    """
    root: Any
    weight: float
    subtrees: list[SimplePrefixTree]

    ###########################################################################
    # Part 1(a)
    ###########################################################################
    def __init__(self) -> None:
        """Initialize an empty simple prefix tree.
        """
        self.root = []
        self.weight = 0.0
        self.subtrees = []

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return (self.root == [] and self.weight == 0.0
                and self.subtrees == [])

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.subtrees == [] and self.weight > 0

    def __len__(self) -> int:
        """Return the number of LEAF values stored in this prefix tree.

        Note that this is a different definition than how we calculate __len__
        of regular trees from lecture!
        """
        # essence: number of words stored or inserted in the Tree

        if self.is_leaf():  # Actual operator of the recursion
            return 1
        else:
            # Accumulate the number of leaf values in each subtree
            return sum(len(subtree) for subtree in self.subtrees)

    ###########################################################################
    # Extra helper methods
    ###########################################################################
    def __str__(self) -> str:
        """Return a string representation of this prefix tree.

        You may find this method helpful for debugging. You should not change this method
        (nor the helper _str_indented).
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this prefix tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.root} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    ###########################################################################
    # Add code for Parts 1(c), 2, and 3 here
    ###########################################################################
    def insert(self, value: Any, weight: float, prefix: list) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this autocompleter
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
        - weight > 0
        - the given value is either:
            1) not in this Autocompleter, or
            2) was previously inserted with the SAME prefix sequence
        """
        # Base case: we have reached the insertion point
        if not prefix:  # prefix == [], self is the last internal node, ['c', 'a', 't']
            self._create_leaf(value, weight)
            self.weight += weight

        # Recursive case: Keep going until prefix becomes empty
        elif prefix:  # prefix != []
            next_tree = None
            for subtree in self.subtrees:
                # Find ['c','a'] == ['c','a','t'][0:len(pre.root)]
                if subtree.root[-1] == prefix[0]:
                    next_tree = subtree
                    break
            if next_tree is None:  # Fail to find ['c']
                # create one and append that to the subtree
                next_tree = SimplePrefixTree()
                next_tree.root = self.root + [prefix[0]]
                self.subtrees.append(next_tree)
                self.subtrees.sort(key=lambda t: t.weight, reverse=True)

            next_tree.insert(value, weight, prefix[1:])

            self.subtrees.sort(key=lambda t: t.weight, reverse=True)

        # update weights
        self._update_weight()

    def _update_weight(self) -> None:
        """Update the weight of this tree based on the weights of its subtrees."""
        if self.is_leaf():
            return None
        else:
            self.weight = sum(subtree.weight for subtree in self.subtrees)
            return None

    def _create_leaf(self, value: Any, weight: float) -> None:
        """Create a new leaf"""
        # check all leaves
        check_leaf = None
        for subtree in self.subtrees:  # self is the last internal node
            # this leaf already exists
            if subtree.is_leaf() and subtree.root == value:
                check_leaf = subtree
                subtree.weight += weight  # do nothing, just update weights
        if check_leaf is None:  # after checking all leaves, find the leaf non-exist
            leaf = SimplePrefixTree()
            leaf.root = value
            leaf.weight = weight
            self.subtrees.append(leaf)
        self.subtrees.sort(key=lambda t: t.weight, reverse=True)

    ###########################################################################
    # Part 2: autocompletion
    ###########################################################################
    def autocomplete(self, prefix: list,
                     limit: int | None = None) -> list[tuple[Any, float]]:
        results = []
        if self._look_up_prefix(prefix) is False:
            return []

        self._look_up_prefix(prefix)._autocomplete_helper(results)

        return sorted(results[:limit if limit is not None else None],
                      key=lambda x: x[1], reverse=True)

    def _look_up_prefix(self, prefix: list) -> SimplePrefixTree | bool:
        """This helper function helps find the SimplePrefixTree
        whose root is the same as the prefix.
        If the tree is not found, it should return False
        else it should reach the SimplePrefixTree"""
        # Base case: we have reached the point
        if self.root == prefix:
            return self

        # Recursive case: prefix is still longer than the root
        for subtree in self.subtrees:
            if len(subtree.root) <= len(prefix) and subtree.root == prefix[:len(subtree.root)]:
                result = subtree._look_up_prefix(prefix)
                if result:
                    return result

        return False

    def _autocomplete_helper(self, results: list) -> None:
        """This helper function will go on recurse the targeted SimplePrefixTree
        to find the leaf and append the leaves to the output"""
        if self.is_leaf():
            results.append((self.root, self.weight))
        else:  # if not self.is_leaf(), the recursion will go on
            for subtree in self.subtrees:
                subtree._autocomplete_helper(results)

    ###########################################################################
    # Part 3: remove
    ###########################################################################
    def remove(self, prefix: list) -> None:
        """Remove all values that match the given prefix.
        Be careful about preserving all representation invariants
        (e.g., updating weights, making sure there aren’t any empty subtrees)
        """
        if self.is_empty() or self.is_leaf():
            return

        elif not prefix:
            self.root, self.weight, self.subtrees = [], 0.0, []

        elif not self.subtrees:
            self.root, self.weight, self.subtrees = [], 0.0, []

        for subtree in self.subtrees:
            if subtree.root == prefix[:len(subtree.root)]:
                # If the full prefix matches, remove the subtree
                if len(subtree.root) == len(prefix):
                    subtree.root, subtree.subtrees = None, []
                    self.weight -= subtree.weight
                    self.subtrees.remove(subtree)
                else:
                    # Recursively call remove on the subtree
                    subtree.remove(prefix)
                    if not subtree.subtrees:  # If subtree.subtrees == [], remove it
                        self.subtrees.remove(subtree)
                break

        self._check_removable()

        # update weights
        self._update_weight()

    def _check_removable(self) -> None:
        """This helper function recurse through the whole SimplePrefixTree to see
        if any node should be removed. If it's removable, just remove it.
        Otherwise, do nothing.

        The removable node should have an empty subtree"""
        # Base case: this node is removable
        if self.is_leaf() or self.is_empty():
            return

        # Recursive case: this node has a non-empty subtree
        else:
            for subtree in self.subtrees:
                if not subtree.subtrees:  # subtree.subtrees = []
                    if len(subtree.subtrees) == 1 and subtree.subtrees[0].is_leaf():
                        self.subtrees.remove(subtree)
                        subtree.root, subtree.weight = None, 0.0

                subtree._check_removable()


################################################################################
# CompressedPrefixTree (Part 6)
################################################################################
@check_contracts
class CompressedPrefixTree(SimplePrefixTree):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the definitions
    described in Part 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    Representation Invariants:
    - (NEW) This tree does not contain any compressible internal values.
    """
    subtrees: list[CompressedPrefixTree]  # Note the different type annotation

    ###########################################################################
    # Add code for Part 6 here
    ###########################################################################
    def _create_empty(self, value: Any, weight: float, prefix: list) -> None:
        """When self is empty, create a CompressedPrefixTree like this:
        [prefix] -> value
        """
        leaf = CompressedPrefixTree()
        leaf.root, leaf.weight = value, weight
        self.root, self.weight = prefix, weight
        self.subtrees = [leaf]

    def _create_leaf(self, value: Any, weight: float) -> None:
        """When self.root == prefix, create a new leaf or just update the weight"""
        # check all leaves
        check_leaf = None
        for subtree in self.subtrees:  # subtree = 'cat', self = ['c','a','t']
            # this leaf already exists
            if subtree.is_leaf() and subtree.root == value:
                subtree.weight += weight  # do nothing, just update weights
                check_leaf = subtree
                break
        if check_leaf is None:  # after checking all leaves, find the leaf non-exist
            leaf = CompressedPrefixTree()
            leaf.root, leaf.weight = value, weight
            self.subtrees.append(leaf)
        self.subtrees.sort(key=lambda t: t.weight, reverse=True)
        self.weight += weight

    def _create_new_tree(self, value: Any, weight: float, prefix: list) -> None:
        """This helper function creates a new CompressedPrefixTree
        and append that tree to self"""
        leaf = CompressedPrefixTree()
        leaf.root, leaf.weight = value, weight
        sub = CompressedPrefixTree()
        sub.root, sub.weight = prefix, weight
        sub.subtrees = [leaf]
        self.subtrees.append(sub)
        self.subtrees.sort(key=lambda t: t.weight, reverse=True)

    def _create_parent_tree(self, value: Any, weight: float, prefix: list) -> None:
        """This helper function creates a new CompressedPrefixTree
        and self to the subtrees of that tree, or maybe merge"""
        # create a copy of self
        child = self.copy()
        # create a parent tree
        leaf = CompressedPrefixTree()
        leaf.root, leaf.weight = value, weight
        parent = CompressedPrefixTree()
        parent.root, parent.weight = prefix, weight
        parent.subtrees = [leaf]
        parent.subtrees.append(child)
        parent.subtrees.sort(key=lambda t: t.weight, reverse=True)

        self.root, self.subtrees = parent.root, parent.subtrees
        self._update_weight()

    def _create_common_prefix_tree(self, overlapping: list, prefix: list,
                                   value: Any, weight: float) -> None:
        """This should create a new tree with a common prefix tree,
        and merge the two trees together
        """
        # create a copy of self
        right = self.copy()
        # create a tree using prefix
        leaf = CompressedPrefixTree()
        leaf.root, leaf.weight = value, weight
        left = CompressedPrefixTree()
        left.root, left.weight = prefix, weight
        left.subtrees = [leaf]
        # create a tree with common prefix
        common = CompressedPrefixTree()
        common.root = overlapping
        common.subtrees.append(right)
        common.subtrees.append(left)
        common.subtrees.sort(key=lambda t: t.weight, reverse=True)

        self.root, self.subtrees = common.root, common.subtrees
        self._update_weight()

    def copy(self) -> CompressedPrefixTree:
        """Returns an identical copy of """
        new_tree = CompressedPrefixTree()
        new_tree.root, new_tree.weight = self.root, self.weight

        new_tree.subtrees = [subtree.copy() for subtree in self.subtrees]

        return new_tree

    def _overlapping_list(self, prefix: list) -> list:
        """This should return a list
        If the two lists don't having overlapping part, return []
        else, return the overlapping part
        """
        overlapping = []
        for i in range(min(len(self.root), len(prefix))):
            if self.root[i] != prefix[i]:
                return overlapping
            overlapping.append(self.root[i])
        return overlapping

    def insert(self, value: Any, weight: float, prefix: list) -> None:

        # case 0: self.is_empty
        if self.is_empty():
            self._create_empty(value, weight, prefix)
            return

        # case 1: ['c','a','t'] == ['c','a','t']
        if self.root == prefix:
            self._create_leaf(value, weight)  # create cat or just update weight
            return

        # one completely overlap another
        # case 2: self.root = ['c','a'], prefix = ['c','a','t']
        elif isinstance(self.root, list) and \
                len(self.root) < len(prefix) and self.root == prefix[:len(self.root)]:
            max_length = 0
            best_subtree = None
            for subtree in self.subtrees:
                overlap_list = subtree._overlapping_list(prefix)
                # if not subtree.is_leaf() and subtree.root == overlap_list:
                if not subtree.is_leaf() and len(overlap_list) > len(self.root):
                    if max_length < len(overlap_list):
                        max_length = len(overlap_list)
                        best_subtree = subtree

            # if the best_subtree is found, go on inserting value into the tree
            if best_subtree:
                best_subtree.insert(value, weight, prefix)  # just recurse into one subtree
                self.subtrees.sort(key=lambda t: t.weight, reverse=True)
                self._update_weight()
                return

            # create one and append that to self
            self._create_new_tree(value, weight, prefix)
            self._update_weight()

        # one completely overlap another
        # case 3: self.root = ['c','a','t','h'], prefix = ['c','a','t']
        elif isinstance(self.root, list) and \
                len(self.root) > len(prefix) and self.root[:len(prefix)] == prefix:
            self._create_parent_tree(value, weight, prefix)

        # case 4: self.root = ['c','a','r'], prefix = ['c','a','t']
        else:
            overlap = []
            for subtree in self.subtrees:
                overlap = subtree._overlapping_list(prefix)
            self._create_common_prefix_tree(overlap, prefix, value, weight)

    #############################################################################
    # Below is Part 6: autocomplete
    #############################################################################

    def autocomplete(self, prefix: list, limit: int | None = None) -> list[tuple[Any, float]]:
        """
        Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be sorted by
        non-increasing weight. You can decide how to break ties.

        If limit is None, return every match for the given prefix.

        Preconditions:
        - limit is None or limit > 0
        """
        results = []
        if self._look_up_prefix(prefix) is False:
            return []

        self._look_up_prefix(prefix)._autocomplete_helper(results)

        # Sort and limit the results if necessary
        return sorted(results[:limit if limit is not None else None],
                      key=lambda x: x[1], reverse=True)

    def _look_up_prefix(self, prefix: list) -> SimplePrefixTree | bool:
        """This helper function helps find the right tree.
        If the right tree does not exist, return False"""
        # case 0: self.is_empty
        if self.is_empty():
            return False

        # case 1: ['c','a','t'] == ['c','a','t']
        elif self.root == prefix:
            return self

        # case 2: self.root = ['c','a'], prefix = ['c','a','t']
        elif len(self.root) < len(prefix) and self.root == prefix[:len(self.root)]:
            for subtree in self.subtrees:
                # ['c','a','t'] or ['c','a','t','h']
                if not subtree.is_leaf() and prefix == subtree.root[:len(prefix)]:
                    return subtree

                # ['c','a'] or ['c']
                elif not subtree.is_leaf() and prefix[:len(subtree.root)] == subtree.root:
                    return subtree._look_up_prefix(prefix)

            # ['c','a','t'] does not exist
            return False

        # case 3: self.root = ['c','a','t','h'], prefix = ['c','a','t']
        elif len(self.root) > len(prefix) and self.root[:len(prefix)] == prefix:
            return self

        return False


if __name__ == '__main__':
    import doctest

    doctest.testmod()

    # Uncomment the python_ta lines below and run this module.
    # This is different that just running doctests! To run this file in PyCharm,
    # right-click in the file and select "Run a2_prefix_tree" or
    # "Run File in Python Console".
    #
    # python_ta will check your work and open up your web browser to display
    # its report. For full marks, you must fix all issues reported, so that
    # you see "None!" under both "Code Errors" and "Style and Convention Errors".
    # TIP: To quickly uncomment lines in PyCharm, select the lines below and press
    # "Ctrl + /" or "⌘ + /".
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 100,
        'max-nested-blocks': 4
    })
