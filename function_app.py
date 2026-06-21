import azure.functions as func
import logging
import json
import os
import pyodbc

app = func.FunctionApp()

@app.service_bus_queue_trigger(arg_name="msg", 
                               queue_name="incoming-payload", 
                               connection="ServiceBusConnection")
def servicebus_to_sql_trigger(msg: func.ServiceBusMessage):
    # 1. Decode the message
    body = msg.get_body().decode('utf-8')
    logging.info(f"Python ServiceBus queue trigger processed message: {body}")
    
    try:
        payload = json.loads(body)
        user_id = payload.get('userId')
        name = payload.get('name')
        action = payload.get('action')

        if not user_id or not name or not action:
            logging.error("Invalid payload format.")
            return

        # 2. Connect to SQL Database
        sql_conn_string = os.environ["SqlConnectionString"]
        
        with pyodbc.connect(sql_conn_string) as conn:
            cursor = conn.cursor()
            
            # 3. Insert into Azure SQL
            insert_query = """
                INSERT INTO dbo.UserActions (UserId, Name, Action)
                VALUES (?, ?, ?)
            """
            cursor.execute(insert_query, (user_id, name, action))
            conn.commit()
            
            logging.info(f"Successfully inserted User {name} into database.")

    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        raise e