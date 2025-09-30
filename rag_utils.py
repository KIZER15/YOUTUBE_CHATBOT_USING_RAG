# rag_utils.py
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from googletrans import Translator 
from dotenv import load_dotenv


load_dotenv()

# Initialize LLM
llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

# Prompt template
prompt = PromptTemplate(
    template="""
      You are a helpful assistant.
      Answer ONLY from the provided transcript context.
      If the context is insufficient, just say you don't know.

      {context}
      Question: {question}
    """,
    input_variables=['context', 'question']
)


from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from googletrans import Translator

def fetch_transcript(video_id: str) -> str:
    try:
        # 1. Try fetching English transcript first
        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id, language_code='en')
            transcript_text = " ".join([snippet.text for snippet in transcript])
            return transcript_text
        except Exception:
            # English not available, continue to fetch default transcript
            pass

        # 2. Fetch default transcript in any available language
        transcript = api.fetch(video_id)
        transcript_text = " ".join([snippet.text for snippet in transcript])

        # 3. Detect language and translate to English if needed
        translator = Translator()
        detected_lang = translator.detect(transcript_text[:500]).lang
        if detected_lang != "en":
            transcript_text = translator.translate(transcript_text, src=detected_lang, dest="en").text

        return transcript_text

    except TranscriptsDisabled:
        return "Transcript not available (subtitles disabled)."
    except Exception as e:
        print("Error fetching transcript:", e)
        return f"Error: {e}"



# Function to build vector store (FAISS)
def build_vector_store(transcript_text: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcript_text])
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store

# Function to run RAG
def run_rag(video_id: str, question: str):
    transcript_text = fetch_transcript(video_id)
    if transcript_text.startswith("Error"):
        return transcript_text

    vector_store = build_vector_store(transcript_text)
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    retrieved_docs = retriever.invoke(question)
    
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    final_prompt = prompt.invoke({"context": context_text, "question": question})
    answer = llm.invoke(final_prompt)
    return answer.content
