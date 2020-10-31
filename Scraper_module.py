import requests
import bs4
import csv


def get_url():  # get the url from which we will later extract the data
    print('Please choose a county you would like to get the data for by pressing "X" under "Výběr obce". ')
    print('Choose from https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ')
    county_url = input('Insert the url of the county: ')

    return county_url


# here begins the first round of scraping; we want to scrape the number of the city, its name and the
# link we will use to get the information about the election itself


def bs4_scrape1(county_url):  # get the source code and extract some tags we need
    response_1 = requests.get(county_url)
    soup_1 = bs4.BeautifulSoup(response_1.text, 'html.parser')
    city_data = soup_1.find_all('td')

    return city_data


names_list = []  # will need this variable in global scope later (in city_parse function)


def get_city_names(city_data):  # get the names of the cities from td tags
    for i in city_data:
        if 'headers' in str(i) and 'center' not in str(i) and 'cislo' not in str(i):
            names_list.append(str(i)[26:-5].replace('<br/>', ''))  # found <br/> to be the issue only once fixed it tho
            for j in names_list:  # some td tags at the end of the table were blank, here they are deleted from list
                if '<' in j or '>' in j or '=' in j or '"' in j:
                    names_list.remove(j)

    return names_list


def get_city_url(city_data):  # get partial url for every city
    dirty_strings = []
    for i in city_data:  # extract the dirty strings containing partial urls first
        if 'cislo' in str(i):
            dirty_strings.append(i)

    partial_urls = []
    for i in dirty_strings:  # now clean the dirty
        partial_urls.append(str(dirty_strings[dirty_strings.index(i)].a)[9:-12].replace('amp;', ''))

    return partial_urls


numbers_list = []


def get_city_number(city_data):  # get id numbers of the cities
    for k in city_data:  # this way we get the numbers but also the Xs
        if 'center' in str(k) or 'cislo' in str(k):
            numbers_list.append(k.a.contents)

    for i in numbers_list:  # we get rid of the Xs
        numbers_list.remove(['X'])

    return numbers_list


# we have finished the first round of scraping
# now we need to look at each and every city and get some info


base_url = 'https://volby.cz/pls/ps2017nss/'

eligible_voters = []
distributed_envelopes = []
valid_votes = []

dirty_parties = []  # all the parties times every city
parties = []  # only one set of parties
party_votes = []


def bs4_scrape2(i):  # scraping every city for source code and extracting
    response_2 = requests.get(base_url + i)
    soup_2 = bs4.BeautifulSoup(response_2.text, 'html.parser')
    inside_data = list(soup_2.find_all('tr'))

    return inside_data


def voters_envelopes_votes(inside_data):  # getting data from part of inside_data based on its id str (sa2...)
    for j in inside_data[2]:  # this part holds 3 particular data for each city
        if 'sa2' in str(j):
            eligible_voters.append(str(j)[32:-5])

        elif 'sa3' in str(j):
            distributed_envelopes.append(str(j)[32:-5])

        elif 'sa6' in str(j):
            valid_votes.append(str(j)[32:-5])


def parties_and_votes(inside_data):  # getting names of parties and number of votes for each
    for k in inside_data:  # going through every element in this list
        if 'b3">-' not in str(k):
            for l in k:  # going through every line in each element
                if 't1sa1 t1sb2' in str(l):  # there are 2 panels, that means 4 id strings overall
                    dirty_parties.append(str(l)[26:-5])

                elif 't2sa1 t2sb2' in str(l):
                    dirty_parties.append(str(l)[26:-5])

                elif 't1sa2 t1sb3' in str(l):
                    party_votes.append(str(l)[40:-5])

                elif 't2sa2 t2sb3' in str(l):
                    party_votes.append(str(l)[40:-5])


def city_parse(partial_urls):  # getting all the remaining data
    for i in partial_urls:  # for every city
        inside_data = bs4_scrape2(i)  # getting data to parse through
        voters_envelopes_votes(inside_data)  # finds 3 particular pieces for every city
        parties_and_votes(inside_data)  # gets votes for every party for every city

    for i in range(int(len(dirty_parties)/len(names_list))):  # I have to choose only the first set of parties, it's
        parties.append(dirty_parties[i])  # the same for every city in region


def first_row():  # creating a header for our data
    header = ['Number', 'Name', 'Voters', 'Distributed envelopes', 'Valid votes']

    for i in parties:
        header.append(parties[parties.index(i)])  # inserting parties to the header

    return header


def final_data():  # getting the final form of data ready to be written to csv file
    final_list = [first_row()]  # inserting header

    for i in numbers_list:
        values_list = []  # temporary var for every cycle

        for j in i:
            # replacing \xa0 with ' ' due to some encoding issues
            values_list.append(str(numbers_list[numbers_list.index(i)]).strip("[]'"))
            values_list.append(names_list[numbers_list.index(i)].replace(u'\xa0', ' '))
            values_list.append(eligible_voters[numbers_list.index(i)].replace(u'\xa0', ' '))
            values_list.append(distributed_envelopes[numbers_list.index(i)].replace(u'\xa0', ' '))
            values_list.append(valid_votes[numbers_list.index(i)].replace(u'\xa0', ' '))

            # inserting number of votes for each party
            for k in range(numbers_list.index(i) * int(len(dirty_parties)/len(names_list)), (numbers_list.index(i) + 1) * int(len(dirty_parties)/len(names_list))):
                values_list.append(party_votes[k].replace(u'\xa0', ' '))

        final_list.append(values_list)

    return final_list


def file_name():  # get the name of the file about to be created
    filename = input('Please enter your desired csv file name: ')
    filename = filename + '.csv'
    return filename


def file_creator():  # create the file and insert all the data
    with open(file_name(), 'w', encoding='utf_16') as f:  # utf-8 had some issues with some czech chars, utf-16 works
        f_writer = csv.writer(f)
        f_writer.writerows(final_data())
    print('File containing election data has been created. ')
