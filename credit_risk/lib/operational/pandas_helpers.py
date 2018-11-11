import pandas as pd
import numpy as np


def select_rows_w_col_in_list(df, col, _list):
    df['{}_in_list'.format(col)] = [df.loc[i, col] in _list for i in df.index]
    return df[df['{}_in_list'.format(col)]]


def convert_from_multindex(df1):
    df = pd.DataFrame([])
    cols = df1.columns
    for c in cols:
        nc = [sub_col for sub_col in c if len(sub_col) > 0]
        new_col = '_'.join(nc)
        df[new_col] = df1[c]
    return df


def convert_json_column_to_new_df(col, output_keys):
    try:
        df_dic = {k:[] for k in output_keys}
        for dic in col:
            for key in output_keys:
                if key in dic:
                    df_dic[key].append(dic[key])
                else:
                    df_dic[key].append(np.nan)
        return pd.DataFrame.from_dict(df_dic)
    except Exception as error:
        print(error)
        import ipdb; ipdb.set_trace()
