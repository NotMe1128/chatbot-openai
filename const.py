from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine

def check_eligibility(age: int, email:str) -> str:
    if age>18 and email.endswith('@gmail.com'):
        return "This user is eligible"
    else:
        reasons=[]
        if age<18:
            reasons.append("user is under 18")
        if not email.endswith('@gmail.com'):
            reasons.append("Email is not gmail")
        return f"This user is not eligible:{', '.join(reasons)}"
    
tools=[
    {
        "type":"function",
        "function":{
            "name":"check_eligibility",
            "description":"Validate the users age and email address to check if they are eligible",
            "parameters":{
                "type":"object",
                "properties":{
                    "age":{"type":"integer", "description":"Users age"},
                    "email":{"type":"string", "description":"Users Email"}},
                "required":["age","email"],
            }
        }
            
    }
    
]

email_pattern= Pattern(name="email_pattern", regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", score=0.9)
email_recognizer = PatternRecognizer(supported_entity="EMAIL_ADDRESS",name="email_recognizer", patterns=[email_pattern])

analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(email_recognizer)
anonymizer= AnonymizerEngine()

def mask(text: str):
    analyzer_results=analyzer.analyze(text=text, language='en')
    anonymized_result=anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results
    )
    
    pii_stored_data = {item.entity_type: text[item.start:item.end] for item in analyzer_results}
    return anonymized_result.text, pii_stored_data


def unmask(masked_text: str, pii_data: dict):
    unmasked_text=masked_text
    for entity_type, original_value in pii_data.items():
        unmasked_text= unmasked_text.replace(f"<{entity_type}>", original_value)
    return unmasked_text

if __name__=='__main__':
    masked, pii = mask("This is Elon Musk and his email is elon1342@gmail.com")
    print(masked) 
    print(pii)     

    print(unmask(masked, pii))