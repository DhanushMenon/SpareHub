# sparehub/spares/tests.py
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase

class LoginTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up the WebDriver (e.g., Chrome)
        cls.driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH

        # Create a test user
        User = get_user_model()
        cls.test_user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            user_type='CUSTOMER'  # Adjust user_type as needed
        )

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_login(self):
        # Navigate to the login page
        self.driver.get(f'{self.live_server_url}/login/')  # Updated URL to match your configuration

        # Wait for the username input to be present
        username_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))  # Adjust if necessary
        )
        
        # Find the password field
        password_input = self.driver.find_element(By.NAME, 'password')

        # Enter credentials
        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')

        # Submit the form
        password_input.submit()

        # Wait for the page to load and check for a successful login
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Welcome')]"))  # Adjust based on your dashboard
        )

        # Check if the login was successful by looking for a specific element on the redirected page
        self.assertIn("Welcome", self.driver.page_source)  # Adjust the condition based on your dashboard

if __name__ == '__main__':
    unittest.main()
