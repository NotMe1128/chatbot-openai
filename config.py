import os
import dotenv

dotenv.load_dotenv('tokens.env')

OPEN_AI_KEY=os.getenv('OPENAI_KEY',None)