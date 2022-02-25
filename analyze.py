import collections
import json
import os
import re
import sys
from collections import Counter, OrderedDict

import emoji
import nltk
from nltk.corpus import stopwords
from progress.bar import Bar

import graphs

# To get rid of file extension when making graphs
file_split = re.compile(r'(.*)(.[a-zA-Z0-9]{3,4})')

"""
If value exists in the dictionary, increment count. Else add a new entry.
"""


def add_to_dictionary(dictionary, key):
    if key in dictionary:
        dictionary[key] += 1
    else:
        dictionary[key] = 1
    return dictionary


def add_to_dictionary_value(dictionary, key, value):
    if key in dictionary:
        dictionary[key] += value
    else:
        dictionary[key] = value
    return dictionary


"""
Generates a list of frequent words from the list of messages.
Uses a list of common words to avoid.
Takes one message at a time and repeats the following steps:
    Get individual words by splitting the message on every space.
    Convert each word to lower case.
    If the word is in the list of common words, go to the next word.
    Otherwise, "clean" the word. This involves removing any non-alphanumeric characters.
    If the word is already in the dictionary, increment the count.
    Else add it to the list.
When the entire list of messages is covered, return the frequency dict.
"""


def get_word_frequency(message_list):
    stop_words_list = set(stopwords.words('english'))
    clean_word_regex = re.compile(r'[а-яА-Яa-zA-Z0-9]+')
    frequency_dictionary = Counter()
    for messages in message_list:
        processed_words = []
        words_list = messages.split(' ')
        for word in words_list:
            # word = replace_diacritics(word)

            # ignore empty strings or letters
            if len(word) == 0 or len(word) == 1:
                continue
            regex_result = clean_word_regex.search(word.lower())
            if regex_result is None:
                continue
            else:
                clean_word = regex_result.group()

            if clean_word in stop_words_list:
                continue
            elif clean_word_regex.search(clean_word):
                processed_words.append(clean_word)
        frequency_dictionary.update(processed_words)
    return frequency_dictionary


def get_emoji_frequency(message_list):
    frequency_dictionary = Counter()
    for messages in message_list:
        processed_words = []
        words_list = messages.split(' ')
        for words in words_list:
            word = words.lower()
            processed_words.append(word)
        frequency_dictionary.update(processed_words)
    return frequency_dictionary


"""
Function to accept command-line arguments.
If no arguments are found, then it prints an error and stops the script.
Else it returns the arguments.
"""


def get_file_name():
    # If no filename is given
    if len(sys.argv) < 2:
        print('Usage: ' + sys.argv[0] + ' [file_name.extension]')
        sys.exit()
    # Get file name from command line
    return ' '.join(sys.argv[1:])


"""
Function to read the input file of text chats.
Copies it to a variable and returns it.
"""


def read_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as fi:
        text_to_analyze = fi.readlines()
    return text_to_analyze


def extract_emojis(s):
    return ''.join(c for c in s if c in emoji.UNICODE_EMOJI['en'])


"""
    Initialize all variables.
    Read one message at a time.
    Check if it matches our Regex "line" format.
    If it does, perform this process:
        Separate the date, time, person and put them into separate dictionaries.
        If the message isn't some sort of media attachment, add to message_list.
        Increment the number of messages.
    """


def process_data(json_data):
    # Initializing our variables
    number_of_messages = 0
    total_chars = {}
    date_dictionary = {}
    time_dictionary = {}
    person_dictionary = {}
    message_list = []
    emoji_list = []

    time_split = re.compile(r'([0-9]{4}.[0-9]{2}.[0-9]{2})(T)([0-9]{1,2}:[0-9]{2}:[0-9]{2})')
    # Collecting data into variables
    bar = Bar('Processing', max=len(json_data))
    for message in json_data:
        if 'sticker emoji' in message:
            # is a sticker message, ignore
            pass
        else:
            message_text = message['text']
            if type(message_text) == list:
                # is most probably a URL, so will ignore for now
                pass
            else:
                message_list.append(message_text)

                emojis = extract_emojis(message_text)
                for e in emojis:
                    emoji_list.append(e)
                person_dictionary = add_to_dictionary(person_dictionary, message['from'])
                total_chars = add_to_dictionary_value(total_chars, message['from'], len(message_text))

                date = message['date']
                time_found = time_split.search(date)
                """
                time_found:
                index 0 - all the groups concatenated: 2020-12-10T11:28:02
                index 1 - first group:                 2020-12-10
                index 2 - second group (ignored):      T
                index 3 - third group:                 11:28:02
                """
                date_dictionary = add_to_dictionary(date_dictionary, time_found[1])
                message_hour = time_found[3].split(':')[0]
                time_dictionary = add_to_dictionary(time_dictionary, message_hour)
                number_of_messages += 1
        bar.next()
    bar.finish()

    word_dictionary = get_word_frequency(message_list)
    emoji_dictionary = get_emoji_frequency(emoji_list)
    processed_data = {'time_dictionary': time_dictionary,
                      'date_dictionary': date_dictionary,
                      'person_dictionary': person_dictionary,
                      'word_dictionary': word_dictionary,
                      'number_of_messages': number_of_messages,
                      'emoji_dictionary': emoji_dictionary,
                      'total_chars': total_chars}
    return processed_data


"""
Sorts a dictionary by value or key. Value by default.
Uses an OrderedDict since in Python dictionaries can't be sorted.
"""


def sort_dictionary(dictionary, sort_by='value'):
    if sort_by == 'key':
        return OrderedDict(sorted(dictionary.items()))
    return OrderedDict(sorted(dictionary.items(), key=lambda x: x[1], reverse=True))


def revert_dictionary(dictionary):
    return collections.OrderedDict(reversed(list(dictionary.items())))


def preprocess_data(data):
    # filters out only the messages
    filtered_data = list(filter(lambda x: x['type'] == 'message', data['messages']))
    discussion_name = data['name']
    return filtered_data, discussion_name


def driver():
    # Read given file
    file_name_with_extension = get_file_name()

    with open(file_name_with_extension) as json_file:
        json_data = json.load(json_file)
    # Collect data
    json_data, discussion_name = preprocess_data(json_data)
    processed_data = process_data(json_data)

    # Sort all Dictionaries here
    word_dictionary = OrderedDict(processed_data['word_dictionary'].most_common(150))
    emoji_dictionary = OrderedDict(processed_data['emoji_dictionary'].most_common(20))
    person_dictionary = sort_dictionary(processed_data['person_dictionary'])
    date_dictionary = sort_dictionary(processed_data['date_dictionary'])
    inverse_date_dictionary = revert_dictionary(sort_dictionary(processed_data['date_dictionary']))
    number_of_messages = processed_data['number_of_messages']
    total_chars = processed_data['total_chars']

    if not os.path.exists('output'):
        os.mkdir('output')

    graphs.bar_graph(
        word_dictionary, 25, 'Uses',
        'Most used words in ' + str(number_of_messages) + ' messages in ' + discussion_name,
        'output/' + discussion_name + '_word_frequency.png'
    )

    # emojis do not draw correctly on most systems because the font does not support them, so removing them for now
    # graphs.bar_graph(
    #     emoji_dictionary, 20, 'Uses',
    #     'Most used emojis in ' + str(number_of_messages) + ' messages in ' + file_name,
    #     'output/' + file_name + 'emoji_frequency.png'
    # )
    #

    # Prints the most used emojis as alternative to exporting an image with the respective graph
    for key, value in emoji_dictionary.items():
        print(key + '\t-> ' + str(value))

    # total chars per user and average chars per msg in the chat
    for key, value in total_chars.items():
        print(key + '\t-> total: ' + str(value) + ' avg: ' + str(value / person_dictionary[key]))

    graphs.bar_graph(
        person_dictionary, 20, 'Messages',
        'Most active person in ' + discussion_name,
        'output/' + discussion_name + '_person_activity.png'
    )
    #
    graphs.bar_graph(
        date_dictionary, 20, 'Messages',
        'Most Messages with ' + discussion_name,
        'output/' + discussion_name + '_date_activity.png'
    )

    graphs.bar_graph(
        inverse_date_dictionary, 20, 'Messages',
        'Least Messages in ' + discussion_name,
        'output/' + discussion_name + '_inverse_date_activity.png'
    )
    #
    graphs.histogram(
        processed_data['time_dictionary'],
        'Message Frequency Chart in ' + discussion_name,
        'output/' + discussion_name + '_time_activity.png'
    )


"""
Checks whether the environment has the stopwords resource
already installed, if not, downloads them.
"""


def prepare_stop_words():
    try:
        nltk.data.find('corpora/stopwords.zip')
    except LookupError:
        nltk.download('stopwords')


if __name__ == "__main__":
    prepare_stop_words()
    driver()
