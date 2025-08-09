# PCB-fault-detection
Deployed custom trained yolov8 model to predict the defects in a PCB

Defects can be detected : missing hole, mouse bite, open circuit , short , spur ,spurious copper

Model : YOLOv8n
Environment : Anaconda , VS code
Tech Stack: HTML , CSS , JS , Flask 

Work Flow:

    Step 1: Collection of data set 
    
          we used the existing data set imported from roboflow
          Using roboflow , we processed the raw data and get the labels for bounding boxes of fault

    Step 2: After data collectio for both training and testing, we downloaded the necessary dependancies to run YOLO model
          I have used the Anaconda and i created a virtual environment to train the model

    Step 3: Trained the model in conda terminal for 200 epochs
    
    Step 4: Created a web interface and then integrated this model in the web
    
    Step 5: Now we can check a PCB in this web
          
<img width="1891" height="831" alt="image" src="https://github.com/user-attachments/assets/ba350bdd-eba9-4046-817e-050368979401" />

<img width="1586" height="617" alt="image" src="https://github.com/user-attachments/assets/93432c23-1f0d-442c-a819-81991ddf9ef6" />
<img width="1628" height="761" alt="image" src="https://github.com/user-attachments/assets/14b25b5f-2dd4-4508-a80e-a27539d38d13" />
