**Objectif du projet**

Cette application permet de générer et corriger un quiz interactif sur les concepts de OOP.
Elle est faite avec Python et Streamlit, et utilise plusieurs classes pour séparer la logique (backend) et l’interface (frontend).

=> **Lancement de l’application**

Pour exécuter le projet: streamlit run app.py

L’application s’ouvre dans le navigateur avec le titre “Interactive OOP Quiz Generator”.

![alt text](image.png)

🧠 Comment l’application fonctionne (étape par étape)
🪄 1️⃣ Chargement du dataset — QuestionDataset

Quand l’application démarre, la première classe utilisée est QuestionDataset.

Elle lit le fichier quiz_dataset.json qui contient toutes les questions.

Grâce au pattern Singleton, ce fichier est chargé une seule fois pour éviter les doublons.

Elle met toutes les questions dans une liste d’objets de type Question.

📸 (capture d’écran suggérée : page d’accueil avant génération du quiz)

🧩 2️⃣ Sélection des options — QuizView.select_fields()

Dans la barre latérale de Streamlit, l’utilisateur peut choisir :

Les tags (domaines du quiz),

Le nombre de questions,

S’il veut ou non mélanger les choix.

Ces choix sont gérés par la classe QuizView, qui s’occupe de toute l’interface.
Elle retourne un petit dictionnaire contenant les options choisies.

📸 (capture d’écran suggérée : barre latérale avec les options sélectionnées)

🎲 3️⃣ Génération du quiz — QuizGenerator.generate()

Quand on clique sur “Generate Quiz”, c’est la classe QuizGenerator qui entre en action.

Elle récupère les questions du QuestionDataset.

Si l’utilisateur a choisi des tags, elle filtre les questions correspondantes.

Elle choisit un nombre de questions au hasard avec random.sample().

Elle peut aussi mélanger les réponses si l’option “shuffle choices” est cochée.

Le résultat est enregistré dans st.session_state["quiz_questions"], pour que les questions restent visibles même après des actions sur la page.

📸 (capture d’écran suggérée : quiz affiché avec les questions et boutons radio)

🧍 4️⃣ Réponse de l’utilisateur — QuizView.show_quiz()

Cette méthode affiche les questions une par une avec Streamlit :

Si la question est à choix unique, elle affiche des boutons radio.

Si la question est à choix multiples, elle affiche un multiselect.

Les réponses choisies par l’utilisateur sont stockées dans st.session_state["answers"].

💡 Les boutons radio ont toujours une option sélectionnée par défaut (le premier choix), car Streamlit ne permet pas de laisser un radio “vide”.

📸 (capture d’écran suggérée : utilisateur sélectionne des réponses)

🧮 5️⃣ Correction des réponses — QuizCorrector.correct()

Quand l’utilisateur clique sur “Submit & Correct Quiz”, c’est la classe QuizCorrector qui travaille.

Elle compare les réponses données avec les réponses correctes.
Deux méthodes sont utilisées :

score_single() pour les questions à une seule réponse,

score_multiple() pour les questions à plusieurs réponses.

👉 Le score est calculé pour chaque question, puis un score total (en pourcentage) est affiché à l’écran.

📸 (capture d’écran suggérée : résultats affichés avec score total)

📊 6️⃣ Affichage des résultats et graphiques — QuizView.submit_and_correct()

Une fois la correction terminée :

L’application affiche pour chaque question :

la bonne réponse,

la réponse donnée,

le score obtenu.

Ensuite, un graphique en barres est affiché avec Matplotlib pour visualiser les scores par question.

📸 (capture d’écran suggérée : graphique des scores)

🔁 7️⃣ Réinitialisation du quiz — QuizView.reset_quiz()

Quand on clique sur “Reset Quiz”, cette méthode vide :

Les questions,

Les réponses,

Les résultats.

Elle permet de recommencer un nouveau quiz proprement.

📸 (capture d’écran suggérée : message “Quiz reset.” affiché après clic)




Objectif du projet

Cette application permet de générer et corriger un quiz interactif sur les concepts de la programmation orientée objet (OOP).
Elle est faite avec Python et Streamlit, et utilise plusieurs classes pour séparer la logique (backend) et l’interface (frontend).

⚙️ Lancement de l’application

Pour exécuter le projet, on tape dans le terminal :

