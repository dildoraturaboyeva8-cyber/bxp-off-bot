import google.generativeai as genai

genai.configure(api_key="AQ.Ab8RN6I8SxtqQZbn2Ywg53aWRK4J9NkYO_16fuLKIiQa8ZKTTA")

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
