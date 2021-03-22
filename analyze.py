#!python3
import os
import re
import sys
import graphs
from collections import Counter, OrderedDict
from bs4 import BeautifulSoup
from progress.bar import Bar

# To get rid of file extension when making graphs
file_split = re.compile(r'(.*)(.[a-zA-Z0-9]{3,4})')

"""
If value exists in the dictionary, increment count. Else add a new entry.
"""


def add_to_dictionary(dictionary, value):
    if value in dictionary:
        dictionary[value] += 1
    else:
        dictionary[value] = 1
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
    #with open('commonWordsRussian.txt', 'r') as word_file:
    common_words_list = []#word_file.read()
    clean_word = re.compile(r'[а-яА-Яa-zA-z0-9]+')
    frequency_dictionary = Counter()
    for messages in message_list:
        processed_words = []
        words_list = messages.split(' ')
        for words in words_list:
            word = words.lower()
            if word in common_words_list:
                continue
            if clean_word.search(word):
                word = clean_word.search(word).group()
                processed_words.append(word)
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
        print('Usage: vkAnalyze.py file_name.extension')
        sys.exit()
    # Get file name from command line
    return ' '.join(sys.argv[1:])


"""
Function to read the input file of chats.
Copies it to a variable and returns it.
"""


def read_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as fi:
        text_to_analyze = fi.readlines()
    return text_to_analyze


"""
    Initialize all variables.
    Read one message at a time.
    Check if it matches our Regex "line" format.
    If it does, perform this process:
        Separate the date, time, person and put them into separate dictionaries.
        If the message isn't some sort of media attachment, add to message_list.
        Increment the number of messages.
    """


def collect_data(text_to_analyze):
    # Initializing our variables
    number_of_messages = 0
    date_dictionary = {}
    time_dictionary = {}
    person_dictionary = {}
    message_list = []
    emoji_list = []

    time_split = re.compile(r'([0-9]{4}.[0-9]{2}.[0-9]{2})( )([0-9]{1,2}:[0-9]{2}:[0-9]{2})')
    # Collecting data into variables
    bar = Bar('Processing', max=len(text_to_analyze))
    for lines in text_to_analyze:
        lt = str(lines)
        if 'msg_body' in lt and 'emoji' not in lt:
            if 'msg7' in lt or 'msg8' in lt or 'msg9' in lt or 'msg1' in lt:
                from_data = lines.find_all("div", {"class": "from"})
                from_data_as = from_data[0].find_all("a")
                message_text = lines.find("div", {"class": "msg_body"}).text
                time_found = time_split.search(from_data_as[1].text)
                time_splitted = time_found[0].split(' ')[0].split('.')
                formatted_date = time_splitted[2] + '/' + time_splitted[1] + '/' + time_splitted[0][-2:]
                date_dictionary = add_to_dictionary(date_dictionary, formatted_date)
                person_dictionary = add_to_dictionary(person_dictionary, from_data[0].find("b").text)
                hour_splitted = time_found[0].split(' ')[1].split(':')[0]
                time_dictionary = add_to_dictionary(time_dictionary, str(hour_splitted))
                message_list.append(message_text)
                number_of_messages += 1
        if 'msg_body' in lt and 'emoji' in lt:
            if 'msg7' in lt or 'msg8' in lt or 'msg9' in lt or 'msg1' in lt:
                from_data = lines.find_all("div", {"class": "from"})
                from_data_as = from_data[0].find_all("a")
                message_text = lines.find("div", {"class": "msg_body"}).text
                message = lines.find_all("div", {"class": "msg_body"})
                emojis = message[0].find_all("img", {"class": "emoji"})
                for emoji in emojis:
                    emoji_list.append(emoji.get('alt'))
        bar.next()
    bar.finish()
    word_dictionary = get_word_frequency(message_list)
    emoji_dictionary = get_emoji_frequency(emoji_list)
    print(message_list[-1])
    return time_dictionary, date_dictionary, person_dictionary, word_dictionary, number_of_messages, emoji_dictionary


def convert_data(text_to_analyze):
    # Initializing our variables
    number_of_messages = 0
    date_dictionary = {}
    time_dictionary = {}
    person_dictionary = {}
    message_list = []
    emoji_list = []

    export_list = []
    time_split = re.compile(r'([0-9]{4}.[0-9]{2}.[0-9]{2})( )([0-9]{1,2}:[0-9]{2}:[0-9]{2})')
    # Collecting data into variables
    bar = Bar('Processing', max=len(text_to_analyze))
    for lines in text_to_analyze:
        lt = str(lines)
        if 'msg_body' in lt:
            if 'msg7' in lt or 'msg8' in lt or 'msg9' in lt or 'msg1' in lt:
                from_data = lines.find_all("div", {"class": "from"})
                from_data_as = from_data[0].find_all("a")
                message_text = lines.find("div", {"class": "msg_body"}).text
                time_found = time_split.search(from_data_as[1].text)
                time_splitted = time_found[0].split(' ')[0].split('.')
                time_for_converting = time_splitted[1] + '/' + time_splitted[2] + '/' + time_splitted[0][-2:]
                formatted_date = time_splitted[2] + '/' + time_splitted[1] + '/' + time_splitted[0][-2:]
                date_dictionary = add_to_dictionary(date_dictionary, formatted_date)
                person_dictionary = add_to_dictionary(person_dictionary, from_data[0].find("b").text)
                hour_splitted = time_found[0].split(' ')[1].split(':')[0]
                time_dictionary = add_to_dictionary(time_dictionary, str(hour_splitted))
                message_list.append(message_text.strip())
                time = time_found[0].split(' ')[1].split(':')
                emojis = lines.find('div', {'class':'msg_body'}).find_all("img", {"class": "emoji"})
                for emoji in emojis:
                    message_text += emoji.get('alt').strip()
                name = from_data[0].find('b').text.strip()
                if 'А' in name or 'а' in name:
                    name = 'Alina'
                message_to_export = time_for_converting + ', ' + time[0] + ':' + time[1] + ' - ' + name + ': ' + message_text.strip()
                message_to_export = message_to_export.strip()
                export_list.append(message_to_export)
                number_of_messages += 1
        #if 'msg_body' in lt and 'emoji' in lt:
         #   if 'msg7' in lt or 'msg8' in lt or 'msg9' in lt or 'msg1' in lt:
          #      from_data = lines.find_all("div", {"class": "from"})
           ###   message = lines.find_all("div", {"class": "msg_body"})
              #  emojis = message[0].find_all("img", {"class": "emoji"})
               # for emoji in emojis:
                #    emoji_list.append(emoji.get('alt'))
        bar.next()
    bar.finish()
    with open('export.txt', 'w+') as file:
        for line in export_list:
            file.write(line + '\n')

    word_dictionary = get_word_frequency(message_list)
    emoji_dictionary = get_emoji_frequency(emoji_list)
    #print(message_list[-1])
    return time_dictionary, date_dictionary, person_dictionary, word_dictionary, number_of_messages, emoji_dictionary


''' <div id="msg71252" class="msg_item">
        <div class="upic">
            <img src="https://pp.userapi.com/c846324/v846324545/d4cc5/f7DhWUrGHBw.jpg?ava=1" alt="[photo_100]">
        </div>
        <div class="from">
            <b>Alina Boschenko</b>
            <a href="http://vk.com/id133248061" target="_blank">@id_133248061</a>
            <a href="#msg71252">2019.05.16 16:52:51</a>
        </div>
        <div class="msg_body">1111111111</div>
    </div>
'''



"""
Sorts a dictionary by value or key. Value by default.
Uses an OrderedDict since in Python dictionaries can't be sorted.
"""


def sort_dictionary(dictionary, sort_by='value'):
    if sort_by == 'key':
        return OrderedDict(sorted(dictionary.items()))
    return OrderedDict(sorted(dictionary.items(), key=lambda x: x[1], reverse=True))


def driver():
    # Read given file
    file_name_with_extension = get_file_name()
    file_name = file_split.search(file_name_with_extension)[1]
    text_to_analyze = BeautifulSoup(open(file_name_with_extension), "lxml")
    my_divs = text_to_analyze.findAll("div", {"class": "msg_item"})
    print(len(my_divs))
    print("DONE PARSING HTML")
    # Collect data
    convert_data(my_divs)
    # time_dictionary, date_dictionary, person_dictionary, word_dictionary, number_of_messages, emoji_dictionary = collect_data(my_divs)
    # print("DONE EXTRACTING DATA")
    # # Sort all Dictionaries here
    # word_dictionary = OrderedDict(word_dictionary.most_common(150))
    # emoji_dictionary = OrderedDict(emoji_dictionary.most_common(20))
    # person_dictionary = sort_dictionary(person_dictionary)
    # date_dictionary = sort_dictionary(date_dictionary)
    #
    # if not os.path.exists('outputVk'):
    #     os.mkdir('outputVk')
    #
    # graphs.bar_graph(
    #     word_dictionary, 20, 'Uses',
    #     'Most used words in ' + str(number_of_messages) + ' messages in ' + file_name,
    #     'outputVk/' + file_name + 'word_frequency.png'
    # )
    #
    # graphs.bar_graph(
    #      emoji_dictionary, 20, 'Uses',
    #     'Most used emojis in ' + str(number_of_messages) + ' messages in ' + file_name, 'outputVk/' + file_name + 'emoji_frequency.png'
    # )
    #
    # graphs.bar_graph(
    #     person_dictionary, 20, 'Messages',
    #     'Most active person in ' + file_name,
    #     'outputVk/' + file_name + '-person_activity.png'
    # )
    #
    # graphs.bar_graph(
    #     date_dictionary, 20, 'Messages',
    #     'Most Messages in ' + file_name,
    #     'outputVk/' + file_name + '-date_activity.png'
    # )
    #
    # graphs.histogram(
    #     time_dictionary,
    #     'Message Frequency Chart in ' + file_name,
    #     'outputVk/' + file_name + '-time_activity.png'
    # )


if __name__ == "__main__":
    driver()
