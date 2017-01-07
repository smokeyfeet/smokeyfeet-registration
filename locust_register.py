from locust import HttpLocust, TaskSet, task
import random


class UserBehaviour(TaskSet):

    @task
    def get_signup(self):
        self.client.get("/")

    @task
    def post_signup(self):
        r = self.client.get("/", name="get_signup")
        csrftoken = r.cookies["csrftoken"]

        x = random.randrange(10000)
        email = "rocky{}@example.com".format(x)

        data = {
            "csrfmiddlewaretoken": csrftoken,
            "first_name": email,
            "last_name": "Balboa",
            "email": email,
            "email_repeat": email,
            "residing_country": "NL",
            "dance_role": "leader",
            "pass_type": (x % 5),
            "workshop_partner_name": "",
            "workshop_partner_email": "",
            "lunch": 3,
            "agree_to_terms": "on"
            }

        headers = {"X-CSRFToken": csrftoken}
        r = self.client.post(
                "/", headers=headers, data=data, name="post_signup")


class WebsiteUser(HttpLocust):
    task_set = UserBehaviour
    min_wait = 500  # milli
    max_wait = 1000  # milli
