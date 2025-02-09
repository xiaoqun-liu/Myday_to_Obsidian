# get folder dictionary -- local_id: name
import sqlite3
import pandas as pd
from datetime import datetime
import os

def store_db(db_path, store_path):
    if os.path.exists(db_path):
        # get date for today in the format of 'YYYY-MM-DD'
        today = datetime.today()
        formatted_today = today.strftime('%Y-%m-%d')
        # print(">",formatted_today)
        
        # connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # tables = cursor.fetchall()

        # folder name
        cursor.execute(f"SELECT * FROM task_folders;")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        df_folders = pd.DataFrame(rows, columns=columns)
        # print(df_folders.columns)
        all_folders = dict(zip(df_folders['local_id'],df_folders['name'].apply(lambda x: x.split(' ')[0])))
        # print(all_folders)
        # task name 'task_folder_local_id'
        # print(set((df_folders['local_id'],df_folders['name'])))

        # get all todos for today
        cursor.execute(f"SELECT * FROM tasks;")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        df_today = pd.DataFrame()
        for i in df['committed_date']:
            if i and i.startswith(formatted_today):
                df_today = df[df['committed_date'] == i]
        for i in df["due_date"]:
            if i and i.startswith(formatted_today):
                df_today = pd.concat([df_today, df[df['due_date'] == i]])
        # print(">",len(df_today),"todo for today")
    
        # get all subtasks for each task in df_today 
        # cursor.execute(f"SELECT * FROM steps;")
        # rows = cursor.fetchall()
        # columns = [description[0] for description in cursor.description]
        # df_subtasks = pd.DataFrame(rows, columns=columns)
        conn.close() 
    else:
        print("database not found")
        return
    
    if len(df_today):
        # if completed, add a checkmark, if not started, add a unfiled box
        # add folder name before each task and a new line after each task, add the subtasks and their status, add the body_content, add the created_datetime
        # print(df_today.columns)
        df_today = df_today[['task_folder_local_id', 'created_datetime', 'subject', 'body_content', 'status']]
        for i in df_today['task_folder_local_id']:
            df_today['task_folder_local_id'] = df_today['task_folder_local_id'].replace(i, all_folders[i])
        df_today['task_folder_local_id'] = df_today['task_folder_local_id'].apply(lambda x: x.strip())
        df_today['subject'] = df_today['subject'].apply(lambda x: x.strip())
        df_today['body_content'] = df_today['body_content'].apply(lambda x: x.replace('\n','\n\t'))
        df_today['created_datetime'] = df_today['created_datetime'].apply(lambda x: str(x).split('T')[0])
        df_today['status'] = df_today['status'].apply(lambda x: '- [x] ' if x == 'Completed' else '- [ ] ')
        
        if os.path.exists(store_path):
            with open(store_path, 'a') as f:
                f.write(f"> {len(df_today)} todos for today\n")
                for _, row in df_today.iterrows():
                    print(row['task_folder_local_id'],  row['subject'], row['created_datetime'])
                    if row['body_content']:
                        print(row['body_content'])
                    
                    f.write(f"{row['status']} {row['task_folder_local_id']} {row['subject']} -{row['created_datetime']}\n")
                    if row['body_content']:
                        f.write(f"\t{row['body_content']}\n")
                        
db_path = ''
obisidian_path = ''
today = datetime.today()
prev_md = today.strftime('%Y-%m-%d-%w')
found = False
for filename in os.listdir(obisidian_path):
    if filename.startswith(prev_md) and filename.endswith('.md'):
        found = True
        print(f"Found file: {filename}")
        store_path = os.path.join(obisidian_path, filename)
        break
if not found:
    store_path = os.path.join(obisidian_path, prev_md+'.md')
    with open(store_path, 'w') as f:
        pass # create a new file
if os.path.exists(store_path):
    store_db(db_path, store_path)
    
# launchctl load ~/Library/LaunchAgents/com.user.syn.plist
# launchctl list | grep com.user.syn
# launchctl unload ~/Library/LaunchAgents/com.user.syn.plist