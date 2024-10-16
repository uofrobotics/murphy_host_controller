import os
import json
import time
import pygame
from dotenv import load_dotenv
import socket

load_dotenv()
# Initialize Pygame
pygame.init()

# Initialize controller/joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()
data = [0.0] * 2
packet_count = 1

screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Gamepad Input")

font = pygame.font.Font(None, 36)

# JETSON NANO IP ADDRESS + PORT
jetson_ip = os.getenv('JETSON_IP')
jetson_port = int(os.getenv('JETSON_PORT'))

# Create a UDP socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill((255, 255, 255))

        # Display the controller name
        name_text = font.render(f"Controller: {joystick.get_name()}", True, (0, 0, 0))
        screen.blit(name_text, (10, 10))

                # Display the joystick values
        for i in range(joystick.get_numaxes()):
            axis_value = round(joystick.get_axis(i), 2)
            axis_text = font.render(f"Axis {i}: {axis_value:.2f}", True, (0, 0, 0))
            screen.blit(axis_text, (10, 50 + i * 40))

            # Send gamepad input data to the Jetson Nano
            
            if (i == 0 or i == 1):
                data[i] = axis_value
                
            # if i < len(data):  
            #    data[i] = axis_value
            # else:
            #     # Handle an index error if the joystick has more axes than expected
            #     print(f"Index {i} is out of range for the data array")

        data_json = json.dumps(data)
        
        try:
            # Send the data over UDP
            start_time = time.perf_counter_ns()
            udp_socket.sendto(data_json.encode('utf-8'), (jetson_ip, jetson_port))
            end_time = time.perf_counter_ns()
            elapsed_time = end_time - start_time
            print(f"({ packet_count }) Packet took {elapsed_time / 1000} milliseconds to send")
            packet_count += 1
        except Exception as e:
            print(f"Error sending data: {str(e)}")
            

        # Display the button states
        for i in range(joystick.get_numbuttons()):
            button_state = joystick.get_button(i)
            button_text = font.render(f"Button {i}: {button_state}", True, (0, 0, 0))
            screen.blit(button_text, (10, 300 + i * 40))

        pygame.display.update()
        time.sleep(0.5)





