import json
import os 
import math
import numpy as np
import cv2
import logging


class PoseHandler:
    def __init__(self, idx, keypoints, error, align, pose, status):
        
        self.path = os.path.join(f"{status}/analyze", f"{idx}.jpg")
        self.error = error
        self.align = align
        self.pose = pose
        self.img = cv2.imread(self.path)
        
        
        self.kp = keypoints
        
        self.names = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle",
        "left_finger", "right_finger", "left_rib", "right_rib",
        "left_toe", "right_toe"
        ]
        
        
        for i, name in enumerate(self.names):
            setattr(self, name, self.kp[i])
        
        
        self.correct_list1 = {
            1: "Excessively protruding belly",
            2: "Head down, arms wide",
            3: "Curved back",
            4: "Hips too high",
            6: "Toes curled back",
            7: "Hyperextended elbows",
            8: "Hands need to pull back",
            9: "Arms must be vertical",
        }
        
        self.correct_list2 = {
            7:"Overarched back",
            10:"Leaning too far forward"
            }
        self.correct_list3 = {
            7:"Rounded shoulders"
            }
        
        self.pose_list = {
            1: "Mountain Pose",
            2: "Backbend Pose",
            3: "Forward Fold Pose",
            4: "Plank Pose",
            5: "Upward Dog Pose",
            6: "Cobra Pose",
            7: "Downward Dog Pose",
            8: "Eight-Point Pose",
            9: "Crocodile Pose",
            10: "Low Lunge Pose"
            }
        
        
        self.left = True
        self.down_left = True
        
        
        self.correct1 = True
        self.correct2 = True
        self.correct3 = True
        
        self.temp1 = []
        self.temp2 = []
        self.temp3 = []
        
        
    def detect_side_case_1(self):
        #山式
        if (self.left_shoulder[0]+self.right_shoulder[0])/2 < self.nose[0]:
            self.left = False
            

    def handle_case_1(self):
        if self.left:
            if self.compare_angle(self.left_shoulder, self.left_rib, self.left_hip, 180-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.left_shoulder, self.left_rib, self.left_hip])
            
        else:
            if self.compare_angle(self.right_shoulder, self.right_rib, self.right_hip, 180-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.right_shoulder, self.right_rib, self.right_hip])
                
                
    
    def detect_side_case_2(self):
        #後彎
        if (self.left_wrist[0]+self.right_wrist[0]) < (self.left_hip[0]+self.right_hip[0]):
            self.left = False
        

    def handle_case_2(self):
        if self.left:
            if self.compare_angle(self.left_wrist, self.left_ear, self.left_shoulder, 180-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.left_wrist, self.left_ear, self.left_shoulder])
            
        else:
            if self.compare_angle(self.right_wrist, self.right_ear, self.right_shoulder, 180-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.right_wrist, self.right_ear, self.right_shoulder])
                
                
    

    def detect_side_case_3(self):
        #前彎
        if (self.left_shoulder[0]+self.right_shoulder[0]) > (self.left_knee[0]+self.right_knee[0]):
            self.left = False
            

    def handle_case_3(self):
        
        if self.left:
            if self.compare_angle(self.left_shoulder, self.left_rib, self.left_hip, 180-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.left_shoulder, self.left_rib, self.left_hip])
                
        else:
            if self.compare_angle(self.right_shoulder, self.right_rib, self.right_hip, 180-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.right_shoulder, self.right_rib, self.right_hip])

    

    def detect_side_case_4(self):
        #平板式
        if (self.left_hip[0]+self.right_hip[0]) < (self.left_shoulder[0]+self.right_shoulder[0]):
            self.left = False


    def handle_case_4(self):
        
        if self.left:
            if self.compare_angle(self.left_shoulder, self.left_hip, self.left_ankle, 180-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.left_shoulder, self.left_hip, self.left_ankle])
                
        else:
            if self.compare_angle(self.right_shoulder, self.right_hip, self.right_ankle, 180-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.right_shoulder, self.right_hip, self.right_ankle])
    
    
    
    def detect_side_case_6(self):
       #眼鏡蛇式
       if (self.left_shoulder[0]+self.right_shoulder[0])/2 < self.nose[0]:
           self.left = False
           

    def handle_case_6(self):
        if self.left:
            if self.compare_angle(self.left_knee, self.left_ankle, self.left_toe, 120-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.left_knee, self.left_ankle, self.left_toe])
                
        else:
            if self.compare_angle(self.right_knee, self.right_ankle, self.right_toe, 120-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.right_knee, self.right_ankle, self.right_toe])
                
    
    
    def detect_side_case_7(self):
        #下犬式
        if (self.left_wrist[0]+self.right_wrist[0]) > (self.left_shoulder[0]+self.right_shoulder[0]):
            self.left = False


    def handle_case_7(self):
        if self.left:
            if self.compare_angle(self.left_shoulder, self.left_elbow, self.left_wrist, 180-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.left_shoulder, self.left_elbow, self.left_wrist])
                
            if self.compare_angle(self.left_wrist, self.left_shoulder, self.left_hip, 180-self.error, "<", False):
                self.correct2 = False
                self.temp2.append([self.left_wrist, self.left_shoulder, self.left_hip])
                
            if self.compare_angle(self.left_wrist, self.left_shoulder, self.left_hip, 180+self.error, ">", False):
                self.correct3 = False
                self.temp3.append([self.left_wrist, self.left_shoulder, self.left_hip])
            
        else:
            if self.compare_angle(self.right_shoulder, self.right_elbow, self.right_wrist, 180-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.right_shoulder, self.right_elbow, self.right_wrist])
                
            if self.compare_angle(self.right_wrist, self.right_shoulder, self.right_hip, 180-self.error, "<", False):
                self.correct2 = False
                self.temp2.append([self.right_wrist, self.right_shoulder, self.right_hip])
                
            if self.compare_angle(self.right_wrist, self.right_shoulder, self.right_hip, 180+self.error, ">", False):
                self.correct3 = False
                self.temp3.append([self.right_wrist, self.right_shoulder, self.right_hip])
                
    
    
    def detect_side_case_8(self):
        #八肢點式
        if (self.left_hip[0]+self.right_hip[0]) < (self.left_shoulder[0]+self.right_shoulder[0]):
            self.left = False


    def handle_case_8(self):
        if self.left:
            if self.compare_angle(self.left_finger, self.left_wrist, self.left_elbow, 90+self.error, ">", False):
                self.correct1 = False
                self.temp1.append([self.left_finger, self.left_wrist, self.left_elbow])
                
        else:
            if self.compare_angle(self.right_finger, self.right_wrist, self.right_elbow, 90+self.error, ">", False):
                self.correct1 = False
                self.temp1.append([self.right_finger, self.right_wrist, self.right_elbow])
        

    

    def detect_side_case_9(self):
        #鱷魚式
        if (self.left_hip[0]+self.right_hip[0]) < (self.left_shoulder[0]+self.right_shoulder[0]):
            self.left = False
            

    def handle_case_9(self):
        
        if self.left:
            if self.compare_angle(self.left_shoulder, self.left_elbow, self.left_wrist, 90-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.left_shoulder, self.left_elbow, self.left_wrist])
                
            elif self.compare_angle(self.left_shoulder, self.left_elbow, self.left_wrist, 90+self.error, ">", False):
                self.correct1 = False
                self.temp1.append([self.left_shoulder, self.left_elbow, self.left_wrist])
            
        else:
            if self.compare_angle(self.right_shoulder, self.right_elbow, self.right_wrist, 90-self.error, "<", False):
                self.correct1 = False
                self.temp1.append([self.right_shoulder, self.right_elbow, self.right_wrist])
                
            elif self.compare_angle(self.right_shoulder, self.right_elbow, self.right_wrist, 90+self.error, ">", False):
                self.correct1 = False
                self.temp1.append([self.right_shoulder, self.right_elbow, self.right_wrist])


    
    def detect_side_case_10(self):
        #低弓箭步
        if (self.left_hip[0]+self.right_hip[0])/2 < self.nose[0]:
            self.left = False
            
        if self.left:
            if self.left_knee[0] > self.right_knee[0]:
                self.down_left = False
                
        else:
            if self.left_knee[0] < self.right_knee[0]:
                self.down_left = False
            

    def handle_case_10(self):
        
        if self.down_left:                
            if self.compare_angle(self.left_knee, self.left_ankle, self.left_toe, 90-self.error, "<", False):
                self.correct2 = False
                self.temp2.append([self.left_knee, self.left_ankle, self.left_toe])
                
        else:
            if self.compare_angle(self.right_knee, self.right_ankle, self.right_toe, 90-self.error, "<", False):
                self.correct2 = False
                self.temp2.append([self.right_knee, self.right_ankle, self.right_toe])



    def align_pose(self):
    
        keypoints = [np.array(p) for p in self.kp]
    

        hip_mid = (self.left_hip + self.right_hip) / 2
        keypoints_centered = [p - hip_mid for p in keypoints]
    

        shoulder_mid = (self.left_shoulder + self.right_shoulder) / 2
        torso_vector = shoulder_mid - hip_mid
    
        angle_to_vertical = np.arctan2(torso_vector[0], torso_vector[1])  
        rotation_matrix = np.array([
            [np.cos(-angle_to_vertical), -np.sin(-angle_to_vertical)],
            [np.sin(-angle_to_vertical),  np.cos(-angle_to_vertical)],
        ])
    
        self.kp = [rotation_matrix @ p for p in keypoints_centered]
        for i, name in enumerate(self.names):
            setattr(self, name, self.kp[i])
    
            
        
    
    def compare_angle(self, k1, k2, k3, angle, mode, full_degree):
        
        v1 = np.array(k1) - np.array(k2)
        v2 = np.array(k3) - np.array(k2)
        
        if full_degree:
            angle_rad = np.arctan2(np.cross(v1, v2), np.dot(v1, v2))  
            angle_deg = np.degrees(angle_rad)
            if angle_deg < 0:
                angle_deg += 360
                
            
                
        else:
            dot = np.dot(v1, v2)
            norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
            cos_angle = dot / norm_product
            angle_rad = np.arccos(np.clip(cos_angle, -1.0, 1.0))
            angle_deg = np.degrees(angle_rad)
        
        #logging.info(f"[INFO] ask_angle:{angle}")    
        #logging.info(f"[INFO] people_angle:{angle_deg}!")    
        
        if mode == ">":
            result =  angle_deg > angle
        elif mode == "<": 
            result =  angle_deg < angle
            
        
        return result


    def draw(self):
        img_set = []
        
        
        h, w = self.img.shape[:2]
        x = 50
        y = 120
        symbol_font_scale = 3
        text_font_scale = 1.5
        thickness = 8
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        
        #print(self.correct1)
        #print(self.correct2)
        #print(self.correct3)
        
        if  self.correct1 and self.correct2 and self.correct3:

            symbol_color = (0, 200, 0)
            img1 = self.img.copy()
            img1 = cv2.putText(img1, self.pose_list[int(self.pose)], (x, y), font, symbol_font_scale, symbol_color, thickness, cv2.LINE_AA)
            img_set.append(img1)
        
        else:
            alpha = 0.6
            symbol_color = (0, 0, 255)
            img2 = self.img.copy()
            img2 = cv2.putText(img2, self.pose_list[int(self.pose)], (x, y), font, symbol_font_scale, symbol_color, thickness, cv2.LINE_AA)
            
            overlay = img2.copy()
            cv2.rectangle(overlay, (0, h - 120), (w, h), (0, 0, 0), -1)  # 黑色背景
            
            cv2.addWeighted(overlay, alpha, img2, 1 - alpha, 0, img2)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            if not self.correct1:
                
                text = self.correct_list1[self.pose]
                textsize = cv2.getTextSize(text, font, 2.0, thickness)[0]
                text_x = (w - textsize[0]) // 2
                text_y = h - 40  
            
                img2 = cv2.putText(img2, text, (text_x, text_y), font, 2.0, (255, 255, 255), thickness, cv2.LINE_AA)
                
                
                x1 = int(self.temp1[0][0][0])
                y1 = int(self.temp1[0][0][1])
                x2 = int(self.temp1[0][1][0])
                y2 = int(self.temp1[0][1][1])
                x3 = int(self.temp1[0][2][0])
                y3 = int(self.temp1[0][2][1])
                
                #draw points

                img2 = cv2.circle(img2, (x1, y1), 20, (255, 255, 0), -1)
                img2 = cv2.circle(img2, (x2, y2), 20, (255, 255, 0), -1)
                img2 = cv2.circle(img2, (x3, y3), 20, (255, 255, 0), -1)
                
                #draw line between points
                img2 = cv2.line(img2, (x1, y1), (x2, y2), (0, 0, 255), 2)
                img2 = cv2.line(img2, (x3, y3), (x2, y2), (0, 0, 255), 2)
                
                img_set.append(img2)
                img2 = self.img.copy()
            
            if not self.correct2:
                text = self.correct_list2[self.pose]
                textsize = cv2.getTextSize(text, font, 2.0, thickness)[0]
                text_x = (w - textsize[0]) // 2
                text_y = h - 40  
            
                img2 = cv2.putText(img2, text, (text_x, text_y), font, 2.0, (255, 255, 255), thickness, cv2.LINE_AA)
                
                x1 = int(self.temp2[0][0][0])
                y1 = int(self.temp2[0][0][1])
                x2 = int(self.temp2[0][1][0])
                y2 = int(self.temp2[0][1][1])
                x3 = int(self.temp2[0][2][0])
                y3 = int(self.temp2[0][2][1])
                
                #draw points

                img2 = cv2.circle(img2, (x1, y1), 20, (255, 255, 0), -1)
                img2 = cv2.circle(img2, (x2, y2), 20, (255, 255, 0), -1)
                img2 = cv2.circle(img2, (x3, y3), 20, (255, 255, 0), -1)
                
                #draw line between points
                img2 = cv2.line(img2, (x1, y1), (x2, y2), (0, 0, 255), 2)
                img2 = cv2.line(img2, (x3, y3), (x2, y2), (0, 0, 255), 2)
                
                img_set.append(img2)
                img2 = self.img.copy()
            
            if not self.correct3:
                text = self.correct_list3[self.pose]
                textsize = cv2.getTextSize(text, font, 2.0, thickness)[0]
                text_x = (w - textsize[0]) // 2
                text_y = h - 40  
            
                cv2.putText(img2, text, (text_x, text_y), font, 2.0, (255, 255, 255), thickness, cv2.LINE_AA)
                
                x1 = int(self.temp3[0][0][0])
                y1 = int(self.temp3[0][0][1])
                x2 = int(self.temp3[0][1][0])
                y2 = int(self.temp3[0][1][1])
                x3 = int(self.temp3[0][2][0])
                y3 = int(self.temp3[0][2][1])
                
                #draw points

                img2 = cv2.circle(img2, (x1, y1), 20, (255, 255, 0), -1)
                img2 = cv2.circle(img2, (x2, y2), 20, (255, 255, 0), -1)
                img2 = cv2.circle(img2, (x3, y3), 20, (255, 255, 0), -1)
                
                #draw line between points
                img2 = cv2.line(img2, (x1, y1), (x2, y2), (0, 0, 255), 2)
                img2 = cv2.line(img2, (x3, y3), (x2, y2), (0, 0, 255), 2)
                
                img_set.append(img2)
                
        return img_set
    
                            



def correct(result_json, error, align, status):
    logging.info("[INFO] correct start!")

    image_set = []
    path = f"D:/my_project/android-camera-socket-stream-master/server/{status}/analyze"

    
    result = result_json["result"]
    
    
    for key in result.keys():
        logging.info(f"[INFO] pose: {int(key)+1}")
        pose_data = result[key]
        idx =  pose_data["idx"]
        keypoints = pose_data["keypoints"]
        
        handler = PoseHandler(idx, keypoints, error, align, int(key)+1, status)
    
        if align:
            handler.align_pose()
    
        #right or left
        detect_fn = getattr(handler, f"detect_side_case_{int(key)+1}", None)
        if detect_fn:
            detect_fn()
    
        #correct or not
        handle_fn = getattr(handler, f"handle_case_{int(key)+1}", None)
        if handle_fn:
            handle_fn()
            
        #logging.info(f"[INFO] keypoints: {keypoints}")
        #logging.info(f"[INFO] left:{handler.left}")
        #logging.info(f"[INFO] down_left:{handler.down_left}")       
        
        image_set.extend(handler.draw())
    logging.info("[INFO] correct finish!")
    return image_set
    


