import assemblyai as aai
import os
import json
import pymysql
from openai import OpenAI
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
aai.settings.api_key = os.getenv("ASSEMBLY_API_KEY")
audio_path = os.getenv("AUDIO_PATH")
processed_files_path = os.path.join(audio_path, "processed_files.txt")

def connect_to_db():
    connection = pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

def return_important_info(prompt):
    response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": json.dumps(prompt)}],
        )
    return str(response.choices[0].message.content)

def is_file_processed(file_name):
    if os.path.exists(processed_files_path):
        with open(processed_files_path, 'r', encoding='utf-8') as f:
            processed_files = f.read().splitlines()
        return file_name in processed_files
    return False

def mark_file_as_processed(file_name):
    with open(processed_files_path, 'a', encoding='utf-8') as f:
        f.write(file_name + "\n")

def process_audio_files():
    transcriber = aai.Transcriber()
    
    for file_name in os.listdir(audio_path):
        if file_name.endswith(('.m4a', '.mp3', '.wav')):  # You can add more formats if needed
            if is_file_processed(file_name):
                print(f"File {file_name} has already been processed. Skipping.")
                continue
            
            file_url = os.path.join(audio_path, file_name)
            print(f"Processing file: {file_name}")
            
            transcript = transcriber.transcribe(file_url)

            if transcript.status == aai.TranscriptStatus.error:
                print(f"Error transcribing {file_name}: {transcript.error}")
            else:
                prompt = {
                    "prompt": (
                        """
                        You are tasked with analyzing a transcribed NFL analyst show and extracting all relevant information that pertains to sports betting, player performance, team performance, predictions, and any other insights that may be useful for making better sports picks. Your output should be in JSON format, ready for upload to a SQL database.

                        Instructions:

                        Extract Key Insights:

                        Identify and extract key insights related to player performance, team performance, predictions, and any other relevant betting information mentioned in the transcript.
                        For each insight, provide the associated team and player names if mentioned.
                        Team Abbreviations:

                        Convert all mentioned team names to their standard NFL abbreviations (e.g., "Kansas City Chiefs" to "KC").
                        If a player is mentioned, include the abbreviation of their team as well.
                        Structure of the Output:

                        For each insight found, structure the output as a JSON object.
                        Each JSON object should include:
                        insight: The key insight extracted from the transcript.
                        team: The abbreviation of the team mentioned in the insight (if applicable).
                        player: The player mentioned in the insight (if applicable).
                        context: Additional context if relevant (e.g., whether it's a prediction, performance analysis, etc.).
                        Output Format:

                        The final output should be a list of JSON objects. Example format:
                        [
                            {
                                "insight": "Patrick Mahomes is expected to have a strong performance against the Broncos due to their weak pass defense.",
                                "team": "KC",
                                "player": "Patrick Mahomes",
                                "context": "Prediction"
                            },
                            {
                                "insight": "The Eagles have been solid in the red zone, converting 75% of their trips into touchdowns.",
                                "team": "PHI",
                                "context": "Team Performance"
                            }
                        ]
                        Additional Information:
                        If multiple insights relate to the same player or team, provide each insight as a separate JSON object.
                        Ensure that each insight is concise and directly related to sports betting or team/player performance.
                        If there is any information found that comes from a different sport from the NFL, please ignore it.
                        """
                    ),
                    "transcribed_text": transcript.text
                }
                
                response_text_bad = return_important_info(prompt)
                response_text = response_text_bad.strip().strip('```json').strip()

                if not response_text:
                    print(f"The response text for {file_name} is empty or invalid.")
                    continue

                try:
                    insights_data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    print(f"Failed to decode JSON for {file_name}: {e}")
                    continue

                connection = connect_to_db()
                cursor = connection.cursor()

                for insight in insights_data:

                    if not all([insight.get('insight'), insight.get('team'), insight.get('context')]):
                        print(f"Skipping incomplete insight: {insight}")
                        continue

                    query = """
                    INSERT INTO insights (insight, team, player, context, date_added)
                    VALUES (%s, %s, %s, %s, CURDATE())
                    """
                    values = (
                        insight.get('insight', None),
                        insight.get('team', None),
                        insight.get('player', None),
                        insight.get('context', None)
                    )
                    cursor.execute(query, values)

                connection.commit()
                connection.close()
                
                print(f"Data for {file_name} has been successfully inserted into the MySQL database.")
                mark_file_as_processed(file_name)

if __name__ == "__main__":
    process_audio_files()