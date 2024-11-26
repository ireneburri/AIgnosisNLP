from . import LLM_init

class Anamnesis:
    def __init__(self, model='gpt-4o-mini'):
        self.model = model
        self.information = {
            "duration": [],
            "symptoms": [],
            "pre_existing_conditions": [], 
            "medications": [], 
            "allergies": [], 
            "severity": [], 
            "lifestyle_factors": [], 
        }
        self.required = self.information.keys()
        self.llm = LLM_init.LLM(model)
        self.last_question = ""
        self.answer = ""

    def summarize_question(self, last_question, answer):
        self.last_question = last_question
        self.answer = answer
        response = self.llm(task='summary', last_question=self.last_question, answer=self.answer)
        undesired_responses = ["not specified", "not mentioned", "unknown", "none"]
        for key, value in response.items():
            if key in self.information and value and value.lower() not in undesired_responses:
                entries = [item.strip() for item in value.split(',')]
                for entry in entries:
                    if entry and entry not in self.information[key]:
                        self.information[key].append(entry)
        print(f'Current Information: {self.information}')
        return self.information

    def check_if_ready_for_diagnosis(self):
        return self.llm(task='ready for diagnosis', information=self.information, required=self.required)

    def provide_diagnosis(self):
        return self.llm(task='diagnosis', information=self.information)

    def generate_next_question(self):
        return self.llm(task='question', information=self.information, last_question=self.last_question, answer=self.answer)

    def process_response(self, last_question, answer):
        # Summarize the answer and update information
        self.summarize_question(last_question, answer)

        # Check if we are ready to provide a diagnosis
        if self.check_if_ready_for_diagnosis():
            # Provide a diagnosis if enough information is gathered
            diagnosis_info = self.provide_diagnosis()

            # Format the diagnosis output nicely
            formatted_diagnosis = (
                f"**Diagnosis**: {diagnosis_info['diagnosis']}\n"
                f"**Recommendations**:\n"
                f"{diagnosis_info['recommendations']}\n"
            )

            if diagnosis_info.get('specialist'):
                formatted_diagnosis += f"**Specialist**: {diagnosis_info['specialist']}\n"

            return {"type": "diagnosis", "content": formatted_diagnosis}

        else:
            # Otherwise, generate the next best question
            next_question = self.generate_next_question()
            return {"type": "question", "content": next_question}


# Example usage
def main():
    # Initialize the LLM object
    anamnesis = Anamnesis()

    # Example for starting the conversation
    last_question = "How long have you had this issue?"
    last_answer = "For about two weeks."

    # Summarize the conversation and update required information
    updated_info = anamnesis.summarize_question(last_question, last_answer)
    print("Updated required information:", updated_info)

    # Check if the system is ready to provide a diagnosis
    if anamnesis.check_if_ready_for_diagnosis():
        diagnosis = anamnesis.provide_diagnosis()
        print(f"Diagnosis: {diagnosis}")
    else:
        # Generate the next question dynamically if more information is needed
        next_question = anamnesis.generate_next_question()
        print(f"Next Question: {next_question}")

