import os
import shutil
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

        # Cadres de l'interface
        self.frame_intro = tk.Frame(self.master)
        self.frame_choose_quiz = tk.Frame(self.master)
        self.frame_quiz = tk.Frame(self.master)

        self.create_intro_frame()
        self.create_choose_quiz_frame()
        self.create_quiz_frame()

        # Afficher le cadre d'introduction au démarrage
        self.show_frame(self.frame_intro)

    def show_frame(self, frame):
        """Affiche un cadre spécifique et masque les autres."""
        for f in (self.frame_intro, self.frame_choose_quiz, self.frame_quiz):
            f.pack_forget()
        frame.pack(pady=20)

    def create_intro_frame(self):
        """Crée le cadre d'introduction."""
        label_intro = tk.Label(self.frame_intro, text="Bienvenue dans le Quiz Big Data !")
        label_intro.pack(pady=10)

        button_choose_quiz = tk.Button(self.frame_intro, text="Choisir un quiz", command=self.show_choose_quiz)
        button_choose_quiz.pack(pady=5)

        button_add_quiz = tk.Button(self.frame_intro, text="Ajouter un quiz", command=self.add_quiz)
        button_add_quiz.pack(pady=5)

    def create_choose_quiz_frame(self):
        """Crée le cadre de sélection d'un quiz."""
        self.label_choose_quiz = tk.Label(self.frame_choose_quiz, text="Sélectionnez un fichier quiz :")
        self.label_choose_quiz.pack(pady=10)

        self.quiz_var = tk.StringVar()
        self.dropdown_quiz = tk.OptionMenu(self.frame_choose_quiz, self.quiz_var, [])
        self.dropdown_quiz.pack(pady=10)

        button_back = tk.Button(self.frame_choose_quiz, text="Retour", command=lambda: self.show_frame(self.frame_intro))
        button_back.pack(pady=5, side=tk.LEFT)

        button_start = tk.Button(self.frame_choose_quiz, text="Lancer le quiz", command=self.load_selected_quiz)
        button_start.pack(pady=5, side=tk.RIGHT)

    def create_quiz_frame(self):
        """Crée le cadre du quiz."""
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

    def show_choose_quiz(self):
        """Affiche la liste des quiz disponibles dans le dossier res."""
        quiz_dir = "res"
        if not os.path.exists(quiz_dir):
            os.makedirs(quiz_dir)

        quiz_files = [f for f in os.listdir(quiz_dir) if f.endswith(".csv")]
        if not quiz_files:
            messagebox.showinfo("Aucun quiz", "Aucun fichier quiz trouvé dans le dossier res.")
            return

        # Mettre à jour la liste déroulante
        self.quiz_var.set(quiz_files[0])
        menu = self.dropdown_quiz["menu"]
        menu.delete(0, "end")
        for quiz in quiz_files:
            menu.add_command(label=quiz, command=lambda q=quiz: self.quiz_var.set(q))

        self.show_frame(self.frame_choose_quiz)

    def add_quiz(self):
        """Ajoute un fichier quiz dans le dossier res."""
        filename = filedialog.askopenfilename(
            title="Ajouter un fichier quiz",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return  # L'utilisateur a annulé

        quiz_dir = "res"
        if not os.path.exists(quiz_dir):
            os.makedirs(quiz_dir)

        dest_path = os.path.join(quiz_dir, os.path.basename(filename))
        try:
            shutil.copy(filename, dest_path)
            messagebox.showinfo("Succès", f"Le fichier {os.path.basename(filename)} a été ajouté au dossier res.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ajouter le fichier : {e}")

    def load_selected_quiz(self):
        """Charge un fichier quiz sélectionné et passe au quiz."""
        selected_quiz = os.path.join("res", self.quiz_var.get())
        try:
            self.quiz.load_questions_from_csv(selected_quiz)
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return

        # Passer au quiz
        self.show_frame(self.frame_quiz)
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
        self.show_frame(self.frame_intro)


def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()