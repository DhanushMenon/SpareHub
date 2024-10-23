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
        # Set up the WebDriver (e.g., Chrome)
        cls.driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH
        cls.driver.implicitly_wait(10)

        # Create a test user
        User = get_user_model()
        cls.test_user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com',
            user_type='CUSTOMER'  # Adjust user_type as needed
        )

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_login(self):
        # Navigate to the login page
        self.driver.get(f'{self.live_server_url}/login/')

        # Find and fill in the login form
        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')
        password_input.submit()

        # Wait for the page to load and check for a successful login
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Welcome')]"))
        )

        # Check if the login was successful
        self.assertIn("Welcome", self.driver.page_source)

    def test_user_registration(self):
        # Navigate to the registration page
        self.driver.get(f'{self.live_server_url}/register/')

        # Fill out the registration form
        self.driver.find_element(By.NAME, "username").send_keys("newuser")
        self.driver.find_element(By.NAME, "email").send_keys("newuser@example.com")
        self.driver.find_element(By.NAME, "password1").send_keys("newuserpassword123")
        self.driver.find_element(By.NAME, "password2").send_keys("newuserpassword123")

        # Submit the form
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Register')]").click()

        # Check if registration was successful
        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        self.assertIn("Registration successful", success_message.text)

    def test_product_search(self):
        # Navigate to the home page
        self.driver.get(self.live_server_url)

        # Find the search input and enter a query
        search_input = self.driver.find_element(By.NAME, "q")
        search_input.send_keys("brake pad")
        search_input.send_keys(Keys.RETURN)

        # Wait for search results to load
        results = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product-item"))
        )

        # Check if search results are displayed
        self.assertTrue(len(results) > 0, "No search results found")

        # Check if the search query is in the first result's title
        first_result_title = results[0].find_element(By.CLASS_NAME, "product-title").text
        self.assertIn("brake pad", first_result_title.lower())

    def test_order_product(self):
        # Log in first
        self.test_login()

        # Search for a product
        search_input = self.driver.find_element(By.NAME, "q")
        search_input.send_keys("oil filter")
        search_input.send_keys(Keys.RETURN)

        # Click on the first product in search results
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "product-item"))
        ).click()

        # Add the product to cart
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add to Cart')]"))
        ).click()

        # Go to cart
        self.driver.find_element(By.LINK_TEXT, "Cart").click()

        # Proceed to checkout
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Proceed to Checkout')]"))
        ).click()

        # Fill out shipping information
        self.driver.find_element(By.NAME, "address").send_keys("123 Test St")
        self.driver.find_element(By.NAME, "city").send_keys("Test City")
        self.driver.find_element(By.NAME, "state").send_keys("Test State")
        self.driver.find_element(By.NAME, "zip_code").send_keys("12345")

        # Place order
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Place Order')]").click()

        # Check if order was successful
        order_confirmation = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "order-confirmation"))
        )
        self.assertIn("Your order has been placed successfully", order_confirmation.text)

if __name__ == '__main__':
    unittest.main()