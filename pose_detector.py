"""
Pose Detection Module
MediaPipe ile pose, hand ve face detection
"""

import cv2
import mediapipe as mp
import numpy as np


class PoseDetector:
    """MediaPipe ile pose algılama - 4 poz: el kaldırma, şaşırma, düşünme, varsayılan"""
    
    def __init__(self):
        # MediaPipe modüllerini başlat
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_face_mesh = mp.solutions.face_mesh
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Debug bilgileri
        self.debug_info = {
            'mouth_ratio': 0.0,
            'hand_height': 0.0,
            'hands_detected': 0,
            'face_detected': False
        }
        
    def detect_pose(self, frame):
        """Frame üzerinde pose detection yapar"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detection'lar
        pose_results = self.pose.process(rgb_frame)
        hand_results = self.hands.process(rgb_frame)
        face_results = self.face_mesh.process(rgb_frame)
        
        # Debug sıfırla
        self.debug_info['hands_detected'] = 0
        self.debug_info['face_detected'] = False
        
        # Sadece ağız bölgesi çiz
        if face_results.multi_face_landmarks:
            self.debug_info['face_detected'] = True
            for face_landmarks in face_results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                h, w = frame.shape[:2]
                
                # Sadece dudak konturları
                self.mp_drawing.draw_landmarks(
                    frame,
                    face_landmarks,
                    self.mp_face_mesh.FACEMESH_LIPS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=1)
                )
        
        # Eller çiz
        if hand_results.multi_hand_landmarks:
            self.debug_info['hands_detected'] = len(hand_results.multi_hand_landmarks)
            for hand_landmarks in hand_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        
        # Pozu belirle
        pose_name = self._determine_pose(pose_results, hand_results, face_results)
        
        # Debug bilgileri göster
        y_pos = 30
        cv2.putText(frame, f"Eller: {self.debug_info['hands_detected']}", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        y_pos += 30
        cv2.putText(frame, f"Yuz: {'VAR' if self.debug_info['face_detected'] else 'YOK'}", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        y_pos += 30
        cv2.putText(frame, f"Agiz: {self.debug_info['mouth_ratio']:.3f}", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        y_pos += 30
        cv2.putText(frame, f"El Yukseklik: {self.debug_info['hand_height']:.3f}", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Poz göster
        cv2.putText(frame, f"Pose: {pose_name}", (10, frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        return frame, pose_name
    
    def _determine_pose(self, pose_results, hand_results, face_results):
        """Pozu belirler - öncelik: el kaldırma > düşünme > şaşırma > varsayılan"""
        if self._is_raising_hand(pose_results, hand_results):
            return "raising_hand"
        
        if self._is_thinking(pose_results, hand_results, face_results):
            return "thinking"
        
        if self._is_shocking(face_results):
            return "shocking"
        
        return "default"
    
    def _is_raising_hand(self, pose_results, hand_results):
        """El baş hizasından yukarıda mı"""
        if not pose_results.pose_landmarks or not hand_results.multi_hand_landmarks:
            self.debug_info['hand_height'] = 0.0
            return False
        
        pose_landmarks = pose_results.pose_landmarks.landmark
        nose_y = pose_landmarks[self.mp_pose.PoseLandmark.NOSE].y
        
        for hand_landmarks in hand_results.multi_hand_landmarks:
            wrist_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST].y
            height_diff = nose_y - wrist_y
            self.debug_info['hand_height'] = height_diff
            
            if height_diff > 0.05:
                return True
        
        return False
    
    def _is_shocking(self, face_results):
        """Ağız açık mı"""
        if not face_results.multi_face_landmarks:
            self.debug_info['mouth_ratio'] = 0.0
            return False
        
        face_landmarks = face_results.multi_face_landmarks[0].landmark
        
        # Ağız landmark'ları
        upper_lip = face_landmarks[13].y
        lower_lip = face_landmarks[14].y
        forehead = face_landmarks[10].y
        chin = face_landmarks[152].y
        face_height = abs(chin - forehead)
        
        mouth_opening = abs(lower_lip - upper_lip)
        mouth_ratio = mouth_opening / face_height if face_height > 0 else 0
        self.debug_info['mouth_ratio'] = mouth_ratio
        
        return mouth_ratio > 0.15
    
    def _is_thinking(self, pose_results, hand_results, face_results):
        """El ağza/çeneye değiyor mu (thinking pozu)"""
        if not face_results.multi_face_landmarks or not hand_results.multi_hand_landmarks:
            return False
        
        face_landmarks = face_results.multi_face_landmarks[0].landmark
        
        # Ağız bölgesi (üst dudak, alt dudak, çene)
        mouth_points = [
            face_landmarks[13],   # Üst dudak
            face_landmarks[14],   # Alt dudak
            face_landmarks[152],  # Çene
            face_landmarks[0],    # Ağız merkezi
        ]
        
        for hand_landmarks in hand_results.multi_hand_landmarks:
            # El parmaklarının uçları
            finger_tips = [
                hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP],
                hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP],
                hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
            ]
            
            # Herhangi bir parmak ağız bölgesine çok yakın mı?
            for finger_tip in finger_tips:
                for mouth_point in mouth_points:
                    distance = np.sqrt((finger_tip.x - mouth_point.x)**2 + (finger_tip.y - mouth_point.y)**2)
                    
                    # Threshold çok düşük - neredeyse değmeli
                    if distance < 0.08:
                        return True
        
        return False
    
    def release(self):
        """Kaynakları serbest bırak"""
        self.pose.close()
        self.hands.close()
        self.face_mesh.close()
