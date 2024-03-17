# AWS Rekognition Models as Dataloop's Pipeline Applications

## Introduction

Amazon Rekognition is a cloud-based service for image and video analysis, designed to seamlessly integrate advanced 
computer vision features into your applications. Utilizing state-of-the-art deep learning technology, it offers a 
user-friendly interface that requires no prior machine learning knowledge. With its intuitive API, Amazon Rekognition 
can analyze images and videos stored in Amazon S3, offering a easy-to-use experience.


## Description

This repo is an integration between [AWS Rekgonition](https://docs.aws.amazon.com/rekognition/)
models and [Dataloop](https://dataloop.ai/).

The Applications provide accesses to AWS Rekognition models, using the AWS SDK for Python (Boto3), as Dataloop pipeline 
nodes. The detections are available to images only (not videos).

The proposed pipeline nodes:

* ```Detect Labels``` -  This node utilizes the DetectLabels operation to identify labels (objects and concepts) in 
an image, providing information about various image properties such as foreground and background color, sharpness, 
brightness, and contrast.


* ```Detect Faces``` - Amazon Rekognition Image offers the DetectFaces operation, which identifies key facial features 
like eyes, nose, and mouth to detect faces within an image. It can detect up to 100 faces. The face partial 
annotations within the Dataloop platform are considered child annotations of the face annotation.

* ```Detect Protective Equipment``` - This node is designed to detect Personal Protective Equipment (PPE) worn by 
individuals in an image, including categories such as Face cover, Hand cover, and Head cover.

* ```Recognize Celebrities``` - With pre-trained capabilities, this node can recognize hundreds of thousands of popular 
figures across various domains such as sports, media, politics, and business. The detection annotations are similar to 
those of face detection.

* ```Detect Moderation Labels``` - Utilizing a classification model, this node assesses whether an image contains 
inappropriate or offensive content, returning a list of labels indicating potential concerns.

* ```Detect Text``` - Amazon Rekognition can identify text within images and videos, and subsequently convert it into 
machine-readable text for further processing.

### The pipeline nodes parameters:

* ```threshold```: All nodes gets threshold, a float, between "0" to "1", (default: 0.8) as the threshold for 
confidence of the returned detection.
* ```Annotation type```: Parameter for ```Detect Text``` only. A choice between the type of the returned annotation - 
Box or Polygon.  

### Installation - Dataloop platform
Install the desired pipeline node from StartLine:


![bandicam2024-03-1715-16-15-658-ezgif com-video-to-gif-converter](https://github.com/dataloop-ai-apps/aws-rekognition-adapter/assets/152878248/4b327cdf-ba73-42c9-b94a-3b431032d9dc)



### Add integrations
Init parameter have to have same name as secrets name.



https://github.com/dataloop-ai-apps/aws-rekognition-adapter/assets/152878248/0a105518-6cfb-4aaa-8858-7a9c482b26fb

