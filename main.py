from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

import time
import ipaddress
import re

import subprocess
from cls.post_mail import PostSend


def check_ping(server_ip: str) -> bool:
    """
    Check resource availability
    :return: bool: resource is available or not
    """
    print("Ping the host IP.")

    try:
        response = subprocess.check_output(
            f"ping -n 1 {server_ip}",
            shell=True).decode("cp866")

        if "TTL" in response:
            print(f'resource {server_ip} is available,')
            return True
        else:
            print(f'resource {server_ip} + is unavailable')
            return False

    except subprocess.CalledProcessError:
        print(f'{server_ip} - Ping command failed.')
        return False
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
        return False


def check_app(server_ip: str) -> bool:
    """
    Check the application header
    :return: bool: application send a right web page header
    """
    print("Check the application.")

    options = Options()
    options.add_argument('--headless')
    service = Service()

    try:
        with webdriver.Firefox(service=service, options=options) as driver:
            try:
                driver.get(server_ip)

                # Wait for the application response.
                WebDriverWait(driver, 10).until(
                    EC.title_contains("CRYSTALPUZZLES")
                )
                still_alive = True
                print("App is adequate.")
            except TimeoutException:
                print("The response time is over.")
                still_alive = False
            except WebDriverException as e:
                print(f"Error WebDriver: {e}")
                still_alive = False
    except Exception as e:
        print(f"Error of server access: {e}")
        still_alive = False

    return still_alive


def main():
    # To input server_ip
    server_ip = input('\nInput the application host IP:\t')
    # Try to validate the input as an IPv4 address
    try:
        ipaddress.ip_address(server_ip)  # Checks if it's a valid IP address
    except ValueError:
        print("Invalid IP address. Please enter a correct IP address.")
        exit(1)  # Exit if the IP is invalid

    customer_email = input('Please input your e-mail:\t')

    # Check if the email format is valid (simple regex check)
    email_pattern = r"[^@]+@[^@]+\.[a-zA-Z]{2,}"
    if not re.match(email_pattern, customer_email):
        print("Invalid email format. Please enter a valid email address.")
        exit(1)  # Exit if the email is invalid

    print()  # Adding space for readability in the console

    post_mail = PostSend(send_to=customer_email)

    # Compose the email subject and message
    subject = 'Start of the Program'
    message = (
        f"Start of the application monitoring program.<br>"
        f"Site IP: {server_ip}\n"
    )

    # Send the email using the post_mail utility
    try:
        email_result = post_mail.mail_send(subj=subject, message=message)
        print(f"The Start email to {customer_email} sent successfully.")
    except 'Connection error':
        print(f"Failed to send email: {customer_email}")
        exit(1)

    count_lost = 0
    server_on_line = False

    while True:
        if check_ping(server_ip) and check_app(f'http://{server_ip}'):
            count_lost = 0

            if not server_on_line:
                # Compose and send the email notification
                subject = "Server: online"
                message = (
                    f"Server {server_ip} online."
                )

                # Send an email notification
                email_result = post_mail.mail_send(subj=subject, message=message)
                print(email_result)
                # Change the status to offline
                server_on_line = True

        else:
            print("Add is down")
            count_lost += 1
            print(f'count_lost: {count_lost}')

            if count_lost < 2:
                # Compose and send the email notification
                subject = "Application: App Lost"
                message = (
                    f"Server {server_ip} is not respond.<br>"
                )

                # Send an email notification
                email_result = post_mail.mail_send(subj=subject, message=message)
                print(email_result)
                # Change the status to offline
                server_on_line = False

        time.sleep(10)


if __name__ == '__main__':
    main()
