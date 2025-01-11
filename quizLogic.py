import csv

class QuizLogic:
    def __init__(self):
        self.questions = []
        self.current_question_index = 0
        self.score = 0
        self.total_questions_answered = 0

    def load_questions_from_csv(self, filename):
        """Charge les questions depuis un fichier CSV."""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=';')
                self.questions = []
                for row in reader:
                    question_text = row["Question Text"].strip()
                    question_type = row["Question Type"].strip()
                    options = [
                        row["Option 1"].strip(),
                        row["Option 2"].strip(),
                        row["Option 3"].strip(),
                        row["Option 4"].strip(),
                        row["Option 5"].strip(),
                    ]
                    correct_answer = row["Correct Answer"].strip()
                    time_limit = int(row["Time in seconds"].strip()) if row["Time in seconds"].strip().isdigit() else 30
                    explanation = row["Answer explanation"].strip()
                    
                    self.questions.append({
                        "question": question_text,
                        "type": question_type,
                        "options": [opt for opt in options if opt],
                        "correct": correct_answer,
                        "time_limit": time_limit,
                        "explanation": explanation
                    })
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement des questions : {e}")

    def get_current_question(self):
        """Retourne la question actuelle et ses données."""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None

    def validate_answer(self, user_answer):
        """Valide la réponse de l'utilisateur et retourne un feedback."""
        question_data = self.get_current_question()
        if not question_data:
            return None, None  # Pas de question actuelle

        is_correct = str(user_answer) == question_data["correct"]
        feedback = "Correct !" if is_correct else "Incorrect."
        explanation = question_data["explanation"]

        # Mise à jour du score et de la progression
        if is_correct:
            self.score += 1
        self.total_questions_answered += 1

        return feedback, explanation, is_correct

    def next_question(self):
        """Passe à la question suivante."""
        self.current_question_index += 1
        if self.current_question_index >= len(self.questions):
            return False  # Fin du quiz
        return True

    def get_score(self):
        """Retourne le score actuel et le nombre total de questions répondues."""
        return self.score, self.total_questions_answered

    def get_total_questions(self):
        """Retourne le nombre total de questions dans le quiz."""
        return len(self.questions)