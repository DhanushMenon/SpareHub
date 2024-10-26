import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase

class SpareHubTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH
        cls.driver.implicitly_wait(10)

        # Create a test user if it doesn't exist
        User = get_user_model()
        cls.test_user, created = User.objects.get_or_create(
            username='existing_user',
            defaults={
                'password': 'testpassword123',
                'email': 'existing_user@example.com',
                'user_type': 'CUSTOMER'  # Adjust user_type as needed
            }
        )
        if created:
            cls.test_user.set_password('testpassword123')  # Set password if user was created
            cls.test_user.save()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_login(self):
        self.driver.get(f'{self.live_server_url}/login/')

        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        username_input.send_keys('existing_user')
        password_input.send_keys('testpassword123')
        password_input.submit()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Welcome')]"))
        )

        self.assertIn("Welcome", self.driver.page_source)

    # Other test methods...

if __name__ == '__main__':
    unittest.main()