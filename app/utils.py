def load_model(model_path):
    import face_recognition
    return face_recognition.face_encodings(face_recognition.load_image_file(model_path))[0]

def process_image(image_path):
    import cv2
    image = cv2.imread(image_path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def recognize_faces(known_face_encodings, unknown_face_encoding):
    import face_recognition
    results = face_recognition.compare_faces(known_face_encodings, unknown_face_encoding)
    return results

def mark_attendance(name):
    import pandas as pd
    attendance_file = 'attendance.csv'
    try:
        df = pd.read_csv(attendance_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Name', 'Timestamp'])
    
    if name not in df['Name'].values:
        new_entry = pd.DataFrame([[name, pd.Timestamp.now()]], columns=['Name', 'Timestamp'])
        df = pd.concat([df, new_entry], ignore_index=True)
    
    df.to_csv(attendance_file, index=False)