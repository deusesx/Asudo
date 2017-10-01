import pandas as pd
from flask import Flask
import json

DB_ADDRESS = 'postgresql://postgres@78.24.221.184:5432/asudo?user=postgres&password=demo123'
app = Flask(__name__)

@app.route('/user/{user_id}/', methods=['GET'])
def get_user(user_id):
    user_query = "SELECT * FROM profiles WHERE uid={0}"
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
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='777')
