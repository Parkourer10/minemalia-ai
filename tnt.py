import gradio as gr
from openai import OpenAI
from datetime import datetime
import re
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("API_KEY"),
)

with open("minemalia.md", "r", encoding="utf-8") as f:
    markdown_context = f.read()

def classify(message: str) -> str:
    system_prompt = """You are a professional classifier AI. 
Classify the user query into one of these categories:
- gameplay
- rules
- commands
- server
- features
- gamemodes
- community
- technical
- general

Respond with only ONE word from the list."""
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b:free",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        temperature=0.0,
        max_tokens=5
    )
    return response.choices[0].message.content.strip().lower()

def extract(query, context):
    query_lower = query.lower()
    relevant_sections = []
    sections = re.split(r'\n# ', context)
    for section in sections:
        section_lower = section.lower()
        if any(word in section_lower for word in query_lower.split()):
            if len(section) > 2000:
                section = section[:2000] + "..."
            relevant_sections.append(section)
    return relevant_sections[:3]

def genocide(message, chat_history):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query_type = classify(message)

    use_context = query_type in ["gameplay", "rules", "commands", "server", "features", "gamemodes", "community"]
    relevant_context = ""
    if use_context:
        sections = extract(message, markdown_context)
        if sections:
            relevant_context = "\n\n---\n" + "\n\n".join(sections)

    # professional system prompt
    system_prompt = f"""You are TnTplayerTnT, a professional AI assistant for MineMalia Minecraft server.
Your goal is to provide accurate and helpful information about the server.
You understand all gamemodes, commands, rules, technical issues, and community info.
Always give precise and correct answers. Be professional in understanding the user's needs.
Current time: {current_time}"""

    #chat history so its like an actual convo
    messages = [{"role": "system", "content": system_prompt}]
    for user_msg, bot_msg in chat_history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    full_prompt = f"""{message}

{relevant_context if relevant_context else ""}

instructions: reply in a chill, casual, friendly, kid-like way. keep it simple and fun, but helpful. Website url: https://minemalia.org Discord: https://discord.gg/minemalia-network-play-minemalia-com-361860059627651072 Server IP: play.minemalia.com

"""
    messages.append({"role": "user", "content": full_prompt})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=messages,
            temperature=0.8,
            top_p=0.9,
            max_tokens=1000,
        )
        bot_reply = response.choices[0].message.content.strip()
        return bot_reply
    except Exception as e:
        return f"oops! something broke. try again later. (error: {str(e)})"

def create_interface():
    with gr.Blocks(title="Minemalia AI") as demo:
        gr.Markdown("""
        ## Minemalia AI Helper (Not Official pls no blame on me)
        Hey! I'm TnTplayerTnT AI (i mean the original one also seems AI its just that this cant refuse and will stay online 24/7).  
        Ask me stuff about **Minemalia**  
        (rules, gamemodes, commands, bugs, whatever)

        server ip: `play.minemalia.com`  
        discord: `https://discord.gg/minemalia-network-play-minemalia-com-361860059627651072`  
        """)

        chatbot = gr.Chatbot(height=500, label="chat")

        with gr.Row():
            msg = gr.Textbox(
                placeholder="type ur question here...",
                container=False,
                scale=4
            )
            send_btn = gr.Button("send", scale=1, variant="primary")

        with gr.Row():
            clear_btn = gr.Button("clear chat", scale=1)

        gr.Examples(
            examples=[
                "how can i join minemalia?",
                "what are the server rules?",
                "how do i vote?",
                "what commands are in survival?",
                "how does lifesteal work?",
                "im banned, how do i appeal?",
                "what is the discord link?",
                "who is the best player?",
                "how do i commit war crimes?",
            ],
            inputs=msg,
            label="example questions"
        )

        def respond(message, chat_history):
            if not message.strip():
                return chat_history, ""
            bot_message = genocide(message, chat_history)
            chat_history.append((message, bot_message))
            return chat_history, ""
        
        def clear_chat():
            return [], "" #shit

        send_btn.click(respond, [msg, chatbot], [chatbot, msg])
        msg.submit(respond, [msg, chatbot], [chatbot, msg])
        clear_btn.click(clear_chat, outputs=[chatbot, msg])

    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
