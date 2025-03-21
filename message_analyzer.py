import pandas as pd
import re
from datetime import datetime

# Function to process the chat file
def process_chat(file):
    pattern = re.compile(r"\[(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}:\d{2})\] (.*?): (.*)")
    messages = []
    for line in file:
        match = pattern.match(line)
        if match:
            date, time, sender, message = match.groups()
            messages.append([date, time, sender, message])

    df = pd.DataFrame(messages, columns=["Date", "Time", "Sender", "Message"])
    df["Hour"] = df["Time"].apply(lambda x: int(x.split(":")[0]))
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"], format="%d/%m/%y %H:%M:%S")
    
    return df

# Function to group short messages within a time limit
def group_short_messages(df, time_limit_minutes=1):
    grouped_messages = []
    current_message = ""
    last_sender = None
    last_time = None

    for _, row in df.iterrows():
        sender, message, time = row["Sender"], row["Message"], row["Datetime"]

        if len(message.split()) <= 2:
            if sender == last_sender and (last_time is None or (time - last_time).seconds <= time_limit_minutes * 60):
                current_message += " " + message
            else:
                if current_message:
                    grouped_messages.append((last_sender, current_message.strip(), last_time))
                current_message = message
            last_sender, last_time = sender, time
        else:
            if current_message:
                grouped_messages.append((last_sender, current_message.strip(), last_time))
            grouped_messages.append((sender, message, time))
            current_message, last_sender, last_time = "", sender, time

    if current_message:
        grouped_messages.append((last_sender, current_message.strip(), last_time))

    grouped_df = pd.DataFrame(grouped_messages, columns=["Sender", "Message", "Datetime"])
    return grouped_df

# List of words to remove
words_to_remove = {"videochamada", "ta", "ja", "bem", "pra", "tou", "so"}

# Slang dictionary for replacements
slang_dict = {
    "n": "não", "sq": "secalhar", "vc": "você", "tb": "também", "q": "que", "hj": "hoje",
    "blz": "beleza", "vlw": "valeu", "flw": "falou", "brb": "be right back", "tmj": "tamo junto",
    "bjs": "beijos", "td": "tudo", "tbm": "também", "pq": "porque", "oq": "o que",
    "bwe": "bue", "s": "sim", "mm": "mesmo", "agr": "agora", "min": "minutos", "tp": "tipo", "tou": "estou"
}

# Function to preprocess text
def preprocess_text(text):
    text = re.sub(r"[^\x00-\x7F]+", "", text)  # Remove non-ASCII characters (emojis)
    text = re.sub(r"http\S+|www\S+", "", text)  # Remove URLs
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    text = text.lower()  # Convert to lowercase

    words = text.split()
    words = [slang_dict.get(word, word) for word in words]  # Apply slang substitutions
    words = [word for word in words if word not in words_to_remove]  # Remove specific words

    return " ".join(words)  # Convert back to string

# Function that handles everything: Processing, Grouping, and Preprocessing
def process_and_group_chat(file, time_limit_minutes=1):
    df = process_chat(file)
    grouped_df = group_short_messages(df, time_limit_minutes)
    grouped_df["Processed_Message"] = grouped_df["Message"].apply(preprocess_text)
    return grouped_df
