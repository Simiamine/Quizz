import tkinter as tk
from tkinter import filedialog, messagebox
from quizLogic import QuizLogic


class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz Big Data")
        
        # Logique du quiz
        self.quiz = QuizLogic()

        # Variables pour l'interface
        self.selected_option = tk.IntVar()
        self.timer = None
        self.time_left = 0

        # Interface principale
        self.frame_intro = tk.Frame(self.master)
        self.frame_intro.pack(pady=20)
        
        self.label_intro = tk.Label(self.frame_intro, text="Bienvenue dans le Quiz Big Data !\nSélectionnez un fichier CSV pour commencer.")
        self.label_intro.pack(pady=10)
        
        self.button_load_csv = tk.Button(self.frame_intro, text="Charger un CSV", command=self.load_csv)
        self.button_load_csv.pack()

        # Frame pour le quiz
        self.frame_quiz = tk.Frame(self.master)
        
        self.label_question = tk.Label(self.frame_quiz, text="", wraplength=500, justify="left", font=("Helvetica", 12, "bold"))
        self.label_question.pack(pady=10)

        self.label_timer = tk.Label(self.frame_quiz, text="", font=("Helvetica", 10, "bold"), fg="red")
        self.label_timer.pack(pady=5)

        self.radio_buttons = []

        self.label_feedback = tk.Label(self.frame_quiz, text="", font=("Helvetica", 10, "italic"), fg="blue", wraplength=500, justify="left")
        self.label_feedback.pack(pady=5)

        self.label_score = tk.Label(self.frame_quiz, text="Score : 0/0", font=("Helvetica", 10, "bold"), fg="green")
        self.label_score.pack(pady=5)

        self.button_next = tk.Button(self.frame_quiz, text="Valider", command=self.validate_answer)
        self.button_next.pack(pady=10)

    def load_csv(self):
        """Ouvre une boîte de dialogue pour charger le fichier CSV."""
        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return

        try:
            self.quiz.load_questions_from_csv(filename)
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return

        # Passer à l'interface de quiz
        self.frame_intro.pack_forget()
        self.frame_quiz.pack(pady=20)
        self.show_question()

    def show_question(self):
        """Affiche la question actuelle."""
        self.selected_option.set(0)
        question_data = self.quiz.get_current_question()
        if not question_data:
            return

        self.label_question.config(text=f"Q{self.quiz.current_question_index + 1}. {question_data['question']}")
        self.label_feedback.config(text="")
        self.label_score.config(text=f"Score : {self.quiz.score}/{self.quiz.total_questions_answered}")

        # Créer les boutons dynamiquement
        for rb in self.radio_buttons:
            rb.pack_forget()
        self.radio_buttons.clear()

        for i, option_text in enumerate(question_data["options"]):
            rb = tk.Radiobutton(self.frame_quiz, text=option_text, variable=self.selected_option, 
                                value=i + 1, wraplength=500, justify="left", anchor="w")
            rb.pack(anchor="w")
            self.radio_buttons.append(rb)

        self.time_left = question_data["time_limit"]
        self.update_timer()

    def update_timer(self):
        """Met à jour le timer."""
        if self.time_left > 0:
            self.label_timer.config(text=f"Temps restant : {self.time_left} s")
            self.time_left -= 1
            self.timer = self.master.after(1000, self.update_timer)
        else:
            self.validate_answer(timeout=True)

    def validate_answer(self, timeout=False):
        """Valide la réponse de l'utilisateur."""
        question_data = self.quiz.get_current_question()
        user_answer = self.selected_option.get()

        if self.timer:
            self.master.after_cancel(self.timer)

        if not timeout and user_answer == 0:
            messagebox.showwarning("Attention", "Veuillez sélectionner une réponse.")
            return

        feedback, explanation, is_correct = self.quiz.validate_answer(user_answer if not timeout else None)
        if timeout:
            feedback = "Temps écoulé ! ❌"
        self.label_feedback.config(text=f"{feedback}\nExplication : {explanation}")
        self.label_score.config(text=f"Score : {self.quiz.score}/{self.quiz.total_questions_answered}")

        self.button_next.config(text="Question suivante", command=self.next_question)

    def next_question(self):
        """Passe à la question suivante."""
        if self.quiz.next_question():
            self.show_question()
            self.button_next.config(text="Valider", command=self.validate_answer)
        else:
            self.end_quiz()

    def end_quiz(self):
        """Affiche le score final."""
        total_questions = self.quiz.get_total_questions()
        messagebox.showinfo("Quiz terminé", f"Votre score final : {self.quiz.score}/{total_questions}")
        self.master.quit()


def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()