import os
import re

def get_current_file_name():
    return os.path.basename(__file__)

def get_files_matching_pattern(dir_, pattern):
    files = ['{}/{}'.format(dir_, name) for name in os.listdir(dir_) if
                  re.search(string=name, pattern=pattern) is not None]
    return files

def clean_for_filenames(value):
    """
    used to clean company names to be used for file names
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = re.sub('[^./\w\s-]', '', value).strip()
    value = (re.sub('[-\s]+', '-', value))
    return value

def check_if_file_exists_if_not_print_dir(file):
    """
    check whether a file exists and if not print whats in its directory
    :param file:
    :return:
    >>> file = '../../workspace\sql\QA2.py'
    >>> check_if_file_exists_if_not_print_dir(file)
    file does not exist, looking at files in: ../../workspace/sql
    ['psql']
    """
    #import pdb; pdb.set_trace()
    if not os.path.isfile(file):
        dir_ = '/'.join(re.split('[\\\/]', file)[:-1])
        print('file does not exist, looking at files in: {}'.format(dir_))
        print(os.listdir(dir_))

def check_if_dir_exists_if_not_make_it(dir):
    clean_dir = clean_for_filenames(dir)
    if not os.path.isdir(clean_dir):
        os.makedirs(clean_dir)
    return clean_dir

def list_files_in_dir(dir):
    #https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    onlyfiles = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    return onlyfiles


def loop_dir(dir_path, types=['news', 'twitter', 'blogs', 'forums', 'instagram']):
    """
    return the list of the files we want to parse
    ass:
    - dir_path :dir_path/company/News or filepath itself
    - we only want the files in those interior dirs
    :param dir_path: dir or file
    :return: {
    """
    files = []
    if os.path.isdir(dir_path):
        walk = os.walk(dir_path)
        count_files = 0
        for p in walk:
            fpath = p[0] # path before the bottom
            if re.split('[\\\\/]*', fpath)[-1] in types:  # => these are the files we want
                count_files += 1
                files += ['{}/{}'.format(fpath, i) for i in p[-1]]  # grab all files in this bottom and prepend the path
        print('number of files that have been selected to parse: {}'.format(count_files))
        return files
    else:
        return [dir_path]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    #check_if_file_exists_if_not_print_dir('../../workspace\mods\QA2.py')