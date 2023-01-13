"""
Wordle
Assignment 1
Semester 1, 2022
CSSE1001/CSSE7030
"""
from __future__ import annotations

from a1_support import (
    load_words,
    choose_word,
    VOCAB_FILE,
    ANSWERS_FILE,
    CORRECT,
    MISPLACED,
    INCORRECT,
    UNSEEN,
)
from string import ascii_lowercase
from typing import Optional

WORD_LENGTH = 6
MAX_GUESSES = 6

GUESS_PROMPT = "Enter guess {}: "
PLAY_AGAIN_PROMPT = "Would you like to play again (y/n)? "
HISTORY_TEXT = "Guess {}: {}\n         {}\n---------------"
INVALID_LENGTH_MESSAGE = "Invalid! Guess must be of length {}"
UNKNOWN_WORD_MESSAGE = "Invalid! Unknown word"
WIN_MESSAGE = "Correct! You won in {} guesses!"
LOSS_MESSAGE = "You lose! The answer was: {}"
HELP_MESSAGE = "Ah, you need help? Unfortunate."
KEYBOARD_ROW = '{}: {}\t{}: {}'

HELP = "h"
KEYBOARD = "k"
QUIT = "q"
YES = "y"
SUGGESTION = "a"

# Keyboard constants
TOP_ROW = "qwertyuiop"
MIDDLE_ROW = " asdfghjk "
BOTTOM_ROW = " lzxcvbnm "
COLUMNS = len(TOP_ROW) + 2


def remove_word(words: tuple[str, ...], word: str) -> tuple[str, ...]:
    """Remove word from a tuple of words.

    Precondition: word is in words.

    Parameters:
        words: A tuple of words, containing word.
        word: The word to remove.

    Returns:
        A copy of words where the word is removed.
    """
    idx = words.index(word)
    return words[:idx] + words[idx + 1 :]


def prompt_user(guess_number: int, words: tuple[str, ...]) -> str:
    """Prompts the user for the next guess, reprompting until either a valid
    guess is entered, or a selection for help, keyboard, or quit is made.

    Parameters:
        guess_number: The number of the current guess
        words: All known words (whole vocab).

    Returns:
        The lowercase guess if a valid guess is made,
        otherwise the selection of either 'h', 'q', or 'k' to represent
        help, quit, or keyboard commands.
    """
    while True:
        guess = input(GUESS_PROMPT.format(guess_number)).lower()

        if guess in (HELP, KEYBOARD, QUIT, SUGGESTION):
            break
        elif len(guess) != WORD_LENGTH:
            print(INVALID_LENGTH_MESSAGE.format(WORD_LENGTH))
        elif guess not in words:
            print(UNKNOWN_WORD_MESSAGE)
        else:
            break

    return guess


def process_guess(guess: str, answer: str) -> str:
    """Determines which letters from guess are correctly placed in answer,
        which letters are incorrectly placed from answer, and which letters
        are not in answer.

    Precondition: len(guess) == 6 and len(answer) == 6

    Parameters:
        guess: The guess made by the player
        answer: The answer for this round

    Returns:
        A modified representation of guess, in which a '🟩' represents a
        correctly placed letter at that position, a '🟨' represents a
        letter at that position in guess that is in answer but not in said
        position, and a '⬛' represents a letter that is not in answer. If
        duplicate letters exist in guess, then the correctly placed letter
        will take precedence if one exists, otherwise the first letter will
        take precedence.
    """
    processed = ""

    for i, char in enumerate(guess):
        if char == answer[i]:
            processed += CORRECT
        elif (
            char in answer
            and char not in guess[:i]  # char是第一个出现的（怕有重复字母）
            and guess[answer.index(char)] != char  # guess的位置不是answer的字母在的位置
        ):
            # If char is correctly placed elsewhere it's counted as incorrect
            # here. Else if it's the 1st occurrence it's counted as misplaced
            processed += MISPLACED
        else:
            processed += INCORRECT

    return processed


def has_won(guess: str, answer: str) -> bool:
    """Returns True iff the round has been won by this guess.

    Preconditions:
        len(guess) == 6 and len(answer) == 6

    Parameters:
        guess: The guess.
        answer: The answer for the round.
    """
    return guess == answer


def has_lost(guess_number: int) -> bool:
    """Returns True iff the round has been lost.

    Parameters:
        guess_number: The number of guesses that have occured.
    """
    return guess_number >= MAX_GUESSES


def print_history(history: tuple[tuple[str, str], ...]) -> None:
    """Prints the guess history.

    Parameters:
        history: contains tuples of (guess, processed_guess)
                  for each turn so far.
    """
    print("-" * 15)  # I <3 magic numbers
    for i, guess_info in enumerate(history):
        guess, processed_guess = guess_info
        guess = ' ' + ' '.join(guess)
        print(HISTORY_TEXT.format(i + 1, guess, processed_guess))
    print()


def letter_status(letter: str, history: tuple[tuple[str, str], ...]) -> str:
    """Returns the 'status' of the given letter. That is, which of the four
        following things do the previous guesses tell us about the letter:
            1. Its correct location in answer
            2. Its presence in answer but not location
            3. Its absence from answer
            4. It has not yet been seen

    Parameters:
        letter: The letter of interest
        history: contains tuples of (guess, processed_guess)
                  for each turn so far.
    """
    status = UNSEEN
    for guess, processed in history:
        if letter in guess:
            this_status = processed[guess.index(letter)]  # 位置相同才能确定为correct，防止有重复字母
            if this_status == CORRECT or status != CORRECT:
                status = this_status
    return status


def print_keyboard(history: tuple[tuple[str, str], ...]) -> None:
    """Prints the keyboard with information currently known about each letter

    Parameters:
        history: contains tuples of (guess, processed_guess)
                  for each turn so far.
    """
    print("\nKeyboard information\n" + COLUMNS * "-")

    for i in range(0, 26, 2):
        first = ascii_lowercase[i]
        first_status = letter_status(first, history)
        second = ascii_lowercase[i + 1]
        second_status = letter_status(second, history)
        print(KEYBOARD_ROW.format(first, first_status, second, second_status))

    print()


def update_stats(stats: tuple[int, ...], guess_number: int) -> tuple[int, ...]:
    """Returns a new updated version of the players stats based on their
        result for the latest round.

    Precondition: 1 < guess_number <= len(stats)

    Parameters:
        stats: The number of games won in 1-6 moves respectively,
                and number of games lost.
        guess_number: The number of guesses it took to win the last
                       round. MAX_GUESSES + 1 if the player lost.

    Returns:
        The updated stats.
    """
    idx = guess_number - 1
    return stats[:idx] + (stats[idx] + 1,) + stats[idx + 1 :]


def update_history(
    history: tuple[tuple[str, str], ...], guess: str, answer: str
) -> tuple[tuple[str, str], ...]:
    """Returns a new updated version of the guess history.

    Parameters:
        history: contains tuples of (guess, processed_guess)
                  for each turn so far.
        guess: The guess made by the player.
        answer: The answer for the round.

    Returns:
        The updated history.
    """
    return history + ((guess, process_guess(guess, answer)),)


def print_stats(stats: tuple[int, ...]) -> None:
    """Prints the stats in a user-friendly way.

    Precondition: len(stats) == 7

    Parameters:
        stats: The current stats to display.
    """
    print("\nGames won in:")
    for i, stat in enumerate(stats[:-1]):  # 除了最后一个元素
        print(f"{i + 1} moves: {stat}")
    print("Games lost:", stats[-1])


def print_help() -> None:
    """Prints the help message."""
    print(HELP_MESSAGE)


## Begin CSSE7030 task ##
def remove_duplicated_letters(
    vocab: tuple[str, ...], history: tuple[tuple[str, str], ...]
) -> tuple[str, ...]:
    """ Removes words that have any non-unique letters, since we know these
        can't be in the solution.

    Parameters:
        vocab: The allowed guesses vocab.
        history: contains tuples of all previous (guess, processed_guess)

    Returns:
        A copy of the vocab with words containing duplicate letters removed.

    """
    for word in vocab:  # vocab里是有重复字母的，但是我们假定答案没有重复字母，所以要先剔除这些vocab
        for i, letter in enumerate(word):
            if letter in word[i+1:]:
                vocab = remove_word(vocab, word)
                break  # 跳出内循环，如果是我做可能会忘
    return vocab


def filter_words(
    vocab: tuple[str, ...], guess: str, position: int, status: str
) -> tuple[str, ...]:
    """ Filters words out of the vocbulary based on a single letter of a guess.

    Parameters:
        vocab: The allowed guesses vocab.
        guess: The guess we are analysing.
        position: The position of the letter we are analysing in guess
        status: The status of the position at the letter

    Returns:
        A copy of the vocab with words violating information about this letter
        removed.

    """
    letter = guess[position]
    for candidate in vocab:
        # Exclude words where a correct letter is not present in its spot
        # 相当于简化了一个if status == correct and candidate[position] != letter
        # false_positive = True <-用来判断删除这个词
        false_positive = (status == CORRECT and candidate[position] != letter)

        # Exclude words where an incorrect letter is present
        # 相当于if status == incorrect and letter in candidate
        # false_negative = True <-用来判断删除这个词
        false_negative = (status == INCORRECT and letter in candidate)

        if false_negative:
            # Handle duplicates where one is incorrectly placed
            # 如果有重复字母是正确的，那么要保留，因为我们在process_guess那一步将非correct位置的重复字母判断为incorrect
            for other_letter, other_status in zip(guess, status):
                if other_status == CORRECT and other_letter == letter:
                    false_negative = False  # <-用来判断不要删除这个词

        # Exclude words that have misplaced letters at their misplaced
        # positions or don't have the misplaced letters at all
        wrong_misplaced = (status == MISPLACED and \
            (letter not in candidate or candidate[position] == letter))

        if false_positive or false_negative or wrong_misplaced:
            vocab = remove_word(vocab, candidate)

    return vocab


def guess_next(
    vocab: tuple[str, ...], history: tuple[tuple[str, str], ...]
) -> Optional[str]:
    """ Returns a valid next guess that doesn't violate known information
        from previous guesses.

    Parameters:
        vocab: The allowed guesses vocab.
        history: contains tuples of all previous (guess, processed_guess)

    Returns:
        A valid word for the next guess chosen using a non-random method.
    """
    # Filter out words with non-unique letters
    vocab = remove_duplicated_letters(vocab, history)

    # Filter out words that violate known information
    for guess, info in history:
        if guess in vocab:
            vocab = remove_word(vocab, guess)
        for i, status in enumerate(info):
            vocab = filter_words(vocab, guess, i, status)

    # Return None if there's no valid word (this shouldn't happen
    # Ever because the answer should be in the vocab)
    if len(vocab) == 0:
        return
    # Select a valid work using a NON-RANDOM method

    return vocab[0]
## End CSSE7030 task ##


def play_round(answer: str, vocab: tuple[str, ...]) -> int:
    """Orchestrates a full round of Wordle with the given answer and
        allowed vocabulary.

    Parameters:
        answer: The answer word for this round.
        vocab: The allowed guesses vocab.

    Returns:
        The number of guesses the player took to correctly guess the word,
         or -1 if they quit, or MAX_GUESSES + 1 if they lost.
    """
    history: tuple[tuple[str, str], ...] = ()
    guess_number = 0

    while True:
        guess = prompt_user(guess_number + 1, vocab)

        if len(guess) == 1:
            if guess == QUIT:
                return -1
            elif guess == KEYBOARD:
                print_keyboard(history)
                continue
            elif guess == HELP:
                print_help()
                continue
            elif guess == SUGGESTION:
                # This is only necessary for CSSE7030
                guess = guess_next(vocab, history)

        # User entered a valid guess; process and display
        history = update_history(history, guess, answer)
        print_history(history)

        guess_number += 1

        if has_won(guess, answer):
            print(WIN_MESSAGE.format(guess_number))
            return guess_number

        if has_lost(guess_number):
            print(LOSS_MESSAGE.format(answer))
            return MAX_GUESSES + 1


def main():
    """Entry-point to gameplay."""
    vocab = load_words(VOCAB_FILE)
    candidate_answers = load_words(ANSWERS_FILE)
    stats = (0,) * (WORD_LENGTH + 1)

    while True:
        answer = choose_word(candidate_answers)
        # Prevent the answer from being chosen again
        candidate_answers = remove_word(candidate_answers, answer)

        result = play_round(answer, vocab)
        if result == -1:  # user chose to quit
            break

        stats = update_stats(stats, result)
        print_stats(stats)

        # Ask whether to exit or replay
        if input(PLAY_AGAIN_PROMPT).lower() != YES:
            break


if __name__ == "__main__":
    main()
