import joblib
import logging
import numpy as np
import math
import logging
import time
from minio import Minio

class Strokeclf(object):
    def __init__(self):

        # Initialize MinIO
        client = client = Minio('10.96.235.164:9000',
           access_key='minioadmin',
           secret_key='minioadmin',
            secure=False
              )
        client.fget_object("modelclf","clf","temp/clf")
        client.fget_object("modelclf","mode","temp/mode")
        client.fget_object("modelclf","encoder_ordinal","temp/encoder_ordinal")
        client.fget_object("modelclf","encoder","temp/encoder")
        client.fget_object("modelclf","scaler","temp/scaler")

        # Initializing Variables, model, encoders
        log = logging.getLogger()
        self.mode = joblib.load("temp/mode")
        log.info(f'Initializing mode to {self.mode}')

        self.clf = joblib.load("temp/clf")
        log.info(f'Initializing Logistic Model')

        self.enc_ord = joblib.load("temp/encoder_ordinal")
        log.info(f'Initializing ordinal encoder')

        self.enc = joblib.load("temp/encoder")
        log.info(f'Initializing encooder')

        self.scaler = joblib.load("temp/scaler")
        log.info(f'Initializing scaler')
        
    
    def predict(self, X, features_name):

        

        # Initialize start time
        self.st = time.time()

        log = logging.getLogger()

        log.info(f'features name list = {features_name}')
        log.info(f'Values list = {X}')

        # Setting index based on feature names
        index_age = features_name.index("age")
        index_bmi = features_name.index("bmi")
        index_hypertension = features_name.index("hypertention")
        index_heart_disease = features_name.index("heart_disease")
        index_avg_glucose_level = features_name.index("avg_glucose_level")
        index_smoking_status = features_name.index("smoking_status")
        index_ever_married = features_name.index("ever_married")
        index_gender = features_name.index("gender")
        index_work_type = features_name.index("work_type")
        index_Residence_type = features_name.index("Residence_type")

        



        # Missing Value
        if X[index_bmi] == "nan":
            X[index_bmi] = self.mode
            log.info('Setting Missing Value for BMI')



        # Convert to numpy 
        values = np.array(X)

        # Define Values to encode and transform
        values_to_encode = values[[index_gender,index_ever_married,index_work_type, index_Residence_type]]
        transform_enc = self.enc.transform(values_to_encode.reshape(1,-1))[0]
        log.info(f'one hot    {transform_enc}')
        
        # Define values for ordinal encoder and transform
        values_to_ord_encode = values[[index_smoking_status]]
        transform_ord_enc = self.enc_ord.transform(values_to_ord_encode.reshape(1,-1))[0]
        log.info(f'testing ord encoder {transform_ord_enc}')

        # Dekete encoded values from the array and add the transformed values
        values =  np.delete(values,[index_gender,index_ever_married,index_Residence_type, index_work_type,index_smoking_status])
        for v in transform_enc:
            values = np.append(values,v)

        for v in transform_ord_enc:
            values = np.append(values,v)

        # Scale values betwee, 0 and 1
        values = self.scaler.transform(values.reshape(1,-1))
        
        # Predict
        result = self.clf.predict(values.reshape(1,-1))

        # End time of code
        self.et = time.time()

        # Call Metrics
        self.metrics()

        # Return prediction
        return result

    def metrics(self):

        # Exposing Metrics
        
        log = logging.getLogger()
        log.info("Exposing Custom Metrics")

        return [
            # a Find execution time of code
            {"type":"GAUGE","key":"gauge_runtime","value":self.et - self.st},
        ]