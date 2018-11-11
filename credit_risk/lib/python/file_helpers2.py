
import re

def read(encoding, fpath, replace = None):

    if replace is None:
        with open(fpath, 'r', encoding=encoding, errors = "surrogateescape") as f:
            txt = f.read()
        return txt
    else:
        with open(fpath, 'r', encoding=encoding, errors = "replace") as f:
            txt = f.read()
        return txt

def try_to_read_file(fpath, save_error_path = None):
    """
    try to open fpath under different encodings and see if any works
    if not just skip it and report it
    :param fpath:
    :return:
    """

    try:
        return read('utf8', fpath)
    except Exception as error:
        print(error)
        try:
            return read('latin-1', fpath)
        except Exception as error:
            print(error)
            try:
                return read('utf8', fpath, replace = True)
            except Exception as error:
                print(error)
                print('skipping file')
                with open(save_error_path, 'a') as f:
                    f.write('file: {}, error: {}'.format(fpath, error))


def encode_cols(df, cols, encoding='utf-8', ignore_errors=True):
    df1 = df.copy()
    for col in cols:
        if ignore_errors:
            df1[col] = [i.encode(encoding, 'ignore') for i in df1[col]]
        else:
            df1[col] = [i.encode(encoding) for i in df1[col]]
    return df1

def clean_for_filenames(value):
    """
    used to clean company names to be used for file names
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = re.sub('[^\w\s-]', '', value).strip()
    value = (re.sub('[-\s]+', '-', value))
    return value

# def load_dump_pickle
