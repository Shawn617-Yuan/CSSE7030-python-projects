"""
Wordle
Assignment 1
Semester 1, 2022
CSSE1001/CSSE7030
"""

from string import ascii_lowercase
from typing import Optional

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

# 所有出现的字符串和数字变量，都要在global中声明

# Replace these <strings> with your name, student number and email address.
__author__ = "Shuo Yuan, 46920348"
__email__ = "s4692034@student.uq.edu.au"


# Add your functions here
def has_won(guess: str, answer: str) -> bool:
    """ Determine if the player has met the win condition.

	Parameters:
		guess (str): The word of player guessed.
		answer (str): The answer to this round of games.

	Returns:
		bool: A boolean value reflecting whether the player is winning or not.
	"""
    if len(guess) == 6 and len(answer) == 6:
        if guess == answer:  # 直接简化为return guess == answer
            return True
        else:
            return False
    else:
        return False


def has_lost(guess_number: int) -> bool:
    """ Determine if the player has lost the game.

	Parameters:
		guess_number (int): The number of times the player has tried in this round of the game.

	Returns:
		bool: A boolean value reflecting whether the player lost the game.
	"""
    if guess_number >= 6: # 直接简化为return guess_number >= 6
        return True
    else:
        return False


def remove_word(words: tuple[str, ...], word: str) -> tuple[str, ...]:
    """ Remove the word(tuple element) in words(tuple).

	Parameters:
		words (tuple<str>): The tuple to perform the element deletion.
        word (str): The element to be deleted.

	Returns:
		tuple<str>: A copy of words with word removed.
	"""

    # A temporary list, since it is not possible to directly modify the tuple.
    temp_list = list()  # 变量名不能阐述类型，且in-line comment不要解释简单的东西

    for element in words:
        if element != word:
            temp_list.append(element)
        else:
            continue

    return tuple(temp_list)


def prompt_user(guess_number: int, words: tuple[str, ...]) -> str:
    """ Prompts the user for the next guess, reprompting until either a valid guess is entered, or a selection for help,
        keyboard, or quit is made.

	Parameters:
		guess_number (int): The number of times the player has tried in this round of the game.
        words (tuple<str>): The tuple containing all the valid words.

	Returns:
		str: The first valid guess or request for help, keyboard, or quit.
	"""
    while 1:
        user_input = input('Enter guess %d: ' % guess_number)

        # Make sure the returned string is lowercase
        lowercase_input = user_input.lower()

        if lowercase_input == 'a':  # 这里犯了代码重复的错误，直接用in来涵括同结果的情况
            return lowercase_input
        elif lowercase_input == 'k':
            return lowercase_input
        elif lowercase_input == 'q':
            return lowercase_input
        elif lowercase_input == 'h':
            return lowercase_input
        elif len(lowercase_input) != 6:
            print('Invalid! Guess must be of length 6')  # 注意结尾要返回一个string，如果长度不等于6就只返回None，不对
        elif lowercase_input not in words:
            print('Invalid! Unknown word')
        else:
            return lowercase_input


def process_guess(guess: str, answer: str) -> str:
    """ Compare the letters in the same position of guess and answer, and guess is processed by three different colored
        squares corresponding to CORRECT, INCORRECT and MISPLACED.

	Parameters:
		guess (str): The word of player guessed.
		answer (str): The answer to this round of games.

	Returns:
		str: A modified representation of guess.
	"""
    if len(guess) == 6 and len(answer) == 6:
        feedback = str()
        compare_result = list()
        duplicate_test = dict()

        for location in range(len(guess)):
            # Determine if each letter is correct from the beginning and save the result in compare_result
            if guess[location] == answer[location]:
                compare_result.append(CORRECT)
            elif guess[location] in answer:
                compare_result.append(MISPLACED)
            else:
                compare_result.append(INCORRECT)

            # Players may enter a repeated letter multiple times, duplicate_test keep track of the position of different
            # letters in the guess
            if guess[location] not in duplicate_test.keys():
                duplicate_test[guess[location]] = [location]
            else:
                duplicate_test[guess[location]].append(location)

            temp_result = list()
            for key in duplicate_test:
                # For repeated letters in guess
                if len(duplicate_test[key]) > 1:
                    # Use temp_result to save the compare_result of the repeated letter in different positions
                    for index in duplicate_test[key]:
                        temp_result.append(compare_result[index])

                    for index in duplicate_test[key]:
                        # If the compare_result of repeated letters is CORRECT, save its position to correct_mark, save
                        # only the compare_result of the correct_mark position as CORRECT, and then change the others to INCORRECT
                        if compare_result[index] == CORRECT:
                            correct_mark = index
                            for location1 in duplicate_test[key]:
                                compare_result[location1] = INCORRECT
                            compare_result[correct_mark] = CORRECT
                        # If all the compare_result of the repeated letters are MISPLACED, then only the compare_result
                        # of the first repeated location will be MISPLACED, and all others will be INCORRECT
                        elif (len(set(temp_result)) == 1) and (compare_result[index] == MISPLACED):
                            for location2 in duplicate_test[key]:
                                compare_result[location2] = INCORRECT
                            compare_result[duplicate_test[key][0]] = MISPLACED
        # If convert compare_result directly to a string, each element will be separated by a comma
        for item in compare_result:
            feedback += item
        return feedback


def update_history(history: tuple[tuple[str, str], ...], guess: str, answer: str) -> tuple[tuple[str, str], ...]:
    """ Update the guess history.

	Parameters:
		history (tuple<tuple<str>>): A tuple where each element is a tuple of (guess, processed guess).
        guess (str): The word of player guessed.
		answer (str): The answer to this round of games.

	Returns:
		tuple<tuple<str>>: A copy of history updated to include the latest guess and its processed form.
	"""

    # Cannot modify a tuple directly, so first convert the tuple to a list and after modification, convert it to a tuple
    temp_history = list(history)
    tuple_element = (guess, process_guess(guess, answer))
    temp_history.append(tuple_element)
    return tuple(temp_history)  # 直接一步到位history + ((guess, process_guess(guess, answer)),)


def print_history(history: tuple[tuple[str, str], ...]) -> None:
    """ Prints the guess history in a user-friendly way.

	Parameters:
		history (tuple<tuple<str>>): A tuple where each element is a tuple of (guess, processed guess).

	Returns:
		None
	"""
    if len(history) == 0:
        print('---------------\n')
    
    # Determine how many histories to output based on the guess_time
    else:
        guess_time = 1
        print('---------------')

        # Make sure the history is printed in a user-friendly way
        for index in range(len(history)):
            print('Guess %d: ' % guess_time, end=' ')
            for letter in history[index][0]:
                print(letter, end=' ')  # 我是用循环输出每个字母，他直接用join，不用循环

            print("\n         ", end='')
            for result in history[index][1]:
                print(result, end='')

            print('\n---------------\n')
            guess_time += 1  # 他也没用到guess_time，直接用enumerate函数中的编号+1来完成了


def print_keyboard(history: tuple[tuple[str, str], ...]) -> None:
    """ Prints the keyboard in a user-friendly way with the information currently known about each letter.

	Parameters:
		history (tuple<tuple<str>>): A tuple where each element is a tuple of (guess, processed guess).

	Returns:
		None
	"""
    print('\nKeyboard information\n------------')
    loop_time = 1  # 甚至用不到loop_time，直接用for i in range(0,26,2)，然后i, i+1就好了
    keyword_info = dict()
    letters = ascii_lowercase

    for letter in letters:
        keyword_info[letter] = UNSEEN

    if len(history) == 0:
        for letter in letters:
            output = letter + ': ' + keyword_info[letter]

            # Ensure that only two letters are output per line
            if loop_time % 2 != 0:
                print(output, end='\t')
            else:
                print(output)
            loop_time += 1
    else:
        # Combine each letter and compare_result into a one-to-one dictionary
        for index in history:
            for location in range(6):
                keyword_info[index[0][location]] = index[1][location]  # 通过元组的属性我能直接找到result，然后用index来索引位置，根本不需要用字典

        for letter in letters:
            output = letter + ': ' + keyword_info[letter]
            if loop_time % 2 != 0:
                print(output, end='\t')
            else:
                print(output)
            loop_time += 1
        print()


def print_stats(stats: tuple[int, ...]) -> None:
    """ Prints the stats in a user-friendly way.

	Parameters:
		stats (tuple<int>): A tuple containing seven elements, which are the number of rounds won in 1-6 guesses, and
		                    the number of rounds lost, respectively.

	Returns:
		None
	"""
    print('\nGames won in:')
    for times in range(7):  # 可以省个range(7)，直接用enumerate(stats[:-1])除去最后一个元素
        if times == 6:
            print('Games lost: %d' % stats[-1])
        else:
            print("%d moves: %d" % (times + 1, stats[times]))


def guess_next(vocab: tuple[str, ...], history: tuple[tuple[str, str], ...]) -> Optional[str]:
    """ Based on the history to intelligently generate the next guess.

	Parameters:
		vocab (tuple<str>): A tuple containing all the valid words.
        history (tuple<tuple<str>>): A tuple where each element is a tuple of (guess, processed guess).

	Returns:
		Optional<str>: A valid next guess that doesn't violate known information from previous guesses. If no valid word
		               remains in the vocabulary, this function return None.
	"""
    correct_letter = list()
    correct_loc = list()
    abandon_letter = str()
    misplace_letter = str()
    misplace_loc = list()
    filtered_word = list()
    # Save the compare_result and location of each letter
    for record in history:
        for location in range(6):
            if record[1][location] == CORRECT:
                correct_letter.append(record[0][location])
                correct_loc.append(location)
            # Repeated letters can only be saved once
            elif record[1][location] == MISPLACED and record[0][location] not in misplace_letter:
                misplace_letter += record[0][location]
                misplace_loc.append(location)
            else:
                abandon_letter += record[0][location]

    # Filter the vocabulary based on whether the compare_result contain MISPLACED and CORRECT to filter out words that
    # do not have incorrect letters, correct letters in the right place, and misplaced letters appearing in different places
    if len(correct_letter) != 0 and len(misplace_letter) != 0:
        for word in vocab:
            for index_cor in range(len(correct_letter)):
                for index_mis in range(len(misplace_letter)):
                    if abandon_letter not in word and (correct_letter[index_cor] == word[correct_loc[index_cor]]) and \
                            (misplace_letter[index_mis] in word) and (
                            misplace_letter[index_mis] != word[misplace_loc[index_mis]]):
                        filtered_word.append(word)
    elif len(correct_letter) == 0:
        for word in vocab:
            for index_mis in range(len(misplace_letter)):
                if abandon_letter not in word and (misplace_letter[index_mis] in word) and \
                        (misplace_letter[index_mis] != word[misplace_loc[index_mis]]):
                    filtered_word.append(word)
    elif len(misplace_letter) == 0:
        for word in vocab:
            for index_cor in range(len(correct_letter)):
                if abandon_letter not in word and (correct_letter[index_cor] == word[correct_loc[index_cor]]):
                    filtered_word.append(word)
    else:
        for word in vocab:
            if abandon_letter not in word:
                filtered_word.append(word)

    if len(filtered_word) == 0:
        return None
    else:
        return choose_word(tuple(filtered_word))


def game_play(words: tuple[str, ...], stats: tuple[int, ...]) -> None:
    """ The whole game flow.

	Parameters:
		words (tuple<str>): The tuple containing all the valid words.
        stats (tuple<int>): A tuple containing seven elements, which are the number of rounds won in 1-6 guesses, and
                            the number of rounds lost, respectively.

	Returns:
		None
	"""
    guess_time = 1
    answer = choose_word(load_words(ANSWERS_FILE))
    history = tuple()  # 不要加tuple!!!直接history = ()

    while guess_time <= 6:
        guess = prompt_user(guess_time, words)
        if guess == 'k':
            print_keyboard(history)
        elif guess == 'q':
            break
        elif guess == 'h':
            print('Ah, you need help? Unfortunate.')
            remove_word(history, history[-1])
        elif guess == 'a':
            if guess_next(words, history) is None:
                raise SystemExit
            else:
                history = update_history(history, guess_next(words, history), answer)
                guess_time += 1
                print_history(history)
        elif has_won(guess, answer):
            print("Correct! You won in %d guesses!" % guess_time)
            play_again(guess_time, words, stats)
        else:
            history = update_history(history, guess, answer)
            guess_time += 1
            print_history(history)

    if has_lost(guess_time):
        print("You lose! The answer was: %s" % answer)
        play_again(guess_time, words, stats)


def play_again(guess_number: int, words: tuple[str, ...], stats: tuple[int, ...]) -> None:
    """ At the end of the game the player is asked if he wants to restart the game, and if the player chooses to restart
        the game, then the game_play function is called again.

	Parameters:
		guess_number (int): The number of times the player has tried in this
                            round of the game.
        stats (tuple<int>): A tuple containing seven elements, which are the number of rounds won in 1-6 guesses, and
                            the number of rounds lost, respectively.

	Returns:
		None
	"""
    temp_list = list(stats)
    temp_list[guess_number - 1] += 1
    stats = tuple(temp_list)
    print_stats(stats)
    choose = input("Would you like to play again (y/n)?")
    if choose == 'y':
        game_play(words, stats)
    else:
        return None


def main():
    words = load_words(VOCAB_FILE)
    # Stats must record information for each game, and game_play will be called repeatedly
    stats = (0, 0, 0, 0, 0, 0, 0)
    game_play(words, stats)


if __name__ == "__main__":
    main()
