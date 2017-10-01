import pandas as pd
from flask import Flask

DB_ADDRESS = 'postgresql://postgres@78.24.221.184:5432/asudo?user=postgres&password=demo123'
app = Flask(__name__)

@app.route('/user/{user_id}/', methods=['GET'])
def get_user(user_id):
    user_query = "SELECT * FROM profiles WHERE user_id='{0}'"
    try:
        user_profile = pd.read_sql_query(user_query.format(user_id), 
                                     con=DB_ADDRESS)
        result = {}
        for col in user_profile.columns:
            result[col] = user_profile[col].values[0]
        return json.dumps(result), 200
    except:
        return 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='777')
