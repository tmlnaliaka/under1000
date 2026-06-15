import time
from datetime import datetime
from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def browse_products(self):
        self.client.get("/api/products", name="GET /api/products")

    @task(2)
    def search_products(self):
        self.client.get("/api/products?search=jacket", name="GET /api/products?search=jacket")

    @task(1)
    def health_check(self):
        self.client.get("/api/health", name="GET /api/health")

    @task(1)
    def filter_by_category(self):
        self.client.get("/api/products?category=Shoes", name="GET /api/products?category=Shoes")
