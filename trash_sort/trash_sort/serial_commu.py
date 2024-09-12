import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos import QoSProfile

import serial
import time
import binascii



class SerialCommu(Node):
    def __init__(self):
        super().__init__('serial_commu')
        qos_profile = QoSProfile(depth=10)
        
        self.sonar_publisher = self.create_publisher(String, "sonar_data", qos_profile)
        self.controll_subscriber = self.create_subscription(String, "cmd_val", self.send_rs485, qos_profile)
        
        
        
        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=5)


        self.sonar485_timer = self.create_timer(1/300, self.sonar_detect)
        
    def sonar_detect(self) :
        msg = String()
        
        if self.ser.in_waiting > 0:
            data = self.ser.read(self.ser.in_waiting)  # 사용 가능한 데이터만큼 읽음
            
            byte_data = bytes(data)

            hex_string = byte_data.hex()
            
            print(hex_string)
            
            msg.data = hex_string
            
            self.sonar_publisher.publish(msg)
            
        
    def send_rs485(self, msg) :
        data = msg.data
        self.ser.write(bytes([0xAF]))
        time.sleep(1)
        hex = int(data,16)
        # ser.write(hex)
        self.ser.write(hex.to_bytes(1, byteorder='big'))  # 1바이트로 변환 후 전송
        time.sleep(1)
        
        self.get_logger().info(f'send data   0XAF    0X{data}')
    
    
    
    
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