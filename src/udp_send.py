import os
import json
import time
import pygame
from dotenv import load_dotenv
import socket

class ControllerUDPClient:
    def __init__(self, jetson_ip, jetson_port, screen_size=(800, 800)):
        self.jetson_ip = jetson_ip
        self.jetson_port = jetson_port
        self.screen_size = screen_size
        self.packet_count = 1
        self.data = [0.0] * 2
        self.setup_pygame()
        self.udp_socket = self.create_udp_socket()

    def setup_pygame(self):
        pygame.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Gamepad Input")
        self.font = pygame.font.Font(None, 36)

    def create_udp_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_data(self, data):
        data_json = json.dumps(data)
        try:
            start_time = time.perf_counter_ns()
            self.udp_socket.sendto(data_json.encode('utf-8'), (self.jetson_ip, self.jetson_port))
            end_time = time.perf_counter_ns()
            elapsed_time = end_time - start_time
            print(f"({self.packet_count}) Packet took {elapsed_time / 1000} microseconds to send")
            self.packet_count += 1
        except Exception as e:
            print(f"Error sending data: {str(e)}")

    def display_controller_info(self):
        self.screen.fill((255, 255, 255))
        # Display controller name
        name_text = self.font.render(f"Controller: {self.joystick.get_name()}", True, (0, 0, 0))
        self.screen.blit(name_text, (10, 10))

        # Display axis values
        for i in range(self.joystick.get_numaxes()):
            axis_value = round(self.joystick.get_axis(i), 2)
            axis_text = self.font.render(f"Axis {i}: {axis_value:.2f}", True, (0, 0, 0))
            self.screen.blit(axis_text, (10, 50 + i * 40))
            # Update data for UDP sending
            if i < len(self.data):
                self.data[i] = axis_value

        # Display button states
        for i in range(self.joystick.get_numbuttons()):
            button_state = self.joystick.get_button(i)
            button_text = self.font.render(f"Button {i}: {button_state}", True, (0, 0, 0))
            self.screen.blit(button_text, (10, 300 + i * 40))

        pygame.display.update()

    def run(self):
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                self.display_controller_info()
                self.send_data(self.data)
                time.sleep(0.25)
        finally:
            self.udp_socket.close()

def main():
    load_dotenv()
    jetson_ip = os.getenv('JETSON_IP')
    jetson_port = int(os.getenv('JETSON_PORT'))

    if not jetson_ip or not jetson_port:
        print("Jetson IP or port is not set. Please check your .env file.")
        return

    controller_client = ControllerUDPClient(jetson_ip, jetson_port)
    controller_client.run()

if __name__ == "__main__":
    main()
