import unittest
import requests

BASE_URL = "https://api-project-for-an-airline-company.vercel.app/api/v1"


class TestAirlineAPI(unittest.TestCase):

    def setUp(self):

        login_response = requests.post(
            f"{BASE_URL}/admin/login",
            json={"username": "admin", "password": "password"},
        )
        self.assertEqual(login_response.status_code, 200)
        self.token = login_response.json()["access_token"]

        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_insert_flight(self):
        response = requests.post(
            f"{BASE_URL}/admin/insert-flight",
            json={
                "from": "Istanbul",
                "to": "Ankara",
                "availableDates": ["2024-12-01", "2024-12-05"],
                "days": ["Monday", "Friday"],
                "capacity": 100,
            },
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 201)
        print("Insert Flight: PASS")

    def test_report_flights(self):
        response = requests.get(
            f"{BASE_URL}/admin/report-flights?from=Istanbul&to=Ankara",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("flights" in response.json())
        print("Report Flights: PASS")

    def test_query_flights(self):

        response = requests.get(
            f"{BASE_URL}/client/query-flights?from=Istanbul&to=Ankara&date=2024-12-01"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("flights" in response.json())
        print("Query Flights: PASS")

    def test_buy_ticket(self):

        response = requests.post(
            f"{BASE_URL}/client/buy-ticket",
            json={
                "date": "2024-12-01",
                "from": "Istanbul",
                "to": "Ankara",
                "passengerName": "John Doe",
            },
        )
        print("Buy Ticket Response:", response.json())
        self.assertEqual(response.status_code, 201)
        print("Buy Ticket: PASS")

    def test_check_in(self):
        buy_ticket_response = requests.post(
            f"{BASE_URL}/client/buy-ticket",
            json={
                "date": "2024-12-01",
                "from": "Istanbul",
                "to": "Ankara",
                "passengerName": "Jane Doe",
            },
        )
        print("Buy Ticket Response for Check-in:", buy_ticket_response.json())
        self.assertEqual(buy_ticket_response.status_code, 201)

        ticket_id = buy_ticket_response.json().get("ticket_id")
        response = requests.post(
            f"{BASE_URL}/client/check-in", json={"ticketId": ticket_id}
        )
        print("Check-in Response:", response.json())
        self.assertEqual(response.status_code, 200)
        print("Check-in: PASS")


if __name__ == "__main__":
    unittest.main()
