from flask import request, jsonify
from redash.handlers.base import (
    BaseResource
)
import os
from openai import OpenAI

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI


VARIABLE_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(
  api_key=VARIABLE_KEY
)

class ChatResource(BaseResource):
    def post(self):
        try:
            value = request.get_json()
            question = value.get('question')

            """completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a redash visualization assistant, skilled in SQL queries and data visualization. You are only required to give answers for query and data visualization questions. If asked about a topic outside these two, make sure to respond that you have no information regarding that question. I am only here to help you with your query and data visualization questions. When asked to write queries, only provide the code without descriptions."},
                    {"role": "user", "content": question}
                ]
            )
            answer = completion.choices[0].message.content
            response_data = {"answer": answer}"""

            print('**************************************************************************************start chat with youtube data')
            youtube_chat = ChatWithYoutubeDatabase()
            print('**************************************************************************************getting db connection')
            _db = youtube_chat.get_db_connection(DB_URI)
            print('**************************************************************************************getting executor')
            _agent_excutor = youtube_chat.llm_connector(_db)
            print('**************************************************************************************running query')        
            query_result = youtube_chat.query_runner(question,_agent_excutor)
            print('**************************************************************************************query result')      
            print(query_result)
            print('**************************************************************************************done')    
            return jsonify(query_result), 200
            #return jsonify(response_data), 200
        
        except Exception as error:
            print(error)
            return jsonify({"error": "An error occurred"}), 500
    
        
class ChatWithYoutubeDatabase():
    def get_db_connection(db_uri):
        try:
            db = SQLDatabase.from_uri(db_uri)
            print(db.dialect)
            print(db.get_usable_table_names())
            return db
        except Exception as e:
            print(e)
    
    def llm_connector(db):
        try:
            llm = ChatOpenAI(model='gpt-3.5-turbo',temperature=0)
            agent_executor = create_sql_agent(llm,db=db,agent_type="openai-tools",verbose=True)
            return agent_executor
        except Exception as e:
            print(e)
    
    def query_runner(query,agent_executor):
        try:
            result = agent_executor.invoke(query)
            return result
        except Exception as e:
            print(e)