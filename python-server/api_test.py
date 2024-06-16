import unittest
from fastapi.testclient import TestClient
from api import app
import json

client = TestClient(app)

class TestAPI(unittest.TestCase):
    def test_index_exists(self):
        self.assertEqual(client.get("/").status_code, 200)

class TestChats(unittest.TestCase):
    def test_invalid_params(self):
        self.assertEqual(client.get("chats").status_code, 422)

    def test_valid_params(self):
        response_json = client.get("chats", params={"uid": 1})
        self.assertEqual(response_json.status_code, 200)
        response = json.loads(response_json.json())
        self.assertIsInstance(response, dict)

    def test_correct_structure(self):
        response_json = client.get("chats", params={"uid": 1})
        response = json.loads(response_json.json())

        self.assertIn("uid", response)
        self.assertIn("chat_ids", response)

    def test_chats_correct_structure(self):
        response_json = client.get("chats", params={"uid": 1})
        response = json.loads(response_json.json())

        self.assertIsInstance(response['chat_ids'], list)

class TestMessages(unittest.TestCase):
    def test_invalid_params(self):
        self.assertEqual(client.get("messages").status_code, 422)

    def test_valid_params(self):
        response_json = client.get("messages", params={"chat_id": 1})
        self.assertEqual(response_json.status_code, 200)
        response = json.loads(response_json.json())
        self.assertIsInstance(response, dict)

    def test_correct_structure(self):
        response_json = client.get("messages", params={"chat_id": 1})
        response = json.loads(response_json.json())

        self.assertIn("chat_id", response)
        self.assertIn("messages", response)

        self.assertIsInstance(response['messages'], list)

    def test_messages_correct_structure(self):
        response_json = client.get("messages", params={"chat_id": 1})
        response = json.loads(response_json.json())

        message = response['messages'][0]

        self.assertIn("id", message)
        self.assertIn("role", message)
        self.assertIn("content", message)


if __name__ == '__main__':
    unittest.main()