import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
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

        qos_profile = QoSProfile(
        reliability=ReliabilityPolicy.BEST_EFFORT,
        history=HistoryPolicy.KEEP_LAST,
        depth=1  
        )
        
        self.publisher = self.create_publisher(Image,'side_camera',qos_profile)
        
        ### camera parameter setting ###
        self.img_size_x = 640
        self.img_size_y = 480

        self.frame_rate = 10
        ##################################
        
        #### algorithm parameter ####
        self.general_waste_ROI = [[int(self.img_size_x * 0.2), int(self.img_size_y * 0.7)],[int(self.img_size_x * 0.4), int(self.img_size_y * 0.95)]]
        self.plastic_waste_ROI = [[int(self.img_size_x * 0.2), int(self.img_size_y * 0.4)],[int(self.img_size_x * 0.4), int(self.img_size_y * 0.65)]]
        self.glass_waste_ROI = [[int(self.img_size_x * 0.2), int(self.img_size_y * 0.1)],[int(self.img_size_x * 0.4), int(self.img_size_y * 0.35)]]
        
        # self.postbox_ROI = [[int(self.img_size_x * 0.4), int(self.img_size_y * 0.65)],[int(self.img_size_x * 0.5), int(self.img_size_y * 0.75)]]## xy xy
        
        ##################################
        
        self.cap0 = cv2.VideoCapture('/dev/video0')  #cam0
        self.cvbrid = CvBridge()
        
        self.cap0.set(cv2.CAP_PROP_FRAME_WIDTH, self.img_size_x)
        self.cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, self.img_size_y)
        self.cap0.set(cv2.CAP_PROP_FPS, self.frame_rate)
        
        self.image_cap_timer = self.create_timer(1/self.frame_rate, self.img_cap)
        self.img_timer = self.create_timer(1/self.frame_rate, self.image_callback)
        
        self.color_img = np.zeros((self.img_size_y, self.img_size_x, 3), dtype=np.uint8)
        
        
        print(f"General waste ROI: {self.general_waste_ROI}")
        print(f"Plastic waste ROI: {self.plastic_waste_ROI}")
        print(f"Glass waste ROI: {self.glass_waste_ROI}")

    def img_cap(self) :
        ret0, frame = self.cap0.read()
        
        if not (ret0) :
            if not ret0 :
                print(f'cam0 is cannot connetion')
        else :
            self.color_img = frame
        
    def image_callback(self):
        
        result = self.model.predict(self.color_img, conf = 0.5, verbose=False)
        
        cv2.rectangle(self.color_img, (int(self.general_waste_ROI[0][0]),int(self.general_waste_ROI[0][1])), ((int(self.general_waste_ROI[1][0]), int(self.general_waste_ROI[1][1]))), (255,0,0),2)
        cv2.rectangle(self.color_img, (int(self.plastic_waste_ROI[0][0]),int(self.plastic_waste_ROI[0][1])), ((int(self.plastic_waste_ROI[1][0]), int(self.plastic_waste_ROI[1][1]))), (0,255,0),2)
        cv2.rectangle(self.color_img, (int(self.glass_waste_ROI[0][0]),int(self.glass_waste_ROI[0][1])), ((int(self.glass_waste_ROI[1][0]), int(self.glass_waste_ROI[1][1]))), (0,0,255),2)

        
        
        annotated = result[0].plot()
        
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