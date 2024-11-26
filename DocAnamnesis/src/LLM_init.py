import openai
import os
import json

def get_openai_api_key():
    current_dir = os.path.dirname(__file__)
    key_file_path = os.path.join(current_dir, 'utils', 'OPENAI_API_KEY.txt')
    try:
        with open(key_file_path, "r") as file:
            key = file.read().strip()
    except FileNotFoundError:
        key = input("Please enter your OpenAI API token: ").strip()
        with open(key_file_path, "w") as file:
            file.write(key)
    return key

def textify_information(information):
    return "\n".join([
        f"{key}: {', '.join(value) if isinstance(value, list) else value}"
        for key, value in information.items()
    ])

class LLM:
    def __init__(self, model):
        self.openAI_api_key = get_openai_api_key()
        
        self.client = openai.OpenAI(api_key=self.openAI_api_key)
        self.diagnosis_model = 'gpt-4o-mini'
        self.question_model = model
        self.ready_for_diagnosis_model = 'gpt-4o-mini'
        self.summarize_model = 'gpt-4o-mini'
        self.functions = [
            {
                "name": "update_required_information",
                "description": "Update required information fields based on user response.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "duration": {"type": "string", "description": "Duration of the issue."},
                        "symptoms": {"type": "string", "description": "Symptoms described by the user."},
                        "pre_existing_conditions": {"type": "string", "description": "Any pre-existing conditions."},
                        "medications": {"type": "string", "description": "Any medications the user is currently taking."},
                        "allergies": {"type": "string", "description": "Any allergies the user has."},
                        "severity": {"type": "string", "description": "Severity of symptoms (e.g., mild, moderate, severe)."},
                        "lifestyle_factors": {"type": "string", "description": "Lifestyle factors such as smoking, alcohol use, exercise, etc."},
                    },
                    "required": ["duration", "symptoms", "pre_existing_conditions", "medications", "allergies", "severity", "onset", "triggers", "relief_methods", "family_history", "lifestyle_factors", "recent_travel", "diet", "sleep_patterns", "previous_treatments"]
                }
            },
            {
                "name": "provide_diagnosis",
                "description": "Provides a diagnosis based on patient information, suggests specialists, and gives actionable recommendations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "diagnosis": {
                            "type": "string",
                            "description": "The medical diagnosis based on the patient's information."
                        },
                        "recommendations": {
                            "type": "string",
                            "description": "Actionable recommendations for the patient (e.g., lifestyle changes, medications)."
                        },
                        "specialist": {
                            "type": "string",
                            "description": "If necessary, suggest a specialist to consult (e.g., cardiologist, dermatologist)."
                        }
                    },
                    "required": ["diagnosis", "recommendations"]
                }
            },
            {
                "name": "check_if_ready_for_diagnosis",
                "description": "Determines if enough relevant information has been gathered to make a diagnosis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ready": {
                            "type": "boolean",
                            "description": "A boolean indicating whether enough information has been gathered to make a diagnosis. Return either True or False (beware of the caps)"
                        }
                    },
                    "required": ["ready"]
                }
            },
            {
                "name": "generate_next_question",
                "description": "Evaluates the previous answer and generates the next best question to ask based on missing or incomplete information. The generated question should be simple, concise, and focused on one piece of information at a time.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "next_question": {
                            "type": "string",
                            "description": "The next best question to ask the patient, based on the provided information."
                        }
                    },
                    "required": ["next_question"]
                }
            }
        ]

    def __call__(self, task, information=None, required=None, last_question=None, answer=None):
        if task == 'summary':
            return self.summarize_conversation(last_question, answer)  # Uses summarize_model
        elif task == 'question':
            return self.generate_next_question(information, last_question=last_question, last_answer=answer)  # Uses question_model (fine-tuned model)
        elif task == 'ready for diagnosis':
            return self.check_if_ready_for_diagnosis(information, required)  # Uses ready_for_diagnosis_model
        elif task == 'diagnosis':
            return self.provide_diagnosis(information)  # Uses diagnosis_model
        else:
            raise ValueError(f"Unknown task: {task}")

    def summarize_conversation(self, last_question, last_answer):
        conversation_input = f"The following is a conversation between a doctor and a patient. The patient was asked: '{last_question}', and they responded: '{last_answer}'. Extract and return any relevant medical information in the provided JSON format."
        response = self.client.chat.completions.create(
            model=self.summarize_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical assistant. You help by extracting relevant medical information from patient conversations. Your goal is to identify key information. Format the extracted information according to the provided structure."
                },
                {
                    "role": "user",
                    "content": conversation_input
                }
            ],
            functions=self.functions,
            function_call={"name": "update_required_information"}
        )
        response_data = response.choices[0].message.function_call.arguments
        extracted_info = eval(response_data)
        print(extracted_info)
        return extracted_info  # Return the structured dictionary

    def check_if_ready_for_diagnosis(self, information, required):
        required_fields = ", ".join(required)
        gathered_info = textify_information(information)
        prompt = f"The required fields for making a diagnosis are: {required_fields}. The gathered information is:\n{gathered_info}.\n\nBased on this information, has the patient provided enough relevant details to make a diagnosis? It is not necessary for every field to be fully completed, only enough relevant information is needed."
        response = self.client.chat.completions.create(
            model=self.ready_for_diagnosis_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical assistant. Your task is to determine if enough relevant information has been gathered to proceed with a diagnosis. Not every required field needs to be fully answered, just sufficiently enough to make a diagnosis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            functions=self.functions,
            function_call={"name": "check_if_ready_for_diagnosis"}
        )
        ready_result = response.choices[0].message.function_call.arguments
        #ready_data = eval(ready_result)
        ready_data = json.loads(ready_result)
        print(f"Ready for diagnosis: {ready_data['ready']}")
        return ready_data["ready"]  # Returns True or False

    def generate_next_question(self, information, last_question, last_answer):
        conversation_summary = textify_information(information)
        prompt = (f"Here is the patient's current information:\n{conversation_summary}\n\n"
                  f"The last question was: '{last_question}' and the answer was: '{last_answer}'.\n"
                  "Evaluate if the answer sufficiently covers the topic. If the answer is insufficient, generate a follow-up question. "
                  "If it is sufficient, generate a new question that fills in any gaps in the required information. The question should be simple, concise, and ask for only one piece of information at a time.")
        response = self.client.chat.completions.create(
            model=self.question_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical assistant. Evaluate the sufficiency of the previous answer. "
                               "If more information is needed, generate a follow-up question or a new question that fills in gaps in the patient's information. "
                               "The question should be simple and ask for only one thing at a time."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            functions=self.functions,
            function_call={"name": "generate_next_question"}
        )
        next_question_result = response.choices[0].message.function_call.arguments
        next_question_data = eval(next_question_result)
        print(f"Next Question: {next_question_data['next_question']}")
        return next_question_data["next_question"]  # Returns the next best question to ask

    def provide_diagnosis(self, information):
        conversation_summary = textify_information(information)
        prompt = f"Based on the following patient information, provide a diagnosis, recommendations, and suggest if they should see a specialist:\n{conversation_summary}"
        response = self.client.chat.completions.create(
            model=self.diagnosis_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical doctor providing an initial diagnosis based on patient information. Your goal is to give a short,clear and concise diagnosis, suggest whether they should visit a specialist (and which type), and offer helpful suggestions on what they can do to improve their condition."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            functions=self.functions,
            function_call={"name": "provide_diagnosis"}
        )
        diagnosis_result = response.choices[0].message.function_call.arguments
        diagnosis_data = eval(diagnosis_result)
        print(f"Diagnosis: {diagnosis_data['diagnosis']}")
        return diagnosis_data  # Returns a dictionary with diagnosis, recommendations, and specialist
