import os
import mysql.connector

# MySQL database configuration
db_config = {
    'host': '31.13.202.185',
    'user': 'bookstore_user',
    'password': '308-_-803',
    'database': 'bookstore'
}


# Function to insert image into the database
def update_image(file_path, table_name, column_name, record_id):
    try:
        # Read the image file as binary data
        with open(file_path, 'rb') as file:
            image_data = file.read()

        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Prepare the SQL query
        query = f"UPDATE {table_name} SET {column_name} = %s WHERE id = %s"
        values = (image_data, record_id)

        # Execute the query
        cursor.execute(query, values)
        connection.commit()

        print(f"Success: {table_name} -> {column_name} -> {record_id}")

    except mysql.connector.Error as error:
        print(f"Failed to update image in the database: {error}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Main function to traverse the folder structure and insert images
def update_images_from_folder(root_folder):
    for table_name in os.listdir(root_folder):
        table_folder = os.path.join(root_folder, table_name)
        if os.path.isdir(table_folder):
            for column_name in os.listdir(table_folder):
                column_folder = os.path.join(table_folder, column_name)
                if os.path.isdir(column_folder):
                    for filename in os.listdir(column_folder):
                        if filename.endswith('.jpg'):
                            file_path = os.path.join(column_folder, filename)
                            record_id = os.path.splitext(filename)[0]
                            update_image(file_path, table_name, column_name, record_id)


# Call the main function with the root folder path
root_folder = 'images/'
update_images_from_folder(root_folder)
