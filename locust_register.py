from locust import HttpLocust, TaskSet, task
import json
import random


class UserBehaviour(TaskSet):

    @task
    def land(self):
        r = self.client.get("/")

    @task
    def post_signup(self):
        r = self.client.get("/signup/", name="get_signup")
        csrftoken = r.cookies['csrftoken']

        x = random.randrange(10000)
        email = 'rocky{}@example.com'.format(x)

        data = {
            'email': email,
            'email_repeat': email,
            'first_name': emial,
            'last_name': 'Balboa',
            'dance_role': 'leader',
            'pass_type': (x % 4)
            }

        headers = {"X-CSRFToken": csrftoken}
        r = self.client.post("/signup/", headers=headers,
                data=data, name="post_signup")


class WebsiteUser(HttpLocust):
    task_set = UserBehaviour
    min_wait = 500 # milli
    max_wait = 1000 # milli
