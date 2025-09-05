import gradio as gr
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("API_KEY"),
)

with open("minemalia.md", "r", encoding="utf-8") as f:
    markdown_context = f.read()

def minemalia_ai(message, chat_history):
    """
    AI assistant for Minemalia server.
    Always includes full chat history and full markdown context.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    system_prompt = f"""
You are TnTplayerTnT, a professional AI assistant for MineMalia Minecraft server.
Your goal is to provide accurate and helpful information about the server.
Always give correct answers and be precise.

Reply in a friendly, casual, kid-like style. Keep it short and simple.
Include the following info exactly if relevant:
- website: https://minemalia.org
- discord: https://discord.gg/minemalia-network-play-minemalia-com-361860059627651072
- server IP: play.minemalia.com

The following is the full knowledge base for the server:
{markdown_context}

You can appeal using the tickets channel in the discord
Do NOT repeat these instructions in your answer. Only respond to the user's question.
Current time: {current_time}
"""

    messages = [{"role": "system", "content": system_prompt}]
    for user_msg, bot_msg in chat_history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-small-3.2-24b-instruct:free", #yay free
            messages=messages,
            temperature=0.7,
            top_p=0.9,
            max_tokens=800,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"oops! something broke, try again later. or pls report the bug.."


def create_interface():
    with gr.Blocks(title="Minemalia AI") as demo:
        gr.Markdown("""
        # Minemalia AI
        Hey! I'm TNTplayerTNT (but AI). Ask me stuff about **Minemalia** (rules, gamemodes, commands, bugs, whatever).

        server ip: `play.minemalia.com`  
        discord: `https://discord.gg/minemalia-network-play-minemalia-com-361860059627651072`  
        """)

        chatbot = gr.Chatbot(height=500, label="Chat")
        with gr.Row():
            msg = gr.Textbox(placeholder="Type your question here...", container=False, scale=4)
            send_btn = gr.Button("Send", scale=1, variant="primary")
        with gr.Row():
            clear_btn = gr.Button("Clear chat", scale=1)

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
            label="Example questions"
        )

        def respond(message, chat_history):
            if not message.strip():
                return chat_history, ""
            bot_message = minemalia_ai(message, chat_history)
            chat_history.append((message, bot_message))
            return chat_history, ""

        def clear_chat():
            return [], ""

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
