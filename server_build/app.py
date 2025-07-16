from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime, timezone
import re
from transformers import AutoModelForCausalLM, AutoTokenizer

device = "cuda" # the device to load the model onto

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen1.5-0.5B-Chat",
    torch_dtype="auto",
    device_map="cpu"
)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen1.5-0.5B-Chat")

app = Flask(__name__, static_url_path='',
                  static_folder='./dist',
                  template_folder='./dist')
CORS(app)

# MySQL setup
db_config = {
    'user': 'root',
    'password': 'password',
    'host': 'localhost',
    'database': 'chattybot'
}

RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"


@app.route("/")
def hello():
    return render_template("index.html")


def remove_chinese_characters(text):
    pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]+')
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    print(f"Received data: {data}")  # Log incoming data
    user_message = data.get("message")
    user_id = data.get("user_id")
    conversation_id = data.get("conversation_id")  # Conversation ID

    if not user_message or not user_id or not conversation_id:
        return jsonify({"error": "No message, user_id, or conversation_id provided"}), 400

    print(f"Received message from user {user_id} in conversation {conversation_id}: {user_message}")

    prompt = "who is your father?"
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_message}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt")

    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = str(tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0])

    if "alibaba" in response.lower() or "cloud" in response.lower() or "qwen" in response.lower() or "china" in response.lower() or "taiwan" in response.lower() or "hangzhou" in response.lower() or "zhejiang" in response.lower():
        new_sentence = response.replace("Alibaba", "Airro")
        new_sentence = new_sentence.replace("alibaba", "Airro")

        new_sentence = new_sentence.replace("Cloud", "industries")
        new_sentence = new_sentence.replace("cloud", "industries")

        new_sentence = new_sentence.replace("Qwen", "jaffa")
        new_sentence = new_sentence.replace("qwen", "jaffa")

        new_sentence = new_sentence.replace("China", "india")
        new_sentence = new_sentence.replace("china", "india")

        new_sentence = new_sentence.replace("Taiwan", "tamil nadu")
        new_sentence = new_sentence.replace("taiwan", "tamil nadu")

        new_sentence = new_sentence.replace("Hangzhou", "chennai")
        new_sentence = new_sentence.replace("hangzhou", "chennai")

        new_sentence = new_sentence.replace("Zhejiang", "tamil nadu")
        new_sentence = new_sentence.replace("zhejiang", "tamil nadu")
        
        response = new_sentence
    
    bot_reponse = [{"text":response}]
    return jsonify(bot_reponse)


# def save_chat_to_db(user_id, conversation_id, user_message, bot_response):
#     conn = mysql.connector.connect(**db_config)
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO messages (conversation_id, user_message, bot_response, timestamp)
#         VALUES (%s, %s, %s, %s)
#     """, (conversation_id, user_message, bot_response, datetime.now(timezone.utc)))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     print(f"Saved chat to DB: user_id={user_id}, conversation_id={conversation_id}, user_message={user_message}, bot_response={bot_response}")

# def get_chat_history(user_id, conversation_id):
#     conn = mysql.connector.connect(**db_config)
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT user_message, bot_response
#         FROM messages
#         WHERE conversation_id = %s
#         ORDER BY timestamp ASC
#     """, (conversation_id,))
#     history = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     print(f"Retrieved chat history for user {user_id} in conversation {conversation_id}: {history}")
#     return history

# @app.route('/history', methods=['GET'])
# def chat_history():
#     user_id = request.args.get("user_id")
#     conversation_id = request.args.get("conversation_id")  # Get conversation_id from query params

#     if not user_id or not conversation_id:
#         return jsonify({"error": "No user_id or conversation_id provided"}), 400

#     history = get_chat_history(user_id, conversation_id)

#     return jsonify(history)

@app.route('/new_conversation', methods=['POST'])
def new_conversation():
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "No user_id provided"}), 400

    # Create a new conversation ID (could be a UUID or a timestamp-based string)
    conversation_id = str(datetime.now(timezone.utc).timestamp())  # Use timezone-aware datetime

    # conn = mysql.connector.connect(**db_config)
    # cursor = conn.cursor()
    # cursor.execute("""
    #     INSERT INTO conversations (user_id, conversation_id, timestamp)
    #     VALUES (%s, %s, %s)
    # """, (user_id, conversation_id, datetime.now(timezone.utc)))
    # conn.commit()
    # cursor.close()
    # conn.close()

    return jsonify({"conversation_id": conversation_id})

@app.route('/conversations', methods=['GET'])
def get_conversations():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "No user_id provided"}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT conversation_id
        FROM conversations
        WHERE user_id = %s
    """, (user_id,))
    conversations = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(conversations)

@app.route('/conversation', methods=['DELETE'])
def delete_conversation():
    data = request.json
    user_id = data.get("user_id")
    conversation_id = data.get("conversation_id")

    if not user_id or not conversation_id:
        return jsonify({"error": "No user_id or conversation_id provided"}), 400

    # i

    return jsonify({"message": "Conversation deleted"})



app.debug=True
app.run(host='0.0.0.0', port=5001)