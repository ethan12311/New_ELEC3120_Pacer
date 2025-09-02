# Create interactive widgets for the chatbot
question_input = widgets.Text(
    value='',
    placeholder='Type your question here...',
    description='Question:',
    disabled=False,
    layout=widgets.Layout(width='80%')
)

ask_button = widgets.Button(
    description='Ask',
    disabled=False,
    button_style='primary',
    tooltip='Ask your question',
    icon='question'
)

concept_input = widgets.Text(
    value='',
    placeholder='Type a concept to find references...',
    description='Concept:',
    disabled=False,
    layout=widgets.Layout(width='80%')
)

find_concept_button = widgets.Button(
    description='Find References',
    disabled=False,
    button_style='info',
    tooltip='Find where a concept is mentioned'
)

progress_button = widgets.Button(
    description='Show Concepts',
    disabled=False,
    button_style='success',
    tooltip='Show all concepts found'
)

output_area = widgets.Output()

def on_ask_button_clicked(b):
    with output_area:
        clear_output()
        question = question_input.value
        if question:
            response = chatbot.ask_question(question)
            
            if response['type'] == 'error':
                display(Markdown(f"### ⚠️ {response['message']}"))
            elif response['type'] == 'not_found':
                display(Markdown(f"### ❌ {response['message']}"))
            elif response['type'] == 'concept_reference':
                display(Markdown(f"### 🔍 {response['message']}"))
                for concept, pages in response['concepts'].items():
                    display(Markdown(f"- **{concept}** appears on pages: {', '.join(map(str, pages))}"))
            else:
                display(Markdown(f"### 📚 Answer (from page {response['page']})"))
                display(Markdown(f"**{response['answer']}**"))
                display(Markdown(f"*Confidence: {response['confidence']:.2f}*"))
                display(Markdown(f"*Context: {response['context']}*"))
        else:
            display(Markdown("Please enter a question."))

def on_find_concept_clicked(b):
    with output_area:
        clear_output()
        concept = concept_input.value
        if concept:
            response = chatbot.get_concept_references(concept)
            
            if response['type'] == 'not_found':
                display(Markdown(f"### ❌ {response['message']}"))
            else:
                display(Markdown(f"### 🔍 Concept: {response['concept']}"))
                display(Markdown(f"Appears on pages: {', '.join(map(str, response['pages']))}"))
        else:
            display(Markdown("Please enter a concept."))

def on_progress_button_clicked(b):
    with output_area:
        clear_output()
        concepts = chatbot.concept_keywords
        
        if concepts:
            display(Markdown("### 📊 Concepts Found in Your Notes"))
            for i, (concept, pages) in enumerate(concepts.items()):
                if i < 20:  # Show first 20 concepts to avoid overload
                    display(Markdown(f"- **{concept}** (pages: {', '.join(map(str, pages))})"))
            if len(concepts) > 20:
                display(Markdown(f"... and {len(concepts) - 20} more concepts"))
        else:
            display(Markdown("No concepts found yet. Process your lecture notes first."))

# Link buttons to functions
ask_button.on_click(on_ask_button_clicked)
find_concept_button.on_click(on_find_concept_clicked)
progress_button.on_click(on_progress_button_clicked)

# Create layout
question_controls = widgets.HBox([question_input, ask_button])
concept_controls = widgets.HBox([concept_input, find_concept_button])
action_buttons = widgets.HBox([progress_button])

# Display the widgets
display(Markdown("## 🤖 Improved Lecture Notes Chatbot"))
display(Markdown("### ❓ Ask a Question About Your Notes"))
display(question_controls)
display(Markdown("### 🔍 Find Where a Concept is Mentioned"))
display(concept_controls)
display(Markdown("### ⚡ Actions"))
display(action_buttons)
display(Markdown("### 📋 Response"))
display(output_area)