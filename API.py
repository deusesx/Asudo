import pandas as pd
from flask import Flask, request
import json
import TextAnalytics
import datetime

DB_ADDRESS = 'postgresql://postgres@78.24.221.184:5432/asudo?user=postgres&password=demo123'
app = Flask(__name__)

@app.route('/user/<user_id>/', methods=['GET'])
def get_user(user_id):
    user_query = "SELECT * FROM profiles WHERE uid='{0}'"
    user_profile = pd.read_sql_query(user_query.format(user_id), 
                                     con=DB_ADDRESS)
    result = {}
    for col in user_profile.columns:
        t = user_profile[col].values
        if len(t) > 0:
            result[col] = t[0]
        else:
            return json.dumps({'error': 'user {0} not found'.format(user_id)}), 500
    print(result)
    return json.dumps(result), 200


@app.route('/message/', methods=['POST'])
def send_message():
    body = json.loads(request.get_data().decode('UTF-8'))
    print(body)
    user_id = (body['uid'])
    text = body['text']
    msg_dat = int(datetime.datetime.now().timestamp())
    new_msg = pd.DataFrame.from_dict({'uid': [user_id], 'text': [text], 'msg_date': [msg_dat]})
    new_msg.to_sql(name='messages', con=DB_ADDRESS, if_exists='append', index=False)
    
    user_query = "SELECT * FROM messages WHERE uid='{0}'"
    user_messages = pd.read_sql_query(user_query.format(user_id), 
                                     con=DB_ADDRESS)
    length_profile = TextAnalytics.recalculate_optimal_length_for_user(user_id, user_messages)
    smile_profile = TextAnalytics.recalculate_smiles_for_user(user_id, user_messages)
    length_profile = length_profile[['Median', 'Confidence']]
    smile_profile = smile_profile[['smile_rate', 'is_smile']]
    user_query = "SELECT * FROM profiles WHERE uid='{0}'"
    user_profile = pd.read_sql_query(user_query.format(user_id), 
                                     con=DB_ADDRESS)
    
    user_profile = user_profile.set_index('uid')
    user_profile.set_value(user_id, 'message_length_class', length_profile['Median'][user_id])
    user_profile.set_value(user_id, 'message_length_confidence', length_profile['Confidence'][user_id])
    user_profile.set_value(user_id, 'smile_rate', smile_profile['smile_rate'][user_id])
    user_profile.set_value(user_id, 'is_smile', smile_profile['is_smile'][user_id])
    user_profile = user_profile.reset_index()
    user_profile['message_length_class'] = user_profile['message_length_class'].astype(str)
    user_profile['message_length_confidence'] = user_profile['message_length_confidence'].astype(str)
    user_profile['smile_rate'] = user_profile['smile_rate'].astype(str)
    user_profile['is_smile'] = user_profile['is_smile'].astype(str)
    
    user_profile.to_sql(name='profiles', con=DB_ADDRESS, if_exists='replace', index=False)
    return json.dumps({}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='777')
