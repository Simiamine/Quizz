import csv
import tkinter as tk
from tkinter import filedialog, messagebox


class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz Big Data")
        
        # Variables pour le quiz
        self.questions = []
        self.current_question_index = 0
        self.score = 0
        self.total_questions_answered = 0
        self.selected_option = tk.IntVar()  # pour les boutons radio
        self.timer = None
        self.time_left = 0

        # Interface principale
        self.frame_intro = tk.Frame(self.master)
        self.frame_intro.pack(pady=20)
        
        self.label_intro = tk.Label(self.frame_intro, text="Bienvenue dans le Quiz Big Data !\nSélectionnez un fichier CSV pour commencer.")
        self.label_intro.pack(pady=10)
        
        self.button_load_csv = tk.Button(self.frame_intro, text="Charger un CSV", command=self.load_csv)
        self.button_load_csv.pack()

        # Frame pour le quiz (sera affichée après chargement CSV)
        self.frame_quiz = tk.Frame(self.master)
        
        self.label_question = tk.Label(self.frame_quiz, text="", wraplength=500, justify="left", font=("Helvetica", 12, "bold"))
        self.label_question.pack(pady=10)

        self.label_timer = tk.Label(self.frame_quiz, text="", font=("Helvetica", 10, "bold"), fg="red")
        self.label_timer.pack(pady=5)

        self.radio_buttons = []  # Boutons pour les options

        self.label_feedback = tk.Label(self.frame_quiz, text="", font=("Helvetica", 10, "italic"), fg="blue", wraplength=500, justify="left")
        self.label_feedback.pack(pady=5)

        self.label_score = tk.Label(self.frame_quiz, text="Score : 0/0", font=("Helvetica", 10, "bold"), fg="green")
        self.label_score.pack(pady=5)

        self.button_next = tk.Button(self.frame_quiz, text="Valider", command=self.validate_answer)
        self.button_next.pack(pady=10)

    def load_csv(self):
        """Ouvre une boîte de dialogue pour charger le fichier CSV, et initialise le quiz."""
        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return  # l'utilisateur a annulé

        # Lecture du CSV
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
                        "options": [opt for opt in options if opt],  # Filtrer les options vides
                        "correct": correct_answer,
                        "time_limit": time_limit,
                        "explanation": explanation
                    })
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lire le fichier CSV.\n{e}")
            return

        if not self.questions:
            messagebox.showwarning("Attention", "Le fichier CSV est vide ou invalide.")
            return
        
        # Passage à la frame du quiz
        self.frame_intro.pack_forget()
        self.frame_quiz.pack(pady=20)
        
        # Initialisation du quiz
        self.current_question_index = 0
        self.score = 0
        self.total_questions_answered = 0
        self.show_question()

    def show_question(self):
        """Affiche la question et les options pour l'index courant."""
        # Remise à zéro de la sélection (0 => rien de coché)
        self.selected_option.set(0)

        # Stopper tout timer en cours
        if self.timer:
            self.master.after_cancel(self.timer)
            self.timer = None

        # Charger la question courante
        question_data = self.questions[self.current_question_index]
        self.label_question.config(text=f"Q{self.current_question_index + 1}. {question_data['question']}")
        self.label_feedback.config(text="")  # Effacer le feedback précédent
        self.label_score.config(text=f"Score : {self.score}/{self.total_questions_answered}")

        # Mettre à jour les options
        for rb in self.radio_buttons:
            rb.pack_forget()  # Masquer les anciens boutons
        self.radio_buttons.clear()

        for i, option_text in enumerate(question_data['options']):
            rb = tk.Radiobutton(self.frame_quiz, text=option_text, variable=self.selected_option, 
                                value=i + 1, wraplength=500, justify="left", anchor="w")
            rb.pack(anchor="w")
            self.radio_buttons.append(rb)
        
        # Configurer le timer
        self.time_left = question_data['time_limit']
        self.update_timer()

    def update_timer(self):
        """Met à jour le temps restant pour la question."""
        if self.time_left > 0:
            self.label_timer.config(text=f"Temps restant : {self.time_left} s")
            self.time_left -= 1
            self.timer = self.master.after(1000, self.update_timer)  # Mise à jour toutes les secondes
        else:
            self.validate_answer(timeout=True)

    def validate_answer(self, timeout=False):
        """Valide la réponse courante et affiche un feedback."""
        question_data = self.questions[self.current_question_index]
        correct_answer = question_data["correct"]
        explanation = question_data["explanation"]

        # Arrêter le timer
        if self.timer:
            self.master.after_cancel(self.timer)
            self.timer = None

        # Vérification de la réponse
        user_answer = self.selected_option.get()
        if not timeout and user_answer == 0:
            messagebox.showwarning("Attention", "Veuillez sélectionner une réponse.")
            return

        # Calcul du feedback
        if not timeout and str(user_answer) == correct_answer:
            self.score += 1
            feedback = f"Correct ! 🎉\nExplication : {explanation}"
        elif timeout:
            feedback = f"Temps écoulé ! ❌\nExplication : {explanation}"
        else:
            feedback = f"Incorrect. ❌\nExplication : {explanation}"

        self.label_feedback.config(text=feedback)
        self.total_questions_answered += 1
        self.label_score.config(text=f"Score : {self.score}/{self.total_questions_answered}")

        # Passer à la question suivante
        self.button_next.config(text="Question suivante", command=self.next_question)

    def next_question(self):
        """Passe à la question suivante ou termine le quiz."""
        self.current_question_index += 1
        if self.current_question_index < len(self.questions):
            self.show_question()
            self.button_next.config(text="Valider", command=self.validate_answer)
        else:
            self.end_quiz()

    def end_quiz(self):
        """Affiche le score final et termine le quiz."""
        total_questions = len(self.questions)
        messagebox.showinfo("Quiz terminé", f"Votre score final : {self.score}/{total_questions}")
        self.master.quit()


def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()