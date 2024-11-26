# AIgnosis
AIgnosis is a digital anamnesis tool that integrates Natural Language Processing with a virtual human interface to enhance user engagement. The NLP component consists of a chatbot which collects and analyzes medical information, providing preliminary diagnoses or advice, while the virtual human, implemented in Unity, offers immersive interaction through dynamic animations, Text-to-Speech synchronization, and real-time responsiveness.
![SamplePicture](https://github.com/user-attachments/assets/2fe93a15-47ea-4e80-ad4e-0a71cdafa95d)
## Setup
For the app to work you need an OpenAI API key and paste in the according file (you need to create in this directory) in 'DocAnamnesis\src\utils\OPENAI_API_KEY.txt'.
Here is the link to the website for the OpenAI API https://platform.openai.com/login?launch
Login, create a Token (Here a manual: https://www.howtogeek.com/885918/how-to-get-an-openai-api-key/) and put in some balance (whole conversations are less than a cent).


## Disclaimer
You will only be able to use the Base-Model, since all Fine-Tuned Models are private by default, so expect to receive an error when you try to use the Fine-Tuned Model.

## App Start
To start the app install the requirements in the 'requirements.txt'.
Then start the app with 
```
$ python app.py
```
