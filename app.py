from flask import Flask, render_template, request, session, redirect, url_for
import openai
import os
from langdetect import detect
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Set your OpenAI API key here
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OpenAI API key not found in environment variables")

# Dictionary of Indian languages and their codes
INDIAN_LANGUAGES = {
    'hi': 'Hindi',
    'ta': 'Tamil',
    'bn': 'Bengali',
    'te': 'Telugu',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'gu': 'Gujarati',
    'mr': 'Marathi',
    'pa': 'Punjabi',
    'or': 'Odia'
}

# UI text translations
UI_TRANSLATIONS = {
    'en': {
        'title': 'GrameenAI - Rural Advisor Bot',
        'welcome': 'Welcome! Ask me any question about farming, agriculture, or rural development.',
        'multi_language': 'Multi-Language Support',
        'language_support': 'Ask your questions in any of these languages, and the bot will respond in the same language:',
        'ask_button': 'Ask',
        'clear_chat': 'Clear Chat',
        'type_question': 'Type your question here...',
        'you': 'You',
        'bot': 'Bot',
        'error': 'Error',
        'change_language': 'Change Language',
        'suggested_questions': 'Suggested Questions',
        'crops_farming': 'Crops & Farming',
        'top_crops': 'What are the top crops to grow in my region?',
        'organic_farming': 'How can I start organic farming?',
        'increase_yield': 'How can I increase my crop yield?',
        'rice_pests': 'How to protect rice from pests?',
        'weather_climate': 'Weather & Climate',
        'climate_change': 'How is climate change affecting farming?',
        'monsoon_crops': 'Which crops are best for monsoon season?',
        'protect_crops': 'How to protect crops from extreme weather?',
        'government_support': 'Government Support',
        'small_farmers': 'What government schemes are available for small farmers?',
        'agricultural_loans': 'How can I get agricultural loans?',
        'farming_equipment': 'Are there subsidies for farming equipment?',
        'technology_innovation': 'Technology & Innovation',
        'mobile_apps': 'What mobile apps can help farmers?',
        'precision_farming': 'What is precision farming?',
        'drip_irrigation': 'How to implement drip irrigation?'
    },
    'hi': {
        'title': 'ग्रामीणएआई - ग्रामीण सलाहकार बॉट',
        'welcome': 'स्वागत है! कृषि, किसानी या ग्रामीण विकास के बारे में कोई भी प्रश्न पूछें।',
        'multi_language': 'बहु-भाषा समर्थन',
        'language_support': 'इनमें से किसी भी भाषा में प्रश्न पूछें, और बॉट उसी भाषा में उत्तर देगा:',
        'ask_button': 'पूछें',
        'clear_chat': 'चैट साफ़ करें',
        'type_question': 'अपना प्रश्न यहाँ टाइप करें...',
        'you': 'आप',
        'bot': 'बॉट',
        'error': 'त्रुटि',
        'change_language': 'भाषा बदलें',
        'suggested_questions': 'सुझाए गए प्रश्न',
        'crops_farming': 'फसलें और कृषि',
        'top_crops': 'मेरे क्षेत्र में कौन सी फसलें उगानी चाहिए?',
        'organic_farming': 'जैविक खेती कैसे शुरू करें?',
        'increase_yield': 'फसल की पैदावार कैसे बढ़ाएं?',
        'rice_pests': 'चावल को कीटों से कैसे बचाएं?',
        'weather_climate': 'मौसम और जलवायु',
        'climate_change': 'जलवायु परिवर्तन खेती को कैसे प्रभावित कर रहा है?',
        'monsoon_crops': 'मानसून के मौसम में कौन सी फसलें सबसे अच्छी हैं?',
        'protect_crops': 'अत्यधिक मौसम से फसलों को कैसे बचाएं?',
        'government_support': 'सरकारी सहायता',
        'small_farmers': 'छोटे किसानों के लिए कौन सी सरकारी योजनाएं उपलब्ध हैं?',
        'agricultural_loans': 'कृषि ऋण कैसे प्राप्त करें?',
        'farming_equipment': 'क्या कृषि उपकरणों के लिए सब्सिडी है?',
        'technology_innovation': 'प्रौद्योगिकी और नवाचार',
        'mobile_apps': 'किसानों की मदद के लिए कौन से मोबाइल ऐप हैं?',
        'precision_farming': 'सटीक खेती क्या है?',
        'drip_irrigation': 'ड्रिप सिंचाई कैसे लागू करें?'
    },
    'ta': {
        'title': 'கிராமீன்ஏஐ - கிராம ஆலோசகர் பாட்',
        'welcome': 'வரவேற்கிறோம்! விவசாயம், வேளாண்மை அல்லது கிராமீண மேம்பாடு பற்றி எந்த கேள்வியையும் கேளுங்கள்.',
        'multi_language': 'பல மொழி ஆதரவு',
        'language_support': 'இந்த மொழிகளில் ஏதேனும் ஒன்றில் கேள்விகளை கேளுங்கள், பாட் அதே மொழியில் பதிலளிக்கும்:',
        'ask_button': 'கேளுங்கள்',
        'clear_chat': 'அரட்டையை அழி',
        'type_question': 'உங்கள் கேள்வியை இங்கே டைப் செய்யவும்...',
        'you': 'நீங்கள்',
        'bot': 'பாட்',
        'error': 'பிழை',
        'change_language': 'மொழியை மாற்றவும்',
        'suggested_questions': 'பரிந்துரைக்கப்பட்ட கேள்விகள்',
        'crops_farming': 'பயிர்கள் & விவசாயம்',
        'top_crops': 'எனது பகுதியில் வளர்க்க வேண்டிய சிறந்த பயிர்கள் என்ன?',
        'organic_farming': 'கரிம விவசாயத்தை எப்படி தொடங்குவது?',
        'increase_yield': 'பயிர் மகசூலை எப்படி அதிகரிப்பது?',
        'rice_pests': 'நெல்லை பூச்சிகளிலிருந்து எப்படி ரக்ஷித்துவது?',
        'weather_climate': 'வானிலை & காலநிலை',
        'climate_change': 'காலநிலை மாற்றம் விவசாயத்தை எப்படி பாதிக்கிறது?',
        'monsoon_crops': 'மழைக்காலத்திற்கு சிறந்த பயிர்கள் எவை?',
        'protect_crops': 'தீவிர வானிலையிலிருந்து பயிர்களை எப்படி பாதுகாக்குவது?',
        'government_support': 'அரசு ஆதரவு',
        'small_farmers': 'சிறு குடிகளுக்கு என்ன அரசு திட்டங்கள் கிடைக்கின்றன?',
        'agricultural_loans': 'குடிகள் குடன் எப்படி பெறுவது?',
        'farming_equipment': 'குடிகள் உபகரணங்கள் எப்படி பெறுவது?',
        'technology_innovation': 'தொழில்நுட்பம் & நவீனத்தின்',
        'mobile_apps': 'குடிகள் மேல் என்ன மொபைல் பயன்பாடுகள் உள்ளன?',
        'precision_farming': 'புள்ளியியல் முடியல் என்றால் என்ன?',
        'drip_irrigation': 'ட்ரிப் நீர் பாருங்கள் எப்படி அமலமாக்குவது?'
    },
    'bn': {
        'title': 'গ্রামীনAI - গ্রামীণ উপদেষ্টা বট',
        'welcome': 'স্বাগতম! কৃষি, চাষাবাদ বা গ্রামীণ উন্নয়ন সম্পর্কে যেকোনো প্রশ্ন জিজ্ঞাসা করুন।',
        'multi_language': 'বহু-ভাষা সমর্থন',
        'language_support': 'এই ভাষাগুলির যেকোনো একটি ভাষায় প্রশ্ন করুন, এবং বট একই ভাষায় উত্তর দেবে:',
        'ask_button': 'জিজ্ঞাসা করুন',
        'clear_chat': 'চ্যাট মুছুন',
        'type_question': 'আপনার প্রশ্ন এখানে টাইপ করুন...',
        'you': 'আপনি',
        'bot': 'বট',
        'error': 'ত্রুটি',
        'change_language': 'ভাষা পরিবর্তন করুন',
        'suggested_questions': 'সাজেস্টেড প্রশ্ন',
        'crops_farming': 'ফসল ও কৃষি',
        'top_crops': 'আমার অঞ্চলে চাষের জন্য সেরা ফসলগুলি কী?',
        'organic_farming': 'জৈব চাষ কীভাবে শুরু করব?',
        'increase_yield': 'ফসলের ফলন কীভাবে বাড়াব?',
        'rice_pests': 'ধান কীটপতঙ্গ থেকে কীভাবে রক্ষা করব?',
        'weather_climate': 'আবহাওয়া ও জল঵ায়ু',
        'climate_change': 'জল঵ায়ু পরিবর্তন খেতীবাদী নেয়া কীভাবে প্রভাবিত করছে?',
        'monsoon_crops': 'মানসূন লয়ত্ত্বের জন্য সেরা ফসলগুলি কী?',
        'protect_crops': 'চরম মানসূনত্বের পাশাপাশি ফসলগুলি কীভাবে রক্ষা করব?',
        'government_support': 'সরকারি সহায়তা',
        'small_farmers': 'ছোট কৃষকদের জন্য কী কী সরকারি যোজনা উপলব্ধ হয়?',
        'agricultural_loans': 'কৃষি ঋণ কীভাবে পাওয়া যাবে?',
        'farming_equipment': 'কৃষি উপকরণগুলির জন্য সবসিডি আছে কি?',
        'technology_innovation': 'প্রযুক্তি ও নবাচার',
        'mobile_apps': 'কৃষকদের সাহায্য করার জন্য কী কী মোবাইল অ্যাপ আছে?',
        'precision_farming': 'প্রিসিশন ফার্মিং কী?',
        'drip_irrigation': 'ড্রিপ সিংচায়ন কীভাবে লাগানো যায়?'
    },
    'te': {
        'title': 'గ్రామీన్AI - గ్రామీణ సలహాదార బాట్',
        'welcome': 'స్వాగతం! వ్యవసాయం, వ్యవసాయం లేదా గ్రామీణ అభివృద్ధి గురించి ఏదైనా ప్రశ్న అడగండి.',
        'multi_language': 'బహుళ-భాషా మద్దతు',
        'language_support': 'ఈ భాషలలో ఏదైనా ఒక భాషలో ప్రశ్నలు అడగండి, మరియు బాట్ అదే భాషలో సమాధానం ఇస్తుంది:',
        'ask_button': 'అడగండి',
        'clear_chat': 'చాట్ క్లియర్ చేయండి',
        'type_question': 'మీ ప్రశ్నను ఇక్కడ టైప్ చేయండి...',
        'you': 'మీరు',
        'bot': 'బాట్',
        'error': 'లోపం',
        'change_language': 'భాష మార్చండి',
        'suggested_questions': 'సూచించిన ప్రశ్నలు',
        'crops_farming': 'పంటలు & వ్యవసాయం',
        'top_crops': 'నా ప్రాంతంలో పండించడానికి ఉత్తమమైన పంటలు ఏమిటి?',
        'organic_farming': 'సేంద్రీయ వ్యవసాయాన్ని ఎలా ప్రారంభించాలి?',
        'increase_yield': 'పంట దిగుబడిని ఎలా పెంచాలి?',
        'rice_pests': 'వరిని పీడల నుండి ఎలా రక్షించాలి?',
        'weather_climate': 'వాతావరణం & వాతావరణం',
        'climate_change': 'వాతావరణ మార్పులు వ్యవసాయాన్ని ఎలా ప్రభావితం చేస్తున్నాయి?',
        'monsoon_crops': 'మళ్ళీ కాలానికి ఉత్తమమైన పంటలు ఏమిటి?',
        'protect_crops': 'తీవ్ర వాతావరణం నుండి పంటలను ఎలా రక్షించాలి?',
        'government_support': 'ప్రభుత్వ మద్దతు',
        'small_farmers': 'చిన్న రైతులకు ఏ ప్రభుత్వ పథకాలు అందుబాటులో ఉన్నాయి?',
        'agricultural_loans': 'వ్యవసాయ రుణాలను ఎలా పొందాలి?',
        'farming_equipment': 'వ్యవసాయ పరికరాలకు సబ్సిడీలు ఉన్నాయా?',
        'technology_innovation': 'సాంకేతిక పరిజ్ఞానం & ఆవిష్కరణ',
        'mobile_apps': 'రైతులకు ఏ మొబైల్ యాప్‌లు సహాయపడతాయి?',
        'precision_farming': 'ప్రిసిషన్ ఫార్మింగ్ అంటే ఏమిటి?',
        'drip_irrigation': 'డ్రిప్ నీరు పారుదలను ఎలా అమలు చేయాలి?'
    },
    'kn': {
        'title': 'ಗ್ರಾಮೀಣAI - ಗ್ರಾಮೀಣ ಸಲಹೆಗಾರ ಬಾಟ್',
        'welcome': 'ಸ್ವಾಗತ! ಕೃಷಿ, ವ್ಯವಸಾಯ ಅಥವಾ ಗ್ರಾಮೀಣ ಅಭಿವೃದ್ಧಿಯ ಬಗ್ಗೆ ಯಾವುದೇ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಿ.',
        'multi_language': 'ಬಹು-ಭಾಷೆ ಬೆಂಬಲ',
        'language_support': 'ಈ ಭಾಷೆಗಳಲ್ಲಿ ಯಾವುದೇ ಒಂದು ಭಾಷೆಯಲ್ಲಿ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಿ, ಮತ್ತು ಬಾಟ್ ಅದೇ ಭಾಷೆಯಲ್ಲಿ ಉತ್ತರಿಸುತ್ತದೆ:',
        'ask_button': 'ಕೇಳಿ',
        'clear_chat': 'ಚಾಟ್ ಕ್ಲೀನ್ ಮಾಡಿ',
        'type_question': 'ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ...',
        'you': 'ನೀವು',
        'bot': 'ಬಾಟ್',
        'error': 'ದೋಷ',
        'change_language': 'ಭಾಷೆ ಬದಲಾಯಿಸಿ',
        'suggested_questions': 'ಸೂಚಿಸಿದ ಪ್ರಶ್ನೆಗಳು',
        'crops_farming': 'ಬೆಳೆಗಳು & ಕೃಷಿ',
        'top_crops': 'ನನ್ನ ಪ್ರದೇಶದಲ್ಲಿ ಬೆಳೆಯಲು ಉತ್ತಮ ಬೆಳೆಗಳು ಯಾವುವು?',
        'organic_farming': 'ಸಾವಯವ ಕೃಷಿಯನ್ನು ಹೇಗೆ ಪ్ರಾರಂಭಿಸಬೇಕು?',
        'increase_yield': 'ಬೆಳೆಯ ಇಳುವರಿಯನ್ನು ಹೇಗೆ ಹೆಚ್ಚಿಸಬೇಕು?',
        'rice_pests': 'ಭತ್ತವನ್ನು ಕೀಟಗಳಿಂದ ಎಲಾ ರಕ್ಷಿಸಬೇಕು?',
        'weather_climate': 'ವಾತಾವರಣ ಮತ್ತು ವಾತಾವರಣ',
        'climate_change': 'ವಾತಾವರಣ ಮಾರ್ಪುಲ್ಗಳು ಕೃಷಿಯನ್ನು ಎಲಾ ಪ్ರಭಾವಿತಂ ಚೇಸುತ್ತಿದೆ?',
        'monsoon_crops': 'ಮಳೆಗಾಲಕ್ಕೆ ಉತ್ತು ಬೆಳೆಗಳು ಯಾವುವು?',
        'protect_crops': 'ತೀವ್ರ ವಾತಾವರಣದಿಂದ ಬೆಳೆಗಳನ್ನು ಎಲಾ ರಕ್ಷಿಸಬೇಕು?',
        'government_support': 'ಸರ್ಕಾರಿ ಸಹಾಯ',
        'small_farmers': 'ಚೆಱು ರೈತುಗಳಿಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಉಪಲಬ್ಧ ಇವೆ?',
        'agricultural_loans': 'ಕೃಷಿ ಲೋನ ಎಲಾ ಪೊಂದಾಲ್ಯ ಇದೆ?',
        'farming_equipment': 'ಕೃಷಿ ಉಪಕರಣಗಳಿಗೆ ಸಬ್ಸಿಡಿಗಳು ಉಣ್ಟೋ?',
        'technology_innovation': 'ತಂತ್ರಜ್ಞಾನ ಮತ್ತು ನವೀನತೆ',
        'mobile_apps': 'ರೈತುಗಳಿಗೆ ಯಾವ ಮೊಬೈಲ್ ಅಪ್ಲಿಕೇಶನ್‌ಗಳು ಸಹಾಯಪಡತಾಯಿ?',
        'precision_farming': 'ಪ್ರಿಸಿಷನ್ ಫಾರ್ಮಿಂಗ್ ಎಂದರೇನು?',
        'drip_irrigation': 'ಡ್ರಿಪ್ ಸಿಂಚಾಈ ಎಲಾ ಅಮಲಮಾಡಬೇಕು?'
    },
    'ml': {
        'title': 'ഗ്രാമീൻAI - ഗ്രാമീണ ഉപദേശക ബോട്ട്',
        'welcome': 'സ്വാഗതം! കൃഷി, കാർഷികം അല്ലെങ്കിൽ ഗ്രാമീണ വികസനത്തെക്കുറിച്ച് ഏതെങ്കിലും ചോദ്യം ചോദിക്കുക.',
        'multi_language': 'ബഹുഭാഷാ പിന്തുണ',
        'language_support': 'ഈ ഭാഷകളിൽ ഏതെങ്കിലും ഒന്നിൽ ചോദ്യങ്ങൾ ചോദിക്കുക, ബോട്ട് അതേ ഭാഷയിൽ മറുപടി നൽകും:',
        'ask_button': 'ചോദിക്കുക',
        'clear_chat': 'ചാറ്റ് മായ്ക്കുക',
        'type_question': 'നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക...',
        'you': 'നിങ്ങൾ',
        'bot': 'ബോട്ട്',
        'error': 'പിശക്',
        'change_language': 'ഭാഷ മാറ്റുക',
        'suggested_questions': 'നിർദ്ദേശിച്ച ചോദ്യങ്ങൾ',
        'crops_farming': 'വിളകളും കൃഷിയും',
        'top_crops': 'എന്റെ മേഖലയിൽ വളർത്താൻ മികച്ച വിളകൾ ഏതൊക്കെ?',
        'organic_farming': 'ജൈവ കൃഷി എങ്ങനെ ആരംഭിക്കാം?',
        'increase_yield': 'വിളവ് എങ്ങനെ വർദ്ധിപ്പിക്കാം?',
        'rice_pests': 'നെല്ലിനെ കീടങ്ങളിൽ നിന്ന് എങ്ങനെ പരിരക്ഷിക്കാം?',
        'weather_climate': 'കാലാവസ്ഥയും കാലാവസ്ഥയും',
        'climate_change': 'കാലാവസ്ഥ മാറ്റം കൃഷിയെ എങ്ങനെ ബാധിക്കുന്നു?',
        'monsoon_crops': 'മഴുന്ന കാലത്തിന് മികച്ച വിളകൾ ഏതൊക്കെ?',
        'protect_crops': 'തീവ്ര കാലാവസ്ഥയിൽ നിന്ന് വിളകളെ എങ്ങനെ പരിരക്ഷിക്കാം?',
        'government_support': 'സർക്കാർ പിന്തുണ',
        'small_farmers': 'ചെറു രൈതുകൾക്ക് ഏതെല്ലാം സർക്കാർ പദ്ധതികൾ ലഭ്യമാണ്?',
        'agricultural_loans': 'കൃഷി വായ്പകൾ എങ്ങനെ നേടാം?',
        'farming_equipment': 'കൃഷി ഉപകരണങ്ങൾക്ക് സബ്സിഡികൾ ഉണ്ടോ?',
        'technology_innovation': 'സാങ്കേതിക പരിജ്ഞാനം & നവീനത',
        'mobile_apps': 'രൈതുകൾക്ക് ഏതെല്ലാം മൊബൈൽ ആപ്പുകൾ സഹായിക്കും?',
        'precision_farming': 'പ്രിസിഷൻ ഫാര്മിംഗ് എന്താണ്?',
        'drip_irrigation': 'ഡ്രിപ്പ് നീരൊഴുക്ക് എങ്ങനെ നടപ്പിലാക്കാം?'
    },
    'gu': {
        'title': 'ગ્રામીણAI - ગ્રામીણ સલાહકાર બોટ',
        'welcome': 'સ્વાગત છે! ખેતી, કૃષિ અથવા ગ્રામીણ વિકાસ વિશે કોઈપણ પ્રશ્ન પૂછો.',
        'multi_language': 'બહુ-ભાષા સપોર્ટ',
        'language_support': 'આ ભાષાઓમાંથી કોઈપણ એક ભાષામાં પ્રશ્નો પૂછો, અને બોટ તે જ ભાષામાં જવાબ આપશે:',
        'ask_button': 'પૂછો',
        'clear_chat': 'ચેટ સાફ કરો',
        'type_question': 'તમારો પ્રશ્ન અહીં ટೈપ કરો...',
        'you': 'તમે',
        'bot': 'બોટ',
        'error': 'ભૂલ',
        'change_language': 'ભાષા બદલો',
        'suggested_questions': 'સૂચવેલા પ્રશ્નો',
        'crops_farming': 'પાક અને ખેતી',
        'top_crops': 'મારા પ્રદેશમાં ઉગાડવા લાવણ લાવણ કયા છે?',
        'organic_farming': 'જੈવિક ખેતી કੇવੀ રੀતੇ શરੂ કરੀએ?',
        'increase_yield': 'પાકની ઉત્પાદકતા કੇવੀ રੀતੇ વધાવાવੀ?',
        'rice_pests': 'ધાનકુ પોક મારિ કੇવੀ રੀતੇ બચાવાવੀ?',
        'weather_climate': 'મોસમ અને જલવાયੂ',
        'climate_change': 'મોસમ પરિવર્તન ખેતીબાદી નੇટાવੀ?',
        'monsoon_crops': 'માનસૂન લાવણ લાવણ કયા છે?',
        'protect_crops': 'ચરમ મોસમ તੋં ફસલ કੇવੀ રੀતੇ બચાવાવੀ?',
        'government_support': 'સરકારી સહાય',
        'small_farmers': 'છોટા કુટીકાં લાવણ લાવણ કયા છે?',
        'agricultural_loans': 'કુટીકાં લોન કੇવੀ રੀતੇ પାવੀ?',
        'farming_equipment': 'ખેતીબાદી ઉપકરણ પાઇવੀ?',
        'technology_innovation': 'તંત્રજ્ઞાન અને નવીનતા',
        'mobile_apps': 'કુટીકાં મોબાઇલ અપ્લિકેશનો કયા છે?',
        'precision_farming': 'પ્રિસિશન ફાર્મિંગ શੁં છે?',
        'drip_irrigation': 'ડ્રિપ સિંચાઈ કੇવੀ રੀતੇ લાવੀ?'
    },
    'mr': {
        'title': 'ग्रामीणAI - ग्रामीण सलाहकार बॉट',
        'welcome': 'स्वागत आहे! शेती, कृषी किंवा ग्रामीण विकासाबद्दल कोणताही प्रश्न विचारा.',
        'multi_language': 'बहु-भाषा समर्थन',
        'language_support': 'या भाषांपैकी कोणत्याही भाषेत प्रश्न विचारा, आणि बॉट त्याच भाषेत उत्तर देईल:',
        'ask_button': 'विचारा',
        'clear_chat': 'चॅट साफ करा',
        'type_question': 'तुमचा प्रश्न येथे टाइप करा...',
        'you': 'तुम्ही',
        'bot': 'बॉट',
        'error': 'त्रुटी',
        'change_language': 'भाषा बदला',
        'suggested_questions': 'सुचवलेले प्रश्न',
        'crops_farming': 'पिके आणि शेती',
        'top_crops': 'माझ्या प्रदेशात लावण्यासाठी सर्वोत्तम पिके कोणती?',
        'organic_farming': 'जैविक शेती कशी सुरू करावी?',
        'increase_yield': 'पिकाची उत्पादकता कशी वाढवावी?',
        'rice_pests': 'तांदळाला कीटकांपासून कसे बचावी?',
        'weather_climate': 'मोसम आणि जलवायू',
        'climate_change': 'मोसम परिवर्तन शेतीवर कसा प्रभावित करतो?',
        'monsoon_crops': 'मानसून लावण्यासाठी सर्वोत्तम पिके कोणती?',
        'protect_crops': 'चरम मोसम तों फसल कोणती बचावी?',
        'government_support': 'सरकारी समर्थन',
        'small_farmers': 'लहान शेतकऱ्यांसाठी कोणत्या सरकारी योजना उपलब्ध आहेत?',
        'agricultural_loans': 'शेतकऱ्यां ऋण कसे प्राप्त करावे?',
        'farming_equipment': 'शेतकऱ्यांचे उपकरण प्राप्त करणे कसे होई?',
        'technology_innovation': 'तंत्रज्ञान आणि नवीनता',
        'mobile_apps': 'शेतकऱ्यांना कोणत्या मोबाईल अप्प्यां मदत करणे होई?',
        'precision_farming': 'प्रिसिशन फार्मिंग कसे होई?',
        'drip_irrigation': 'ड्रिप सिंचन कसे लागू करणे होई?'
    },
    'pa': {
        'title': 'ਗਰਾਮੀਨAI - ਪੇਂਡੂ ਸਲਾਹਕਾਰ ਬੋਟ',
        'welcome': 'ਜੀ ਆਇਆਂ ਨੂੰ! ਖੇਤੀਬਾੜੀ, ਕਾਸ਼ਤਕਾਰੀ ਜਾਂ ਪੇਂਡੂ ਵਿਕਾਸ ਬਾਰੇ ਕੋਈ ਵੀ ਸਵਾਲ ਪੁੱਛੋ.',
        'multi_language': 'ਬਹੁ-ਭਾਸ਼ਾ ਸਹਾਇਤਾ',
        'language_support': 'ਇਨ੍ਹਾਂ ਭਾਸ਼ਾਵਾਂ ਵਿੱਚੋਂ ਕਿਸੇ ਵੀ ਭਾਸ਼ਾ ਵਿੱਚ ਸਵਾਲ ਪੁੱਛੋ, ਅਤੇ ਬੋਟ ਉਸੇ ਭਾਸ਼ਾ ਵਿੱਚ ਜਵਾਬ ਦੇਵੇਗਾ:',
        'ask_button': 'ਪੁੱਛੋ',
        'clear_chat': 'ਚੈਟ ਸਾਫ਼ ਕਰੋ',
        'type_question': 'ਆਪਣਾ ਸਵਾਲ ਇੱਥੇ ਟਾਈਪ ਕਰੋ...',
        'you': 'ਤੁਸੀਂ',
        'bot': 'ਬੋਟ',
        'error': 'ਗਲਤੀ',
        'change_language': 'ਭਾਸ਼ਾ ਬਦਲੋ',
        'suggested_questions': 'ਸੁਝਾਏ ਗਏ ਸਵਾਲ',
        'crops_farming': 'ਫਸਲਾਂ ਅਤੇ ਖੇਤੀਬਾੜੀ',
        'top_crops': 'ਮੇਰੇ ਖੇਤਰ ਵਿੱਚ ਉਗਾਉਣ ਲਈ ਸਭ ਤੋਂ ਵਧੀਆ ਫਸਲਾਂ ਕਿਹੜੀਆਂ ਹਨ?',
        'organic_farming': 'ਜੈਵਿਕ ਖੇਤੀਬਾੜੀ ਕਿਵੇਂ ਸ਼ੁਰੂ ਕਰੀਏ?',
        'increase_yield': 'ਫਸਲ ਦੀ ਉਤਪਾਦਨ ਕਿਵੇਂ ਵਧਾਈਏ?',
        'rice_pests': 'ਚੌਲਾਂ ਨੂੰ ਪੋਕ ਮਾਰਿ ਕਿਵੇਂ ਬਚਾਇਆ ਜਾ ਸਕਦਾ ਹੈ?',
        'weather_climate': 'ਮੋਸਮ ਅਤੇ ਜਲਵਾୟୁ',
        'climate_change': 'ਜਲਵਾୟୁ ਪਰਿਵਰਤਨ ਖੇਤੀਬਾੜੀ ਨੂੰ ਕਿਵੇਂ ਪਰਿਭਾਵਿਤ ਕਰ ਰਹੀ ਹੈ?',
        'monsoon_crops': 'ਮਾਨਸੂਨ ਲਈ ਸਭ ਤੋਂ ਵਧੀਆ ਫਸਲਾਂ ਕਿਹੜੀਆਂ ਹਨ?',
        'protect_crops': 'ਚਰਮ ਮੋਸਮ ਤੋਂ ਫਸਲਾਂ ਨੂੰ ਕਿਵੇਂ ਬਚਾਇਆ ਜਾ ਸਕਦਾ ਹੈ?',
        'government_support': 'ਸਰਕਾਰੀ ਸਮਰਥਨ',
        'small_farmers': 'ਛੋਟੇ ਕਿਸਾਨਾਂ ਲਈ ਕਿਹੜੀਆਂ ਸਰਕਾਰੀ ਯੋਜਨਾଗୁଡ଼ିକ ਉਪਲବ୍ଧ ਹਨ?',
        'agricultural_loans': 'ਖੇਤੀਬਾੜੀ ਲੋਨ ਕਿਵੇਂ ਪ੍ਰਾਪਤ ਕੀਤੀਆਂ ਜਾ ਸਕਦੀਆਂ ਹਨ?',
        'farming_equipment': 'ਖੇਤੀਬਾੜੀ ਉਪਕਰਣ ਪਾਇਵੀ?',
        'technology_innovation': 'ਤਂਤਰਜਞਾਨ ਅਤੇ ਨਵੀਨਤਾ',
        'mobile_apps': 'ਕਿਸਾਨਾਂ ਨੂੰ ਕਿਹੜੀਆਂ ਮੋବਾਈਲ ਅਪਾਂ ਮਦਦ ਕਰਵੀ?',
        'precision_farming': 'ਪ੍ਰਿਸਿਜ਼ਨ ਫਾਰਮਿੰਗ ਕੀ ਹੈ?',
        'drip_irrigation': 'ਡ੍ਰਿਪ ਸਿੰਚਾਈ ਕੇਵੀ ਲਾਗੂ ਕਰਵੀ?'
    },
    'or': {
        'title': 'ଗ୍ରାମୀନAI - ଗ୍ରାମୀଣ ପରାମର୍ଶଦାତା ବଟ',
        'welcome': 'ସ୍ୱାଗତ! କୃଷି, ଚାଷ ବା ଗ୍ରାମୀଣ ବିକାଶ ବିଷୟରେ ଯେକୌଣସି ପ୍ରଶ୍ନ ପଚାରନ୍ତୁ।',
        'multi_language': 'ବହୁ-ଭାଷା ସମର୍ଥନ',
        'language_support': 'ଏହି ଭାଷାଗୁଡ଼ିକ ମଧ୍ୟରୁ ଯେକୌଣସି ଏକ ଭାଷାରେ ପ୍ରଶ୍ନ ପଚାରନ୍ତୁ, ଏବଂ ବଟ ସେହି ଭାଷାରେ ଉତ୍ତର ଦେବ:',
        'ask_button': 'ପଚାରନ୍ତୁ',
        'clear_chat': 'ଚାଟ ସଫା କରନ୍ତୁ',
        'type_question': 'ଆପଣଙ୍କ ପ୍ରଶ୍ନ ଏଠାରେ ଟାଇପ୍ କରନ୍ତୁ...',
        'you': 'ଆପଣ',
        'bot': 'ବଟ',
        'error': 'ତ୍ରୁଟି',
        'change_language': 'ଭାଷା ପରିବର୍ତ୍ତନ କରନ୍ତୁ',
        'suggested_questions': 'ସଜେଷ୍ଟେଡ୍ ପ୍ରଶ୍ନଗୁଡ଼ିକ',
        'crops_farming': 'ଫସଲ ଏବଂ କୃଷି',
        'top_crops': 'ମୋ ଅଞ୍ଚଳରେ ଚାଷ କରିବା ପାଇଁ ସର୍ବୋତ୍ତମ ଫସଲଗୁଡ଼ିକ କଯାଣ?',
        'organic_farming': 'ଜୈବିକ ଚାଷ କିପରି ଆରମ୍ଭ କରିବେ?',
        'increase_yield': 'ଫସଲ ଉତ୍ପାଦନ କିପରି ବଢ଼ାଇବେ?',
        'rice_pests': 'ଧାନକୁ ପୋକ ମਾରି କିପରି ବଞ୍ଚାଇବେ?',
        'weather_climate': 'ମୋସମ ଏବଂ ଜଳବାୟୁ',
        'climate_change': 'ଜଳବାୟୁ ପରିବର୍ତ୍ତନ କୃଷିକୁ କିପରି ପ୍ରଭାଵିਤ କରୁଛି?',
        'monsoon_crops': 'ମଳଳାଲାନିକି ଉତ୍ତମ ଫସଲଗୁଡ଼ିକ କଯାଣ?',
        'protect_crops': 'ଚରମ ମୋସମରୁ ଫସଲଗୁଡ଼ିକୁ କିପରି ବଞ୍ଚାଇବେ?',
        'government_support': 'ସରକାରୀ ସମର୍ଥନ',
        'small_farmers': 'ଛୋଟ ଚାଷୀମାନଙ୍କୁ କେଉଁ ସରକାରୀ ଯୋଜନାଗୁଡ଼ିକ ଉପଲବ୍ଧ ହେବେ?',
        'agricultural_loans': 'କୃଷି ଋଣ କିପରି ପାଇପାରିବେ?',
        'farming_equipment': 'କୃଷି ଉପକରਣਾଂ ପାଇଁ ସବସିଡ଼ି ଅଛି କି?',
        'technology_innovation': 'ପ୍ରଯୁକ୍ତି ଏବଂ ନଵୀਨତਾ',
        'mobile_apps': 'ଚାଷୀମାନଙ୍କୁ କେଉଁ ମୋବାଇଲ୍ ଆପ୍‌ଗୁଡ଼ିକ ସହାୟତା କରਵੀ?',
        'precision_farming': 'ପ୍ରିସିଜ਼ਨ୍ ଫାରਮਿଂ କଯାଣ?',
        'drip_irrigation': 'ଡ୍ରਿਪ୍ ସଞ୍ଚୟନ କିପରି ଲାଗୁ କରਵੀ?'
    }
}

# Add more translations for other languages as needed

def detect_language(text):
    """Detect the language of the input text"""
    try:
        lang_code = detect(text)
        return lang_code
    except:
        return 'en'  # Default to English if detection fails

def get_language_instruction(lang_code):
    """Get the appropriate system instruction based on detected language"""
    if lang_code in INDIAN_LANGUAGES:
        return f"Answer in {INDIAN_LANGUAGES[lang_code]}. You are a rural advisor bot for farmers and village communities."
    elif lang_code == 'en':
        return "Answer in English. You are a rural advisor bot for farmers and village communities."
    else:
        return "Answer in the same language as the user's question. You are a rural advisor bot for farmers and village communities."

def get_ui_text(lang_code):
    """Get UI text in the selected language"""
    if lang_code in UI_TRANSLATIONS:
        return UI_TRANSLATIONS[lang_code]
    return UI_TRANSLATIONS['en']  # Default to English

@app.route("/")
def home():
    # Initialize conversation history if it doesn't exist
    if 'conversation' not in session:
        session['conversation'] = []
    
    # Get the selected language or default to English
    selected_lang = session.get('language', 'en')
    ui_text = get_ui_text(selected_lang)
    
    return render_template("index.html", 
                          conversation=session['conversation'],
                          ui_text=ui_text,
                          selected_lang=selected_lang,
                          languages=INDIAN_LANGUAGES)

@app.route("/set_language", methods=["POST"])
def set_language():
    """Set the user's preferred language"""
    selected_lang = request.form.get("language", "en")
    session['language'] = selected_lang
    return redirect(url_for('home'))

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.form["question"]
    reply = ""
    
    # Get the selected language or default to English
    selected_lang = session.get('language', 'en')
    ui_text = get_ui_text(selected_lang)

    try:
        # Use the selected language for the response
        system_instruction = get_language_instruction(selected_lang)
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_input}
            ]
        )

        reply = response.choices[0].message.content.strip()

    except Exception as e:
        reply = f"❌ {ui_text['error']}: {str(e)}"
    
    # Add the new exchange to the conversation history
    if 'conversation' not in session:
        session['conversation'] = []
    
    session['conversation'].append({"user": user_input, "bot": reply})
    # Save the session
    session.modified = True
    
    return render_template("index.html", 
                          conversation=session['conversation'],
                          ui_text=ui_text,
                          selected_lang=selected_lang,
                          languages=INDIAN_LANGUAGES)

@app.route("/clear", methods=["POST"])
def clear():
    # Clear the conversation history
    session['conversation'] = []
    
    # Get the selected language or default to English
    selected_lang = session.get('language', 'en')
    ui_text = get_ui_text(selected_lang)
    
    return render_template("index.html", 
                          conversation=session['conversation'],
                          ui_text=ui_text,
                          selected_lang=selected_lang,
                          languages=INDIAN_LANGUAGES)

if __name__ == "__main__":
    app.run(debug=True)

