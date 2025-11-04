import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from models import QuestionDataset, QuizGenerator, QuizCorrector


class QuizView:
    """
    Handles all Streamlit rendering and user interactions.
    """
    def __init__(self, dataset: QuestionDataset):
        self.dataset = dataset
        self.tags = dataset.get_all_tags()

        if "quiz_questions" not in st.session_state:
            st.session_state["quiz_questions"] = []
        if "answers" not in st.session_state:
            st.session_state["answers"] = {}
        if "results" not in st.session_state:
            st.session_state["results"] = None
        if "generated" not in st.session_state:
            st.session_state["generated"] = False

    def reset_quiz(self):
        st.session_state["quiz_questions"] = []
        st.session_state["answers"] = {}
        st.session_state["results"] = None
        st.session_state["generated"] = False
        st.success("Quiz reset.")

    def select_fields(self):
        st.sidebar.header("Quiz options")
        selected_tags = st.sidebar.multiselect("Select fields / tags (empty = all):", options=self.tags)
        num_q = st.sidebar.number_input("Number of questions", min_value=1, max_value=20, value=5, step=1)
        shuffle_choices = st.sidebar.checkbox("Shuffle choices", value=True)
        return {"selected_tags": selected_tags, "num_q": int(num_q), "shuffle_choices": bool(shuffle_choices)}

    def generate_quiz(self, options):
        generator = QuizGenerator(self.dataset)
        questions = generator.generate(
            selected_tags=options["selected_tags"],
            num_questions=options["num_q"],
            shuffle_choices=options["shuffle_choices"]
        )
        if not questions:
            st.warning("No questions available for the selected tags.")
            return
        st.session_state["quiz_questions"] = questions
        st.session_state["answers"] = {}
        st.session_state["results"] = None
        st.session_state["generated"] = True
        st.success(f"Generated {len(questions)} questions.")

    def show_quiz(self):
        st.header("Quiz")
        if not st.session_state["generated"] or not st.session_state["quiz_questions"]:
            st.info("Generate a quiz (choose tags and click 'Generate Quiz').")
            return

        questions = st.session_state["quiz_questions"]

        for idx, q in enumerate(questions):
            st.markdown(f"**Q{idx+1}. {q.question}**")
            key = f"q_{idx}"
            if q.mode == "single":
                prev = st.session_state["answers"].get(idx, None)
                choice = st.radio("", options=q.choices, index=q.choices.index(prev) if prev in q.choices else None, key=key)
                st.session_state["answers"][idx] = choice
            else:
                prev = st.session_state["answers"].get(idx, [])
                sel = st.multiselect("", options=q.choices, default=prev, key=key)
                st.session_state["answers"][idx] = sel
            st.write("---")

    def submit_and_correct(self):
        if not st.session_state["generated"] or not st.session_state["quiz_questions"]:
            st.warning("No quiz to submit. Generate a quiz first.")
            return
        corrector = QuizCorrector()
        results = corrector.correct(st.session_state["quiz_questions"], st.session_state["answers"])
        st.session_state["results"] = results

        total_percent = results["total_normalized"] * 100
        st.success(f"Total score: {total_percent:.1f}%")

        st.subheader("Per-question feedback")
        for det in results["details"]:
            idx = det["index"]
            q_text = det["question"]
            st.markdown(f"**Q{idx+1}. {q_text}**")
            st.write(f"Correct answer(s): {', '.join(det['correct'])}")
            st.write(f"Your answer: {det['selected']}")
            st.write(f"Score: {det['score']:.2f}")
            if det["mode"] == "single":
                if det["score"] >= 1.0:
                    st.success("Correct")
                else:
                    st.error("Incorrect")
            else:
                if det["score"] > 0:
                    st.info(f"Partial credit: {det['score']:.2f}")
                else:
                    st.error("No credit")
            st.write("---")

    
        st.markdown('<h3 style="font-size:30px;text-align:center;">Overall performance</h3>', unsafe_allow_html=True)

        per_scores = results["per_question_scores"]
        total_q = len(per_scores)

        # Categorize
        correct_count = sum(1 for s in per_scores if s >= 0.99)
        partial_count = sum(1 for s in per_scores if 0 < s < 0.99)
        incorrect_count = sum(1 for s in per_scores if s <= 0.0)

        labels = ["Correct", "Partial", "Incorrect"]
        values = [correct_count, partial_count, incorrect_count]
        colors = ["#4CAF50", "#FFC107", "#F44336"]  # green, yellow, red

        # Create figure
        fig, ax = plt.subplots(figsize=(4, 4))
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct=lambda pct: f"{pct:.1f}%" if pct > 0 else "",
            startangle=90,
            wedgeprops=dict(width=0.35, edgecolor='white'),
            textprops={"fontsize": 12, "weight": "bold"}
        )

        # --- Adaptive text color for contrast ---
        for i, autotext in enumerate(autotexts):
            rgb = mcolors.to_rgb(colors[i])
            luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
            autotext.set_color("black" if luminance > 0.5 else "white")

        # --- Center text ---
        ax.text(
            0, 0,
            f"{correct_count}/{total_q}\nCorrect",
            ha='center', va='center', fontsize=14, weight='bold'
        )

        ax.axis('equal')  # Circle
        fig.patch.set_facecolor("none")

        # --- Center chart visually ---
        st.pyplot(fig, use_container_width=True)

        # --- Legend below the chart ---
        st.markdown(
            f"""
            <div style='text-align:center; font-size:15px; margin-top:-10px;'>
                ✅ <b>{correct_count}</b> correct &nbsp;|&nbsp;
                🟡 <b>{partial_count}</b> partial &nbsp;|&nbsp;
                ❌ <b>{incorrect_count}</b> incorrect
            </div>
            """,
            unsafe_allow_html=True
        )


# ==================== Streamlit App Configuration ====================
st.set_page_config(page_title="OOP Quiz Generator", layout="wide")
st.title("Interactive OOP Quiz Generator")

dataset = QuestionDataset("quiz_dataset.json")
quiz_view = QuizView(dataset)

if st.button("Reset Quiz"):
    quiz_view.reset_quiz()

options = quiz_view.select_fields()

if st.button("Generate Quiz"):
    quiz_view.generate_quiz(options)

quiz_view.show_quiz()

if st.button("Submit & Correct Quiz"):
    quiz_view.submit_and_correct()


