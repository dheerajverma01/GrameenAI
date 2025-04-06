# GrameenAI - Rural Advisor Bot

GrameenAI is a multi-language chatbot designed specifically for rural communities and farmers. It provides agricultural advice, information about government schemes, and more in multiple Indian languages.

## Features

- **Multi-language Support**: Communicate in 10+ Indian languages including Hindi, Tamil, Bengali, Telugu, Kannada, Malayalam, Gujarati, Marathi, Punjabi, and Odia.
- **Agricultural Information**: Get advice on farming techniques, crop management, and agricultural best practices.
- **Government Schemes**: Learn about relevant government agricultural schemes and subsidies.
- **Community Forum**: Connect with other farmers and share experiences.

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/GrameenAI.git
cd GrameenAI
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Set your OpenAI API key in the `app.py` file:
```python
import os
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OpenAI API key not found in environment variables")
```

4. Run the application:
```
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Select your preferred language from the dropdown menu.
2. Type your question in the text box or use the voice input button to speak your question.
3. Click the "Ask" button to get a response.
4. Use the "Speak" button next to each bot response to listen to it.
5. Use the feature buttons to quickly access common information like weather, market prices, etc.

## Technologies Used

- Flask: Web framework
- OpenAI API: For generating responses
- SpeechRecognition: For converting speech to text
- gTTS (Google Text-to-Speech): For converting text to speech
- HTML/CSS/JavaScript: For the frontend interface

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 