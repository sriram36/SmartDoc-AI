import os
import re
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral:7b"

def test_ollama_connection():
    """Test Ollama connection and model availability"""
    try:
        # Check if Ollama is running
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            
            if OLLAMA_MODEL in model_names:
                return True, f"Ollama connected - Mistral 7B available"
            else:
                return False, f"Ollama connected, but {OLLAMA_MODEL} not found. Available models: {model_names}"
        else:
            return False, f"Ollama responded with status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return False, "Ollama not running. Start with: ollama serve"
    except Exception as e:
        return False, f"Ollama connection error: {str(e)}"

def ollama_document_summary(document_text: str, length: str = "medium") -> dict:
    """
    Generate a summary using Ollama with Mistral 7B
    
    Args:
        document_text: The text content of the document
        length: Summary length - "short", "medium", or "long"
    
    Returns:
        dict containing the summary text and metadata
    """
    
    # Validate inputs
    if not document_text or not document_text.strip():
        return {
            "summary": "No document text provided for summarization.",
            "status": "error", 
            "length": length
        }
    
    # Check Ollama connection
    is_connected, message = test_ollama_connection()
    if not is_connected:
        return {
            "summary": f"Ollama not available: {message}",
            "status": "error",
            "length": length
        }
    
    # Validate length parameter
    valid_lengths = ["short", "medium", "long"]
    if length not in valid_lengths:
        length = "medium"  # Default fallback
    
    # Define length instructions
    length_instructions = {
        "short": "Provide a concise summary in 2-3 sentences highlighting only the most important points.",
        "medium": "Provide a comprehensive summary in 1-2 paragraphs covering the main topics and key details.",
        "long": "Provide a detailed summary with multiple paragraphs, covering all significant points, arguments, conclusions, and supporting details."
    }
    
    instruction = length_instructions.get(length, length_instructions["medium"])
    
    # Create the prompt
    prompt = f"""Please analyze and summarize the following document. {instruction}

Focus on:
- Main topics and themes
- Key findings or conclusions  
- Important details and data
- Overall purpose and context

Document Text:
{document_text}

Please provide a clear, well-structured summary:"""

    try:
        # Make request to Ollama
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more consistent summaries
                "num_predict": 1000 if length == "long" else 500 if length == "medium" else 200
            }
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=60  # Generous timeout for local processing
        )
        
        if response.status_code == 200:
            result = response.json()
            summary_text = result.get("response", "").strip()
            
            if summary_text:
                return {
                    "summary": summary_text,
                    "status": "success",
                    "length": length,
                    "model_used": f"ollama/{OLLAMA_MODEL}",
                    "tokens_used": result.get("eval_count", 0),
                    "processing_time": result.get("total_duration", 0) / 1000000000  # Convert to seconds
                }
            else:
                return {
                    "summary": "Ollama returned empty response",
                    "status": "error",
                    "length": length
                }
        else:
            return {
                "summary": f"Ollama request failed with status {response.status_code}: {response.text}",
                "status": "error",
                "length": length
            }
            
    except requests.exceptions.Timeout:
        return {
            "summary": "Ollama request timed out - the model might be processing a large document",
            "status": "error",
            "length": length
        }
    except Exception as e:
        return {
            "summary": f"Error connecting to Ollama: {str(e)}",
            "status": "error",
            "length": length
        }

# Hugging Face availability (set to False since we're not using it)
HF_AVAILABLE = False
summarizer = None

def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        if not client:
            return False, "OpenAI API key not configured"
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=10
        )
        return True, "Connected successfully"
    except Exception as e:
        return False, str(e)

def huggingface_document_summary(document_text: str, length: str = "medium") -> dict:
    """
    Generate a summary using Hugging Face transformers (free alternative)
    
    Args:
        document_text: The text content of the document
        length: Summary length - "short", "medium", or "long"
    
    Returns:
        dict containing the summary text and metadata
    """
    
    # Validate inputs
    if not document_text or not document_text.strip():
        return {
            "summary": "No document text provided for summarization.",
            "status": "error", 
            "length": length
        }
    
    if not HF_AVAILABLE or not summarizer:
        return {
            "summary": "Hugging Face summarization model not available. Please install: pip install transformers torch",
            "status": "error",
            "length": length
        }
    
    # Validate length parameter
    valid_lengths = ["short", "medium", "long"]
    if length not in valid_lengths:
        length = "medium"  # Default fallback
    
    try:
        # Clean and prepare text
        text = re.sub(r'\s+', ' ', document_text.strip())
        
        # BART model has token limits, so we may need to chunk long documents
        max_input_length = 1024  # BART's max input length
        
        # Split text into chunks if too long
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1  # +1 for space
            
            if current_length >= max_input_length:
                chunks.append(' '.join(current_chunk[:-1]))  # Don't include the word that made it too long
                current_chunk = [word]  # Start new chunk with the current word
                current_length = len(word)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        # Generate summaries for each chunk
        chunk_summaries = []
        
        # Define length parameters
        length_params = {
            "short": {"max_length": 100, "min_length": 30},
            "medium": {"max_length": 200, "min_length": 80},
            "long": {"max_length": 400, "min_length": 150}
        }
        
        params = length_params.get(length, length_params["medium"])
        
        for chunk in chunks:
            if len(chunk.split()) < 50:  # Skip very short chunks
                chunk_summaries.append(chunk)
                continue
                
            try:
                summary_result = summarizer(
                    chunk,
                    max_length=min(params["max_length"], len(chunk.split()) // 2),
                    min_length=min(params["min_length"], len(chunk.split()) // 4),
                    do_sample=False
                )
                chunk_summaries.append(summary_result[0]['summary_text'])
            except Exception as chunk_error:
                print(f"Error summarizing chunk: {chunk_error}")
                # Fallback: use first few sentences
                sentences = chunk.split('. ')[:3]
                chunk_summaries.append('. '.join(sentences) + '.')
        
        # Combine chunk summaries
        final_summary = ' '.join(chunk_summaries)
        
        # If we have multiple chunks and the result is still long, summarize again
        if len(chunks) > 1 and len(final_summary.split()) > params["max_length"]:
            try:
                final_result = summarizer(
                    final_summary,
                    max_length=params["max_length"],
                    min_length=params["min_length"],
                    do_sample=False
                )
                final_summary = final_result[0]['summary_text']
            except:
                # Keep the combined summary if second-pass fails
                pass
        
        return {
            "summary": final_summary,
            "status": "success",
            "length": length,
            "model_used": "facebook/bart-large-cnn",
            "chunks_processed": len(chunks)
        }
        
    except Exception as e:
        return {
            "summary": f"Error generating summary with Hugging Face model: {str(e)}",
            "status": "error",
            "length": length
        }

def openai_document_summary(document_text: str, length: str = "medium") -> dict:
    """
    Generate a summary of the document using OpenAI GPT
    
    Args:
        document_text: The text content of the document
        length: Summary length - "short", "medium", or "long"
    
    Returns:
        dict containing the summary text and metadata
    """
    
    # Validate inputs
    if not document_text or not document_text.strip():
        return {
            "summary": "No document text provided for summarization.",
            "status": "error", 
            "length": length
        }
    
    if not client:
        return {
            "summary": "OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file.",
            "status": "error",
            "length": length
        }
    
    # Validate length parameter
    valid_lengths = ["short", "medium", "long"]
    if length not in valid_lengths:
        length = "medium"  # Default fallback
    
    # Define length parameters
    length_instructions = {
        "short": "Provide a concise summary in 2-3 sentences highlighting only the most important points.",
        "medium": "Provide a comprehensive summary in 1-2 paragraphs covering the main topics and key details.",
        "long": "Provide a detailed summary with multiple paragraphs, covering all significant points, arguments, conclusions, and supporting details."
    }
    
    instruction = length_instructions.get(length, length_instructions["medium"])
    
    # Create the prompt
    prompt = f"""Please analyze and summarize the following document. {instruction}

Focus on:
- Main topics and themes
- Key findings or conclusions  
- Important details and data
- Overall purpose and context

Document Text:
{document_text}

Please provide a clear, well-structured summary:"""

    # Try different models in order of preference
    models = ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4"]
    last_error = None
    
    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional document summarization assistant. Provide clear, accurate, and well-structured summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000 if length == "long" else 500 if length == "medium" else 200,
                temperature=0.3  # Lower temperature for more consistent summaries
            )
            
            summary_text = response.choices[0].message.content.strip()
            
            return {
                "summary": summary_text,
                "status": "success",
                "length": length,
                "model_used": model,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            last_error = str(e)
            print(f"Failed with model {model}: {e}")
            continue
    
    # If all models fail
    error_message = f"Failed to generate summary with all available models."
    if last_error:
        error_message += f" Last error: {last_error}"
    
    return {
        "summary": error_message,
        "status": "error",
        "length": length
    }

def smart_document_summary(document_text: str, length: str = "medium") -> dict:
    """
    Smart document summarization that tries multiple AI services
    
    Priority order:
    1. OpenAI GPT (cloud, high-quality)
    2. Ollama Mistral 7B (local, free backup)
    3. Fallback extractive summary
    
    Args:
        document_text: The text content of the document
        length: Summary length - "short", "medium", or "long"
    
    Returns:
        dict containing the summary text and metadata
    """
    
    # Try OpenAI GPT first (high quality cloud AI)
    if client:
        print("🤖 Trying OpenAI GPT model...")
        result = openai_document_summary(document_text, length)
        if result["status"] == "success":
            return result
        else:
            print(f"⚠️ OpenAI failed: {result['summary']}")
    
    # Try Ollama Mistral as backup (free, local)
    print("🤖 Trying Ollama Mistral 7B as backup...")
    result = ollama_document_summary(document_text, length)
    if result["status"] == "success":
        return result
    else:
        print(f"⚠️ Ollama failed: {result['summary']}")
    
    # Try Hugging Face if available (kept for compatibility)
    if HF_AVAILABLE:
        print("🤖 Trying Hugging Face BART model...")
        result = huggingface_document_summary(document_text, length)
        if result["status"] == "success":
            return result
        else:
            print(f"⚠️ Hugging Face failed: {result['summary']}")
    
    # Fallback to simple extractive summary
    print("🤖 Using fallback extractive summarization...")
    return fallback_extractive_summary(document_text, length)

def fallback_extractive_summary(document_text: str, length: str = "medium") -> dict:
    """
    Simple extractive summarization as last resort
    """
    if not document_text or not document_text.strip():
        return {
            "summary": "No document text provided for summarization.",
            "status": "error", 
            "length": length
        }
    
    # Clean text
    text = re.sub(r'\s+', ' ', document_text.strip())
    sentences = text.split('. ')
    
    # Simple scoring: prefer sentences with common keywords
    scored_sentences = []
    words = text.lower().split()
    word_freq = {}
    
    # Count word frequencies
    for word in words:
        word = re.sub(r'[^\w]', '', word)
        if len(word) > 3:  # Skip short words
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Score sentences based on word frequencies
    for i, sentence in enumerate(sentences):
        score = 0
        sentence_words = sentence.lower().split()
        for word in sentence_words:
            word = re.sub(r'[^\w]', '', word)
            score += word_freq.get(word, 0)
        
        # Prefer sentences that aren't too short or too long
        length_penalty = 0
        if len(sentence_words) < 5:
            length_penalty = -10
        elif len(sentence_words) > 50:
            length_penalty = -5
            
        scored_sentences.append((score + length_penalty, i, sentence))
    
    # Sort by score and select top sentences
    scored_sentences.sort(reverse=True)
    
    # Determine number of sentences based on length
    num_sentences = {
        "short": min(3, len(sentences)),
        "medium": min(5, len(sentences)),
        "long": min(8, len(sentences))
    }.get(length, 5)
    
    # Select top sentences and sort by original order
    selected = sorted(scored_sentences[:num_sentences], key=lambda x: x[1])
    summary = '. '.join([sent[2] for sent in selected])
    
    # Ensure it ends with a period
    if not summary.endswith('.'):
        summary += '.'
    
    return {
        "summary": summary,
        "status": "success",
        "length": length,
        "model_used": "extractive_fallback",
        "sentences_selected": num_sentences
    }

# Keep the old function name for backward compatibility
def gemini_document_summary(document_text: str, length: str = "medium") -> dict:
    """Wrapper function for backward compatibility - now uses smart summarization"""
    return smart_document_summary(document_text, length)