"""
Medical Client for handling AI model interactions
Supports both Gemini and AWS Nova models
"""

import os
import asyncio
from typing import Optional, List
import json

class MedicalClient:
    def __init__(self):
        self.model_type = os.getenv("MEDICAL_MODEL", "gemini").lower()
        self._setup_client()
    
    def _setup_client(self):
        """Initialize the appropriate AI client based on configuration."""
        if self.model_type == "gemini":
            self._setup_gemini()
        elif self.model_type == "nova":
            self._setup_nova()
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def _setup_gemini(self):
        """Setup Gemini client."""
        try:
            import google.generativeai as genai
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment")
            
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel('gemini-1.5-flash')
            self.client_type = "gemini"
        except ImportError:
            raise ImportError("google-generativeai package not installed")
    
    def _setup_nova(self):
        """Setup AWS Nova client."""
        try:
            import boto3
            self.client = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_REGION", "us-east-1")
            )
            self.client_type = "nova"
        except ImportError:
            raise ImportError("boto3 package not installed")
    
    def _get_medical_prompt_prefix(self) -> str:
        """Get the standard medical prompt prefix."""
        return  """You are a medical data assistant for healthcare professionals. Your role is to organize, summarize, and display medical information in a clear, structured format. Do not make clinical decisions or recommendations.

Focus on:
- Organizing patient data into clear, readable formats
- Summarizing previous checkups, diagnoses, and test results
- Calculating and displaying averages for vital signs and health metrics
- Presenting information in tables, lists, or other structured markdown formats
- Being concise and factual

Use proper markdown formatting including tables when displaying structured data. Present facts objectively without clinical interpretation or recommendations.

"""
    
    async def query_medical_question(self, question: str, context: str = "") -> str:
        """Query the AI model with a medical question."""
        prompt = self._get_medical_prompt_prefix()
        prompt += f"Question: {question}\n"
        if context:
            prompt += f"Additional context: {context}\n"
        prompt += "\nPlease provide a comprehensive, professional response:"
        
        if self.client_type == "gemini":
            return await self._query_gemini(prompt)
        elif self.client_type == "nova":
            return await self._query_nova(prompt)
    
    async def analyze_symptoms(self, symptoms: List[str], age: Optional[int] = None, gender: Optional[str] = None) -> str:
        """Analyze symptoms and provide general guidance."""
        prompt = self._get_medical_prompt_prefix()
        prompt += "Please analyze the following symptoms and provide general guidance:\n\n"
        prompt += f"Symptoms: {', '.join(symptoms)}\n"
        
        if age:
            prompt += f"Age: {age}\n"
        if gender:
            prompt += f"Gender: {gender}\n"
        
        prompt += "\nProvide:\n"
        prompt += "1. Possible general categories these symptoms might fall under\n"
        prompt += "2. When to seek medical attention\n"
        prompt += "3. General self-care measures (if appropriate)\n"
        prompt += "4. Red flags that require immediate medical attention\n"
        
        if self.client_type == "gemini":
            return await self._query_gemini(prompt)
        elif self.client_type == "nova":
            return await self._query_nova(prompt)
    
    async def _query_gemini(self, prompt: str) -> str:
        """Query Gemini model."""
        try:
            response = await asyncio.to_thread(
                self.client.generate_content, prompt
            )
            return response.text
        except Exception as e:
            return f"Error querying Gemini: {str(e)}"
    
    async def _query_nova(self, prompt: str) -> str:
        """Query AWS Nova model."""
        try:
            body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 2048,
                    "temperature": 0.3,
                    "topP": 0.9
                }
            })
            
            response = await asyncio.to_thread(
                self.client.invoke_model,
                body=body,
                modelId="amazon.nova-micro-v1:0",
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body.get('outputText', 'No response generated')
            
        except Exception as e:
            return f"Error querying Nova: {str(e)}"