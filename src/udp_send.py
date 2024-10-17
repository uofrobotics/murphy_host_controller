import os
import json
import time
import pygame
from dotenv import load_dotenv
import socket

class ControllerUDPClient:
    def __init__(self, jetson_ip, jetson_port, screen_size=(800, 600), max_feed_items=10):
        self.jetson_ip = jetson_ip
        self.jetson_port = jetson_port
        self.screen_size = screen_size
        self.packet_count = 1
        self.data = [0.0] * 2
        self.sending_packets = False  # State for sending packets
        self.packet_feed = []  # List to keep recent packet data
        self.max_feed_items = max_feed_items
        self.setup_pygame()
        self.udp_socket = self.create_udp_socket()

    def setup_pygame(self):
        pygame.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("UDP Stream GUI")
        self.font = pygame.font.Font(None, 28)
        self.bg_color = (230, 230, 230)  # Light gray background
        self.border_color = (50, 50, 50)  # Dark gray for borders

        # Button properties
        self.button_rect = pygame.Rect(20, 500, 200, 50)
        self.button_color = (0, 255, 0)  # Green for start
        self.button_text = "Start Sending"

    def create_udp_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def toggle_sending(self):
        self.sending_packets = not self.sending_packets
        # Update button color and text based on state
        if self.sending_packets:
            self.button_color = (255, 0, 0)  # Red for stop
            self.button_text = "Stop Sending"
        else:
            self.button_color = (0, 255, 0)  # Green for start
            self.button_text = "Start Sending"

    def send_data(self, data):
        if not self.sending_packets:
            return  # Skip sending if not in sending state

        data_json = json.dumps(data)
        try:
            start_time = time.perf_counter_ns()
            self.udp_socket.sendto(data_json.encode('utf-8'), (self.jetson_ip, self.jetson_port))
            end_time = time.perf_counter_ns()
            elapsed_time = end_time - start_time
            print(f"({self.packet_count}) Packet took {elapsed_time / 1000} microseconds to send")
            
            # Add packet to the feed
            self.add_to_packet_feed(f"Packet {self.packet_count}: {data_json}")

            self.packet_count += 1
        except Exception as e:
            print(f"Error sending data: {str(e)}")

    def add_to_packet_feed(self, packet_info):
        # Add the new packet info to the top of the feed
        self.packet_feed.insert(0, packet_info)
        # Keep the feed within the max number of items
        if len(self.packet_feed) > self.max_feed_items:
            self.packet_feed.pop()

    def display_controller_info(self):
        self.screen.fill(self.bg_color)

        # Display a border around the axes display area
        axes_area = pygame.Rect(20, 20, 360, 320)
        pygame.draw.rect(self.screen, self.border_color, axes_area, 2)

        # Display axes values within the bordered area
        for i in range(self.joystick.get_numaxes()):
            axis_value = round(self.joystick.get_axis(i), 2)
            axis_text = self.font.render(f"Axis {i}: {axis_value:.2f}", True, (0, 0, 0))
            self.screen.blit(axis_text, (30, 30 + i * 40))

            # Update data for UDP sending
            if i < len(self.data):
                self.data[i] = axis_value

        # Display a border around the status area
        status_area = pygame.Rect(20, 360, 360, 60)
        pygame.draw.rect(self.screen, self.border_color, status_area, 2)

        # Display sending status within the bordered area
        status_text = "Sending Packets" if self.sending_packets else "Not Sending Packets"
        status_color = (0, 128, 0) if self.sending_packets else (128, 0, 0)
        status_rendered = self.font.render(status_text, True, status_color)
        self.screen.blit(status_rendered, (30, 370))

        # Draw the start/stop button
        pygame.draw.rect(self.screen, self.button_color, self.button_rect)
        button_text_rendered = self.font.render(self.button_text, True, (255, 255, 255))
        self.screen.blit(button_text_rendered, (self.button_rect.x + 10, self.button_rect.y + 10))

        # Display packet feed
        self.display_packet_feed()

        pygame.display.update()

    def display_packet_feed(self):
        # Display a border around the packet feed area
        feed_area = pygame.Rect(400, 20, 380, 320)
        pygame.draw.rect(self.screen, self.border_color, feed_area, 2)

        # Display recent packets within the bordered area
        for index, packet in enumerate(self.packet_feed):
            packet_text = self.font.render(packet, True, (0, 0, 0))
            self.screen.blit(packet_text, (410, 30 + index * 30))

    def run(self):
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.KEYDOWN:
                        # Check for Escape key to close the program
                        if event.key == pygame.K_ESCAPE:
                            print("Exiting program...")
                            pygame.quit()
                            return
                        # Check for Space key to start/stop sending packets
                        elif event.key == pygame.K_SPACE:
                            self.toggle_sending()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Check if the button was clicked
                        if self.button_rect.collidepoint(event.pos):
                            self.toggle_sending()

                self.display_controller_info()
                self.send_data(self.data)
                time.sleep(0.25)
        except KeyboardInterrupt:
            print("Keyboard interrupt received. Exiting...")
        finally:
            self.udp_socket.close()
            pygame.quit()


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
