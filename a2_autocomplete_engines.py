"""CSC148 Assignment 2: Autocomplete engines

=== CSC148 Fall 2023 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This file contains starter code for the three different autocomplete engines
you are writing for this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
import csv
import time
from typing import Any
from python_ta.contracts import check_contracts

from a2_melody import Melody
from a2_prefix_tree import Autocompleter, SimplePrefixTree, CompressedPrefixTree


################################################################################
# Text-based Autocomplete Engines (Task 4)
################################################################################
@check_contracts
class LetterAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few letters.

    The *prefix sequence* for a string is the list of characters in the string.
    This can include space characters.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters; see the section on
    "Text sanitization" on the assignment handout.

    Instance Attributes:
    - autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
        - 'file': the path to a text file
        - 'autocompleter': either the string 'simple' or 'compressed',
          specifying which subclass of Autocompleter to use.

        Each line of the specified file counts as one input string.
        Note that the line may or may not contain spaces.
        Each string must be sanitized, and if the resulting string contains
        at least one non-space character, it is inserted into the
        Autocompleter.

        SKIP sanitized strings that do not contain at least one non-space character!

        When each string is inserted, it is given a weight of 1.0. It is possible
        for the same string to appear on more than one line of the input file;
        this results in that string receiving a larger weight (because of how
        Autocompleter.insert works).

        Preconditions:
        - config['file'] is a valid path to a file as described above
        - config['autocompleter'] in ['simple', 'compressed']
        """
        self.autocompleter = SimplePrefixTree() if config['autocompleter'] == 'simple' \
            else CompressedPrefixTree()
        # We've opened the file for you here. You should iterate over the
        # lines of the file and process them according to the description in
        # this method's docstring.
        with open(config['file'], encoding='utf8') as f:  # File: sample_words.txt
            for line in f:
                sanitized_line = text_sanitization(line)
                if sanitized_line.strip():
                    self.autocompleter.insert(sanitized_line, 1.0, list(line))

    def autocomplete(self, prefix: str, limit: int | None = None) -> list[tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        sorted by non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of characters before being passed to the Autocompleter.

        Preconditions:
        - limit is None or limit > 0
        - <prefix> is a sanitized string
        """
        return self.autocompleter.autocomplete(list(prefix), limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix string.

        Note that the given prefix string must be transformed into a list
        of characters before being passed to the Autocompleter.

        Preconditions:
        - <prefix> is a sanitized string
        """
        self.autocompleter.remove(list(prefix))


@check_contracts
class SentenceAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few words.

    A *word* is a string containing only alphanumeric characters.
    The *prefix sequence* for a string is the list of words in the string
    (separated by whitespace). The words themselves do not contain spaces.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters; see the section on
    "Text sanitization" on the assignment handout.

    Instance Attributes:
    - autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
        - 'file': the path to a CSV file
        - 'autocompleter': either the string 'simple' or 'compressed',
          specifying which subclass of Autocompleter to use.

        Preconditions:
        - config['file'] is the path to a *CSV file* where each line has two entries:
            - the first entry is a string, which is the value to store in the Autocompleter
            - the second entry is a positive float representing the weight of that
              string
        - config['autocompleter'] in ['simple', 'compressed']

        Note that the line may or may not contain spaces.
        Each string must be sanitized, and if the resulting string contains
        at least one word, it is inserted into the Autocompleter.

        SKIP sanitized strings that do not contain at least one non-space character!

        Note that it is possible for the same string to appear on more than
        one line of the input file; this results in that string receiving
        the sum of the specified weights from each line.
        """
        # We haven't given you any starter code here! You should review how
        # you processed CSV files on Assignment 1.

        self.autocompleter = SimplePrefixTree() if config['autocompleter'] == 'simple' \
            else CompressedPrefixTree()

        with open(config['file'], encoding='utf8') as csvfile:
            reader = csv.reader(csvfile)
            for lines in reader:
                sentence, weight = lines[0].strip(), float(lines[1].strip())
                sanitized_sentence = text_sanitization(sentence)
                words = sanitized_sentence.split()
                if words:
                    self.autocompleter.insert(sanitized_sentence, weight, words)

    def autocomplete(self, prefix: str, limit: int | None = None) -> list[tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        sorted by non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Preconditions:
        - limit is None or limit > 0
        - <prefix> is a sanitized string
        """
        return self.autocompleter.autocomplete(prefix.split(), limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Preconditions:
        - <prefix> is a sanitized string
        """
        self.autocompleter.remove(prefix.split())


################################################################################
# Helper functions for sanitization (Task 4)
################################################################################
def text_sanitization(line: str) -> str:
    """This helper function helps sanitize the text.
    This function:
    (1)Convert all letters to lowercase.
    (2)Remove any characters that are not alphanumeric and not space (' ') characters.
    In other words, keep only alphanumeric and space characters.
    Remove other forms of whitespace, such as the newline character '\n'.
    """
    result = ''
    for word in line:
        if word.isalnum():
            result += word.lower()
        elif word == ' ':
            result += word
    return result


def calculate_intervals(notes: list[tuple[int, int]]) -> list[int]:
    """Calculate the interval sequence from a list of notes."""
    intervals = []
    for i in range(1, len(notes)):
        interval = notes[i][0] - notes[i - 1][0]
        intervals.append(interval)
    return intervals


################################################################################
# Melody-based Autocomplete Engines (Task 5)
################################################################################
@check_contracts
class MelodyAutocompleteEngine:
    """An autocomplete engine that suggests melodies based on a few intervals.

    The values stored are Melody objects, and the corresponding
    prefix sequence for a Melody is its interval sequence.

    Because the prefix is based only on interval sequence and not the
    starting pitch or duration of the notes, it is possible for different
    melodies to have the same prefix.

    Instance Attributes:
    - autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
        - 'file': the path to a CSV file
        - 'autocompleter': either the string 'simple' or 'compressed',
          specifying which subclass of Autocompleter to use.

        Preconditions:
        - config['file'] is the path to a *CSV file* where each line has the following format:
            - The first entry is the name of a melody (a string).
            - The remaining entries are grouped into pairs of integers (as in Assignment 1)
              where the first number in each pair is a note pitch,
              and the second number is the corresponding duration.
        - config['autocompleter'] in ['simple', 'compressed']

        HOWEVER, there may be blank entries (stored as an empty string '').
        As soon as you encounter a blank entry, stop processing this line
        and move onto the next line the CSV file.

        Each melody is inserted into the Autocompleter with a weight of 1.0.
        """
        # We haven't given you any starter code here! You should review how
        # you processed CSV files on Assignment 1.
        self.autocompleter = SimplePrefixTree() if config['autocompleter'] == 'simple' \
            else CompressedPrefixTree()

        with open(config['file'], newline='', encoding='utf8') as csvfile:
            for line in csvfile:
                line = line.strip().split(',')
                melody_name = line[0]
                notes = []
                for i in range(1, len(line), 2):
                    if line[i] == '' or i + 1 >= len(line) or line[i + 1] == '':
                        break  # Stop if there is a blank entry or incomplete note
                    pitch, duration = int(line[i]), int(line[i + 1])
                    notes.append((pitch, duration))

                if notes:
                    melody = Melody(melody_name, notes)
                    interval_sequence = calculate_intervals(notes)
                    self.autocompleter.insert(melody, 1.0, interval_sequence)

    def autocomplete(
            self, prefix: list[int], limit: int | None = None
    ) -> list[tuple[Melody, float]]:
        """Return up to <limit> matches for the given interval sequence.

        The return value is a list of tuples (melody, weight), and must be
        sorted by non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given interval sequence.

        Preconditions:
        - limit is None or limit > 0
        """
        return self.autocompleter.autocomplete(prefix, limit)

    def remove(self, prefix: list[int]) -> None:
        """Remove all melodies that match the given interval sequence."""
        self.autocompleter.remove(prefix)


###############################################################################
# Sample runs
###############################################################################
def example_letter_autocomplete() -> list[tuple[str, float]]:
    """A sample run of the letter autocomplete engine.

    Notes:
    - You can open .txt files directly in PyCharm to see their contents.
    - You can try out the larger ".txt" datasets under data/texts. If you do so,
      we recommend TEMPORARILY commenting out the @check_contracts decorator for
      the SimpleTreePrefix/CompressedTreePrefix classes to help speed up the
      computation. Just make sure to uncomment the decorator before your final
      submission.
    - For lotr.txt, try the prefix 'frodo' or 'gandalf' 🧙
      Make sure to put in a limit!
    """
    engine = LetterAutocompleteEngine(
        {
            'file': 'data/texts/sample_words.txt',
            'autocompleter': 'simple',
        }
    )
    return engine.autocomplete('ca', 2)


def example_sentence_autocomplete() -> list[tuple[str, float]]:
    """A sample run of the sentence autocomplete engine.

    Same notes as example_letter_autocomplete above, except you should use
    the .csv files under data/texts (not the .txt files).
    If using google_searches.csv, try a prefix of 'how to'. Make sure to put in a limit.
    """
    engine = SentenceAutocompleteEngine(
        {
            'file': 'data/texts/sample_sentences.csv',
            'autocompleter': 'simple',
        }
    )
    return engine.autocomplete('a star')


def example_melody_autocomplete(play: bool = False) -> list[tuple[Melody, float]]:
    """A sample run of the melody autocomplete engine.

    If <play> is True, also play each melody using Pygame.

    Notes:
    - You may wish to comment out the @check_contracts decorator for the prefix tree classes
      and Melody for this example.
    - You can try the other datasets under data/melodies.
    - Remember, you can open csv files in PyCharm, too!
    """
    engine = MelodyAutocompleteEngine(
        {
            'file': 'data/melodies/songbook.csv',
            'autocompleter': 'simple'
        }
    )
    melodies = engine.autocomplete([0, 0], 3)

    if play:
        for melody, _ in melodies:
            melody.play()
            time.sleep(2)  # Wait 2 seconds after playing each melody

    return melodies


if __name__ == '__main__':
    # This is used to increase the recursion limit so that your autocomplete engines work
    # even for tall SimplePrefixTrees.
    import sys

    sys.setrecursionlimit(5000)

    # print(example_letter_autocomplete())
    # print(example_sentence_autocomplete())
    # print(example_melody_autocomplete(play=True))

    # Uncomment the python_ta lines below and run this module.
    # This is different that just running doctests! To run this file in PyCharm,
    # right-click in the file and select "Run a2_autocomplete_engines" or
    # "Run File in Python Console".
    #
    # python_ta will check your work and open up your web browser to display
    # its report. For full marks, you must fix all issues reported, so that
    # you see "None!" under both "Code Errors" and "Style and Convention Errors".
    # TIP: To quickly uncomment lines in PyCharm, select the lines below and press
    # "Ctrl + /" or "⌘ + /".
    # import python_ta
    # python_ta.check_all(
    #     config={
    #         'allowed-io': [
    #             'LetterAutocompleteEngine.__init__',
    #             'SentenceAutocompleteEngine.__init__',
    #             'MelodyAutocompleteEngine.__init__'
    #         ],
    #         'extra-imports': ['csv', 'time', 'sys', 'a2_prefix_tree', 'a2_melody'],
    #         'max-line-length': 100,
    #     }
    # )
