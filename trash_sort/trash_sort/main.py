import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np
from ultralytics import YOLO
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class TrashSort(Node):
    def __init__(self):
        super().__init__('trash_sort')
        self.bridge = CvBridge()
        self.model = YOLO('/home/skh/testing_folder/trash_sort/deneme-3/runs/detect/train3/weights/best.pt')  #lattepanda

        img_qos_profile = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, history=HistoryPolicy.KEEP_LAST, depth=1  )
        qos_profile = QoSProfile(depth = 10)
        
        self.img_publisher = self.create_publisher(Image,'side_camera',img_qos_profile)
        self.controll_publisher = self.create_publisher(String,'cmd_val',qos_profile)
        
        self.sonar_subscriber = self.create_subscription(String, 'sonar_data', self.waste_full_checker,qos_profile)
        
        ### camera parameter setting ###
        self.img_size_x = 640
        self.img_size_y = 480

        self.frame_rate = 10
        ##################################
        
        #### algorithm parameter ####
        self.glass_waste_ROI = [[int(self.img_size_x * 0.2), int(self.img_size_y * 0.7)],[int(self.img_size_x * 0.4), int(self.img_size_y * 0.95)]]
        self.plastic_waste_ROI = [[int(self.img_size_x * 0.2), int(self.img_size_y * 0.4)],[int(self.img_size_x * 0.4), int(self.img_size_y * 0.65)]]
        self.general_waste_ROI = [[int(self.img_size_x * 0.2), int(self.img_size_y * 0.1)],[int(self.img_size_x * 0.4), int(self.img_size_y * 0.35)]]
        
        # self.postbox_ROI = [[int(self.img_size_x * 0.4), int(self.img_size_y * 0.65)],[int(self.img_size_x * 0.5), int(self.img_size_y * 0.75)]]## xy xy
        
        ##################################
        
        self.cap0 = cv2.VideoCapture('/dev/video4')  #cam0
        self.cvbrid = CvBridge()
        
        self.cap0.set(cv2.CAP_PROP_FRAME_WIDTH, self.img_size_x)
        self.cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, self.img_size_y)
        self.cap0.set(cv2.CAP_PROP_FPS, self.frame_rate)
        
        self.image_cap_timer = self.create_timer(1/self.frame_rate, self.img_cap)
        self.img_timer = self.create_timer(1/self.frame_rate, self.image_callback)
        self.full_checker_timer = self.create_timer(1/5, self.flag_falser)
        
        self.publish_flag_timer = self.create_timer(1, self.pub_flag_checker)
        
        self.color_img = np.zeros((self.img_size_y, self.img_size_x, 3), dtype=np.uint8)
        
        
        self.full_flag_general = False
        self.full_flag_plastic = False
        self.full_flag_glass = False
        self.full_cnt_general = 0
        self.full_cnt_plastic = 0
        self.full_cnt_glass = 0
        
        self.general_pub_flag = False
        self.plastic_pub_flag = False
        self.glass_pub_flag = False
        self.general_pub_flag_cnt = 0
        self.plastic_pub_flag_cnt = 0
        self.glass_pub_flag_cnt = 0
        
        
        self.get_logger().info(f"General waste ROI: {self.general_waste_ROI}")
        self.get_logger().info(f"Plastic waste ROI: {self.plastic_waste_ROI}")
        self.get_logger().info(f"Glass waste ROI: {self.glass_waste_ROI}")

    def img_cap(self) :
        ret0, frame = self.cap0.read()
        
        if not (ret0) :
            if not ret0 :
                self.get_logger().info(f'cam0 is cannot connetion')
        else :
            self.color_img = frame
            
    def flag_falser(self) :
        if self.full_flag_general == True :
            self.full_cnt_general += 1
            if self.full_cnt_general >= 10 :
                self.full_flag_general = False
                
        elif self.full_flag_plastic == True :
            self.full_cnt_plastic += 1
            if self.full_cnt_plastic >= 10 :
                self.full_flag_platic = False
                
        elif self.full_flag_glass == True :
            self.full_cnt_glass += 1
            if self.full_cnt_glass>= 10 :
                self.full_flag_glass = False
        
        
        
            
    def waste_full_checker(self , msg) :
        if msg.data == "ca" :
            self.full_flag_general = True
            self.full_cnt_general = 0
        elif msg.data == "cb" :
            self.full_flag_plastic = True
            self.full_cnt_plastic = 0
        elif msg.data == "cc" :
            self.full_flag_glass = True
            self.full_cnt_glass = 0
            
    def pub_flag_checker(self) :
        self.general_pub_flag = False
        self.plastic_pub_flag = False
        self.glass_pub_flag = False
        
        if self.general_pub_flag == True :
            self.general_pub_flag_cnt += 1
            if self.general_pub_flag_cnt >= 5 :
                self.general_pub_flag = False
        
        
        if self.plastic_pub_flag == True :
            self.plastic_pub_flag_cnt += 1
            if self.plastic_pub_flag_cnt >= 5 :
                self.plastic_pub_flag = False
                
        
        if self.glass_pub_flag == True :
            self.glass_pub_flag_cnt += 1
            if self.glass_pub_flag_cnt >= 5 :
                self.glass_pub_flag = False
        
        # self.general_pub_flag = False
        # self.plastic_pub_flag = False
        # self.glass_pub_flag = False
        # self.general_pub_flag_cnt = 0
        # self.plastic_pub_flag_cnt = 0
        # self.glass_pub_flag_cnt = 0
        
        return 
        
    def image_callback(self):
        
        result = self.model.predict(self.color_img, conf = 0.4, verbose=False)
        
        cv2.rectangle(self.color_img, (int(self.general_waste_ROI[0][0]),int(self.general_waste_ROI[0][1])), ((int(self.general_waste_ROI[1][0]), int(self.general_waste_ROI[1][1]))), (255,0,0),2)
        cv2.putText(self.color_img, "general_waste",(int(self.general_waste_ROI[0][0]), int(self.general_waste_ROI[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        
        cv2.rectangle(self.color_img, (int(self.plastic_waste_ROI[0][0]),int(self.plastic_waste_ROI[0][1])), ((int(self.plastic_waste_ROI[1][0]), int(self.plastic_waste_ROI[1][1]))), (0,255,0),2)
        cv2.putText(self.color_img, "plastic_waste", (int(self.plastic_waste_ROI[0][0]), int(self.plastic_waste_ROI[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.rectangle(self.color_img, (int(self.glass_waste_ROI[0][0]),int(self.glass_waste_ROI[0][1])), ((int(self.glass_waste_ROI[1][0]), int(self.glass_waste_ROI[1][1]))), (0,0,255),2)
        cv2.putText(self.color_img, "glass_waste", (int(self.glass_waste_ROI[0][0]), int(self.glass_waste_ROI[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        
        
        if self.full_flag_general == True :
            cv2.putText(self.color_img, "general_waste is full", (int(self.general_waste_ROI[1][0]) + 10, int(self.general_waste_ROI[1][1])),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)  # 빨간색 텍스트 추가
        if self.full_flag_plastic == True :
            cv2.putText(self.color_img, "plastic_waste is full", (int(self.plastic_waste_ROI[1][0]) + 10, int(self.plastic_waste_ROI[1][1])),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)  # 빨간색 텍스트 추가
        if self.full_flag_glass == True :
            cv2.putText(self.color_img, "glass_waste is full", (int(self.glass_waste_ROI[1][0]) + 10, int(self.glass_waste_ROI[1][1])),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)  # 빨간색 텍스트 추가
        
        
        annotated = result[0].plot()
                
        # 탐지된 객체가 있는지 확인
        if len(result[0].boxes) > 0:
            for i, box in enumerate(result[0].boxes):
                # 각 객체의 위치 좌표 (xywh) 가져오기
                trash_locate = np.array(box.xywh.detach().numpy(), dtype='int')

                # 객체 클래스 및 정확도 가져오기
                class_id = int(box.cls)  # 클래스 ID
                confidence = box.conf.item()  # 정확도

                self.get_logger().info(f"Object {i}: Class ID: {class_id}, Confidence: {confidence:.2f}, Location (x, y, w, h): {trash_locate}")
                

                # if trash_locate.shape[0] >= 2:  # 최소한 x와 y 좌표가 있는지 확인
                # 객체의 (x, y) 좌표 가져오기
                object_x, object_y = trash_locate[0][0], trash_locate[0][1]
                if class_id == 1:
                    if self.glass_waste_ROI[0][0] <= object_x <= self.glass_waste_ROI[1][0] and self.glass_waste_ROI[0][1] <= object_y <= self.glass_waste_ROI[1][1]:
                        msg = String()
                        msg.data = "aa"
                        if self.glass_pub_flag == False :
                            self.controll_publisher.publish(msg)
                            self.glass_pub_flag = True
                            self.get_logger().info("Glass detected in ROI, published 'aa'")
                        else :
                            self.get_logger().info("waiting")

                if class_id == 3:
                    if self.plastic_waste_ROI[0][0] <= object_x <= self.plastic_waste_ROI[1][0] and self.plastic_waste_ROI[0][1] <= object_y <= self.plastic_waste_ROI[1][1]:
                        msg = String()
                        msg.data = "ab"
                        if self.plastic_pub_flag == False :
                            self.controll_publisher.publish(msg)
                            self.get_logger().info("Plastic detected in ROI, published 'ab'")
                        else :
                            self.get_logger().info("waiting")

                if class_id == 2:
                    if self.general_waste_ROI[0][0] <= object_x <= self.general_waste_ROI[1][0] and self.general_waste_ROI[0][1] <= object_y <= self.general_waste_ROI[1][1]:
                        msg = String()
                        msg.data = "ac"
                        if self.general_pub_flag == False :
                            self.controll_publisher.publish(msg)
                            self.get_logger().info("Metal detected in ROI, published 'ac'")
                        else :
                            self.get_logger().info("waiting")
            
        # if len(result[0].boxes.cls) :
        #     for box in result[0].boxes :
        #         label = box.cls
        #         confidence = box.conf.item()
        #         object_xyxy = np.array(box.xyxy.detach().numpy().tolist()[0], dtype='int')
        #         color = [255,255,255]
        #         if label == 0 :
        #             color =[0,255,0]
        #             cv2.putText(frame, f'Korea ARMY  {(confidence*100):.2f}%', (object_xyxy[0], object_xyxy[1] - 20),cv2.FONT_ITALIC, 1, (0, 255, 0), 2)
        #         else :
        #             color = [0,0,255]
        #             cv2.putText(frame, f'ENEMY  {(confidence*100):.2f}%', (object_xyxy[0], object_xyxy[1] - 20), cv2.FONT_ITALIC, 1, (0, 0, 255), 2)
        #         cv2.rectangle(frame, (object_xyxy[0], object_xyxy[1]), (object_xyxy[2], object_xyxy[3]), color, 2)
        
        
        # resized = cv2.resize(frame, (int(self.img_size_x/2),int(self.img_size_y)),interpolation=cv2.INTER_AREA)
        # self.publisher.publish(self.cvbrid.cv2_to_imgmsg(resized))
        cv2.imshow("Object Detection1", annotated)
        cv2.waitKey(1)  # Adjust the waitKey value for the desired frame display time

def main(args=None):
    rclpy.init(args=args)
    node = TrashSort()
    try :
        rclpy.spin(node)
    except KeyboardInterrupt :
        node.get_logger().info('Keyboard Interrupt (SIGINT)')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()