from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient


class ChatDB:
    def __init__(self, uri="mongodb://mongodb:27017/", db_name="chat_db"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db.messages

    def read_all(self):
        return self.collection.find()

    def open(self):
        self.client.open()

    def close(self):
        self.client.close()

    def create(self, post):
        return self.collection.insert_one(post)

    def update(self, pk, date, username, message):
        new_post = {"date": date, "username": username, "message": message}
        return self.collection.update_one({"_id": ObjectId(pk)}, {"$set": new_post})

    def delete(self, pk):
        return self.collection.delete_one({"_id": ObjectId(pk)})

    def delete_by_name(self, username):
        return self.collection.delete_one({"username": username})

    def delete_all(self):
        return self.collection.delete_many({})

    def add_features(self, username, messages):
        return self.collection.update_one({"username": username}, {"$push": {"message": {"$each": messages}}})

    def read_by_name(self, username):
        document = self.collection.find_one({"username": username})
        if document:
            print(document)
        else:
            print("Not found")


if __name__ == "__main__":
    # Example usage:
    chat_db = ChatDB()

    # Reading all records
    for record in chat_db.read_all():
        print(record)

    # Creating a new record
    chat_db.create("2023-12-31", "John", "Hello!")

    # Updating a record
    chat_db.update("<your_object_id>", "2023-12-31", "John", "Updated message")

    # Deleting a record
    chat_db.delete("<your_object_id>")

    # Deleting by username
    chat_db.delete_by_name("John")

    # Deleting all records
    chat_db.delete_all()

    # Adding features
    chat_db.add_features("John", ["Feature 1", "Feature 2"])

    # Reading by username
    chat_db.read_by_name("John")
