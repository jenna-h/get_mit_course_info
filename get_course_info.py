from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time

# Make sure you have the right versions of Selenium, Chrome Driver, and Chrome
# Replace this file path with the right file path if your Chrome Driver is somewhere else
driver = webdriver.Chrome('/usr/local/bin/chromedriver')

# Translate Infinite Connection output to pretty course numbers
INFCON_TO_SHEET = {'1 - Civil and Environmental Engineering': '1',
                   '2 - Mechanical Engineering': '2',
                   '2A - Mech Eng - Coop': '2A',
                   '2O - Mech and Ocean Eng - SB': '2O',
                   '3 - Materials Sci & Eng': '3',
                   '3A - Materials Sci & Eng': '3A',
                   '4 - Architecture': '4',
                   '5 - Chemistry': '5',
                   '57 - Chemistry & Biology': '5-7',
                   '67 - Comp Sci & Mol Bio': '6-7',
                   '6 - Elec Eng & Comp Sci': '6',
                   '6 - Computer Science': '6-14',
                   '61 - Electrical Engrg': '6-1',
                   '62 - Elec Eng & Comp Sci': '6-2',
                   '63 - Computer Sci & Engrg': '6-3',
                   '6P - Elec Eng & Comp Sci': '6P',
                   '7 - Biology/Life Science': '7',
                   '7D - Biology - Doctoral': '7D',
                   '8 - Physics': '8',
                   '9 - Brain & Cognitive Sciences': '9',
                   '10 - Chemical Engineering': '10',
                   '10B - Chemical-Biological Engineering': '10B',
                   '15 - Management': '15',
                   '151 - Management': '15-1',
                   '152 - Business Analytics': '15-2',
                   '153 - Finance': '15-3',
                   '16 - AeroAstro': '16',
                   '16 - Aeronautics and Astronautics': '16',
                   '16E - AeroAstro': '16E',
                   '18 - Mathematics': '18',
                   '18C - Math With Comp Sci': '18C',
                   '20 - Biological Engineering': '20',
                   '21C - Comparative Media Studies':'21C',
                   '22 - Nuclear Engineering': '22',
                   '241 - Philosophy': '24-1',
                   'UND - Undesignated/Undeclared': 'UND',
                   }

# Translate courses with modifiers to their unmodified versions
MAJMOD_TO_UNMOD = {'2A': ['2'],
                   '2O': ['2'],
                   '3A': ['3'],
                   '5-7': ['5', '7'],
                   '6-1': ['6'],
                   '6-2': ['6'],
                   '6-3': ['6'],
                   '6-7': ['6', '7'],
                   '6-14': ['6', '14'],
                   '6P': ['6'],
                   '7A': ['7'],
                   '7D': ['7'],
                   '10B': ['10'],
                   '10E': ['10'],
                   '14-2': ['14'],
                   '15-1': ['15'],
                   '15-2': ['15'],
                   '15-3': ['15'],
                   '16E': ['16'],
                   '18C': ['18'],
                   '21C': ['21'],
                   '24-1': ['24']
                   }
                   
# How many seconds should I wait for the Infinite Connection to load?
WAIT_TIME = 2

# Login info for Infinite Connection goes here
USERNAME = # YOUR USERNAME HERE
PASSWORD = # YOUR PASSWORD HERE

def open_infinite_connection():
    '''Opens and logs into the Infinite Connection.'''
    driver.get('https://alum.mit.edu/directory/#/')
    username = driver.find_element_by_id('username')
    username.send_keys(USERNAME)
    password = driver.find_element_by_id('password')
    password.send_keys(PASSWORD + Keys.ENTER)

def search(name):
    '''Performs a search for a person using the Infinite Connection.
    Throws an exception if more than one record comes up, or
    if something else goes wrong. Otherwise, returns some info about the person.'''
    driver.get('https://alum.mit.edu/directory/#/')
    searchbox = driver.find_element_by_xpath("//*[@class='typeahead tt-input']")
    searchbox.click()
    webdriver.ActionChains(driver).send_keys(name + Keys.ENTER).perform()
    time.sleep(WAIT_TIME)
    num_records = driver.find_element_by_xpath('//*[@id="content-wrapper"]/div[1]/div/div[2]/h1')
    assert(num_records.text == '1 Records')
    info = driver.find_element_by_xpath('//*[@id="directory-search-filters"]/div[2]/div/div[2]/div[2]/div[4]/div')
    return info.text
    
def parse_csv(simmons_db_csv):
    '''Returns a list of names from a Simmons DB-style CSV'''
    names = simmons_db_csv.split('\n')
    names = [name.split('\t')[1] + ' ' + name.split('\t')[0] for name in names]
    return names

def convert_kerbs_to_names(kerbs_list):
    '''Converts a list of kerbs to names.'''
    driver.get('https://web.mit.edu/people.html')
    names_list = []
    for kerb in kerbs_list:
        names_list.append(convert_kerb_to_name(kerb))
    go(names_list)
    
def convert_kerb_to_name(kerb):
    search_box = driver.find_element_by_name('query')
    search_box.send_keys(kerb)
    search_box.send_keys(Keys.ENTER)
    time.sleep(WAIT_TIME)
    search_result = driver.find_element_by_xpath('/html/body/div[2]/div[1]/table/tbody/tr[7]/td[3]/table[1]/tbody/tr/td/pre').get_attribute("innerHTML").splitlines()[0]
    # search result looks like '      name: Himawan, Jenna M.'
    name_only = search_result[len('      name: '):]
    last, first_and_middle = name_only.split(', ')
    if len(first_and_middle.split(' ')) == 2:
        first, middle = first_and_middle.split(' ')
    name = first + ' ' + last
    return name
    

def go(names_list):
    '''Print out course numbers for all the people in names_list'''
    open_infinite_connection()
    for name in names_list:
        try:
            res = search(name).split(', ')[2]
            if res in INFCON_TO_SHEET:
                print("'"+INFCON_TO_SHEET[res])
            else:
                print("'"+res)
        except:
            print('Could not find', name)
    driver.close()

def get_unmod_counts(mod_counts):
    '''Given course numbers with modifiers, count how many people belong
    to each unmodified / base course.'''
    unmod_counts = {}
    for mod_course in mod_counts.split('\n'):
        if mod_course in MAJMOD_TO_UNMOD:
            for unmod_course in MAJMOD_TO_UNMOD[mod_course]:
                if unmod_course in unmod_counts:
                    unmod_counts[unmod_course] += 1/len(MAJMOD_TO_UNMOD[mod_course])
                else:
                    unmod_counts[unmod_course] = 1/len(MAJMOD_TO_UNMOD[mod_course])
        else:
            if mod_course in unmod_counts:
                unmod_counts[mod_course] += 1
            else:
                unmod_counts[mod_course] = 1
    return unmod_counts

def use_kerbs(kerbs_list):
    names_list = convert_kerbs_to_names(kerbs_list)


# use_kerbs(['benbit', 'aphacker'])
# go(parse_csv('''Alyssa	Hacker
# Ben	Bitdiddle'''))
