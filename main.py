from selenium import webdriver
import time
import ipaddress
import re
import socket
import subprocess
from cls.post_mail import PostSend


def check_ping(server_ip: str) -> bool:
    """
    Check resource availability
    :return: bool: resource is available or not
    """
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
    driver = webdriver.Firefox()
    driver.get(server_ip)
    still_alive = "CRYSTALPUZZLES" in driver.title
    driver.close()

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

    server_port = input('Furnace PORT:\t')

    # Validate input for port to ensure it's a valid integer
    try:
        furnace_port = int(server_port)
    except ValueError:
        print("Invalid port number. Please enter a valid integer.")
        exit(1)  # Exit if the port is invalid

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
        f"Port number: {server_port}"
    )

    # Send the email using the post_mail utility
    try:
        email_result = post_mail.mail_send(subj=subject, message=message)
        print(f"The Start email to {customer_email} sent successfully.")
    except 'Connection error':
        print(f"Failed to send email: {customer_email}")
        exit(1)

    count_lost = 0

    while True:
        if check_ping(server_ip):
            count_lost = 0



        else:
            print("lost connection")
            count_lost += 1
            print(f'count_lost: {count_lost}')

            if count_lost < 2:
                # Compose and send the email notification
                subject = "Application: Connection Lost"
                message = (
                    f"Furnace {server_ip} has lost connection.<br>"
                )

                # Send an email notification
                email_result = post_mail.mail_send(subj=subject, message=message)
                print(email_result)
                # Change the status to offline
                server_on_line = False

        time.sleep(10)


if __name__ == '__main__':
    main()
