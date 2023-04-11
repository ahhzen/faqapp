Simple Question & Answering web app by feeding GPT-index the text data

Directly Run Flask
- Python3 faq.py

Docker Deployment
1. docker build -t faqapp .
2. docker run -p 5005:5005 -e OPENAI_API_KEY = "KEY HERE" faqapp 