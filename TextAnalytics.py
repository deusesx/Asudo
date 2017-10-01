import pandas as pd
import re
from string import punctuation
from pymystem3 import Mystem
import numpy as np

def optimal_length_calculations(df_bd: pd.DataFrame, threshold: int=11) -> pd.DataFrame:
    mystem = Mystem(entire_input=False)
    df = df_bd[~df_bd['text'].isnull()].copy()
    df['text'] = df['text'].apply(lambda x: re.sub('[^[]*\[([^]]*)\]', '', x))
    punkt_re = re.compile('[%s]' % re.escape(punctuation))
    nums = re.compile("[+-]?\d+(?:\.\d+)?")
    df['text'] = df['text'].apply(lambda x: nums.sub(' ', punkt_re.sub(' ', x)))
    length_profile = pd.DataFrame()
    length_profile['Texts'] = df.groupby('user_id')['text'].agg(lambda x: [t for t in x])
    length_profile['Lengths'] = length_profile['Texts'].apply(lambda x: [len(t.split()) for t in x])
    length_profile['Count'] = length_profile['Texts'].apply(len)
    length_profile['Mean'] = length_profile['Lengths'].apply(pd.np.mean)
    length_profile['Std'] = length_profile['Lengths'].apply(pd.np.std)
    length_profile['Median'] = length_profile['Lengths'].apply(pd.np.median)
    length_profile['Volatility'] = (length_profile['Mean'] / length_profile['Std']).fillna(0)
    length_profile['Confidence'] = (np.round((length_profile['Volatility'] / 3)
                                             .apply(lambda x: 1 - x if x < 1 else 0) * 100) * 
                                    (length_profile['Count'] >= threshold).astype(int))
    length_profile['Vocab_Len'] = (length_profile['Texts']
                              .apply(
            lambda x: [t.lower().split() for t in x if len(t) > 0 and t is not None])
                              .apply(
            lambda l: {item for sublist in l for item in sublist})
                              .apply(
            lambda x: {t for t in mystem.lemmatize(' '.join(x))})
                              .apply(len))
    length_profile['Vocab_on_Count'] = length_profile['Vocab_Len'] / length_profile['Count']
    result = length_profile[['Median', 'Confidence', 'Vocab_on_Count', 'Count']].copy()
    return result

def recalculate_optimal_length_for_user(user_id: int, df_bd: pd.DataFrame) -> list:
    dx = optimal_length_calculations(df_bd[df_bd['user_id'] == user_id])
    print(dx)
    return {'message_length_class': dx.loc[user_id]['Median'], 
            'message_length_confidence': dx.loc[user_id]['Confidence']}

def smile_rate_calsulations(df_bd: pd.DataFrame, threshold: int=7) -> pd.DataFrame:
    df = df_bd[~df_bd['text'].isnull()].copy()
    sm = re.compile('(\:\w+\:|\<[\/\\]?3|[\(\)\\\D|\*\$][\-\^]?[\:\;\=]|'
    '[\:\;\=B8][\-\^]?[3DOPp\@\$\*\\\)\(\/\|])(?=\s|[\!\.\?]|$)')
    df['sm_s'] = df['text'].apply(lambda x: re.findall(sm, x))
    df['sm_s__len'] = df['sm_s'].apply(len)
    df['hasSmile'] = (df['sm_s__len'] > 0).astype(int)
    smile_profile = pd.DataFrame(df.groupby('user_id')['hasSmile'].sum())
    smile_profile['msg_cnt'] = df.groupby('user_id')['text'].count()
    smile_profile['smile_rate'] = np.round(smile_profile['hasSmile'] / smile_profile['msg_cnt'] * 100)
    smile_profile['is_smile'] = smile_profile.apply(
        lambda x: x['smile_rate'] > 30 if x['msg_cnt'] >= threshold else None, axis=1)
    return smile_profile

def recalculate_smiles_for_user(user_id: int, df_bd: pd.DataFrame) -> list:
    dx = smile_rate_calsulations(df_bd[df_bd['user_id'] == user_id])
    print(dx)
    return {'smile_rate': dx.loc[user_id]['smile_rate'], 
            'is_smile': dx.loc[user_id]['is_smile']}

