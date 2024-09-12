import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos import QoSProfile

import serial
import time



class SerialCommu(Node):
    def __init__(self):
        super().__init__('serial_commu')
        qos_profile = QoSProfile(depth=10)
        
        self.sonar_publisher = self.create_publisher(String, "sonar_data", qos_profile)
        self.controll_subscriber = self.create_subscription(String, "cmd_vel", qos_profile, self.send_rs485)
        
        
        
        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=5)


        self.sonar485_timer = self.create_timer(1/50, self.sonar_detect)
        
    def sonar_detect(self) :
        msg = String()
        
        if self.ser.in_waiting > 0:
            msg.data = self.ser.read(self.ser.in_waiting)  # 사용 가능한 데이터만큼 읽음
            
            self.sonar_publisher.publish(msg)
            
            # 16진수로 변환하여 출력
            hex_data = msg.data.hex()  # 수신한 데이터를 16진수로 변환
            print(f"수신한 데이터 (16진수): {hex_data}")
        
        
    def send_rs485(self, msg) :
        data = msg.data
        
        hex = int(data,16)
        # ser.write(hex)
        self.ser.write(hex.to_bytes(1, byteorder='big'))  # 1바이트로 변환 후 전송
    
    
    
    
def main(args=None):
    rclpy.init(args=args)
    node = SerialCommu()
    try :
        rclpy.spin(node)
    except KeyboardInterrupt :
        node.get_logger().info('Keyboard Interrupt (SIGINT)')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()