import os
import mysql.connector

# MySQL database configuration
db_config = {
    'host': '31.13.202.185',
    'user': 'bookstore_user',
    'password': '308-_-803',
    'database': 'bookstore'
}


def connect_to_database():
    try:
        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(**db_config)
        return connection

    except mysql.connector.Error as error:
        print(f"Failed to connect to the database: {error}")


# Function to search and rename files
def rename_files_in_folder(folder_path, table_name, column_name):
    # Connect to the database
    connection = connect_to_database()
    if connection is None:
        return

    try:
        cursor = connection.cursor()

        # Iterate through the files in the folder
        for filename in os.listdir(folder_path):
            if filename.endswith('.jpg'):
                file_path = os.path.join(folder_path, filename)

                # Strip the file extension to get the name
                name = os.path.splitext(filename)[0]

                # Find the corresponding ID in the specified table and column
                query = f"SELECT id FROM {table_name} WHERE {column_name} = %s"
                values = (name,)
                cursor.execute(query, values)
                row = cursor.fetchone()

                if row is not None:
                    record_id = row[0]

                    # Rename the local file to <id>.jpg
                    new_file_path = os.path.join(folder_path, f"{record_id}.jpg")
                    os.rename(file_path, new_file_path)

                    print(f"File '{filename}' renamed to '{record_id}.jpg'")

    except mysql.connector.Error as error:
        print(f"Failed to retrieve data from the database: {error}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Call the function with the folder path and table name
folder_path = 'images/book/cover'
table_name = 'book'
column_name = 'title'
rename_files_in_folder(folder_path, table_name, column_name)
