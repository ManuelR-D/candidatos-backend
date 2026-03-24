"""AI Summarizer for text summarization using Azure OpenAI and LangChain."""
import os
import logging
from typing import Optional
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Configure logger
logger = logging.getLogger(__name__)


class AISummarizer:
    """
    AI-powered text summarizer using Azure OpenAI through LangChain.
    
    This class provides text summarization capabilities using Azure OpenAI's
    GPT models via LangChain framework.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment_name: Optional[str] = None,
        api_version: Optional[str] = None,
        temperature: float = 1,
        max_tokens: int = 64000
    ):
        """
        Initialize the AI Summarizer.
        
        Args:
            api_key: Azure OpenAI API key (defaults to AZURE_OPENAI_API_KEY env var)
            endpoint: Azure OpenAI endpoint (defaults to AZURE_OPENAI_ENDPOINT env var)
            deployment_name: Deployment name (defaults to AZURE_OPENAI_DEPLOYMENT_NAME env var)
            api_version: API version (defaults to AZURE_OPENAI_API_VERSION env var)
            temperature: Model temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens in the summary
        """
        self.api_key = api_key or os.getenv('AZURE_OPENAI_API_KEY')
        self.endpoint = endpoint or os.getenv('AZURE_OPENAI_ENDPOINT')
        self.deployment_name = deployment_name or os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        self.api_version = api_version or os.getenv('AZURE_OPENAI_API_VERSION')
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        logger.debug(f"Initializing AISummarizer with deployment: {self.deployment_name}, temperature: {temperature}, max_tokens: {max_tokens}")
        
        if not all([self.api_key, self.endpoint, self.deployment_name, self.api_version]):
            logger.error("Missing required Azure OpenAI configuration")
            raise ValueError(
                "Missing required Azure OpenAI configuration. "
                "Please set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, "
                "AZURE_OPENAI_DEPLOYMENT_NAME, and AZURE_OPENAI_API_VERSION"
            )
        
        assert self.api_key is not None
        assert self.endpoint is not None
        assert self.deployment_name is not None
        assert self.api_version is not None
        
        # Set environment variables for LangChain to use
        os.environ['AZURE_OPENAI_API_KEY'] = self.api_key
        os.environ['AZURE_OPENAI_ENDPOINT'] = self.endpoint
        
        logger.debug("Initializing AzureChatOpenAI client")
        # Initialize Azure OpenAI client through LangChain
        self.llm = AzureChatOpenAI(
            azure_deployment=self.deployment_name,
            api_version=self.api_version,
            temperature=self.temperature,
            max_completion_tokens=self.max_tokens
        )
        logger.info("AISummarizer initialized successfully")
    
    def summarize(
        self,
        text: str,
        max_length: Optional[int] = None,
        summary_type: str = "concise",
        rep_name: Optional[str] = None,
        topic_name: Optional[str] = None
    ) -> str:
        """
        Summarize the given text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length for the summary in words (optional)
            summary_type: Type of summary - "concise", "detailed", or "bullet_points"
            rep_name: Representative name for contextual summaries (optional)
            topic_name: Topic name for contextual summaries (optional)
            
        Returns:
            Summarized text
            
        Raises:
            ValueError: If text is empty or summary_type is invalid
        """
        if not text or not text.strip():
            logger.warning("Attempted to summarize empty text")
            raise ValueError("Text cannot be empty")
        
        valid_types = ["concise", "detailed", "bullet_points"]
        if summary_type not in valid_types:
            logger.error(f"Invalid summary_type: {summary_type}")
            raise ValueError(f"summary_type must be one of {valid_types}")
        
        text_length = len(text)
        word_count = len(text.split())
        logger.debug(f"Starting summarization: type={summary_type}, text_length={text_length}, word_count={word_count}, max_length={max_length}")
        
        # Create prompt based on summary type
        if summary_type == "concise":
            rep_label = rep_name or "Desconocido"
            topic_label = topic_name or "Tema no especificado"
            prompt_template = f"""Actúa como un analista político objetivo experto en el Congreso Argentino.
Analiza las siguientes intervenciones del senador/a {rep_label} sobre el tema "{topic_label}".

Intervenciones:
"{{text}}"

Tu tarea:
1. Resume su postura en 2 o 3 oraciones claras.
2. Determina si su postura parece ser A FAVOR, EN CONTRA o ABSTENCIÓN/NEUTRAL basándote en el texto.
3. Sé conciso y directo."""
        elif summary_type == "detailed":
            prompt_template = """Escribí un resumen detallado del siguiente texto:

{text}

RESUMEN DETALLADO:"""
        else:  # bullet_points
            prompt_template = """Resumí el siguiente texto como una lista de puntos clave que destaquen la información más importante:

{text}

RESUMEN LISTA DE PUNTOS:"""
        
        # Add length constraint if specified
        if max_length:
            prompt_template = f"{prompt_template}\n\nLímite: máximo {max_length} palabras."
        
        # For shorter texts, use simple prompt-based summarization
        if len(text.split()) < 3000:
            logger.debug("Using simple prompt-based summarization (text < 3000 words)")
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["text"]
            )
            
            chain = prompt | self.llm
            logger.debug("Invoking LLM for summarization")
            result = chain.invoke({"text": text})
            
            # Extract content from AIMessage
            if hasattr(result, 'content'):
                content = result.content
                if isinstance(content, str):
                    summary_text = content.strip()
                else:
                    summary_text = str(content).strip()
            else:
                summary_text = str(result).strip()

            if not summary_text:
                response_metadata = getattr(result, "response_metadata", None)
                usage_metadata = getattr(result, "usage_metadata", None)
                additional_kwargs = getattr(result, "additional_kwargs", None)
                logger.warning(
                    "Empty summary returned by model. response_metadata=%s usage_metadata=%s additional_kwargs=%s",
                    response_metadata,
                    usage_metadata,
                    additional_kwargs
                )
                raise ValueError("Model returned empty summary")

            logger.info(f"Summary generated successfully: {len(summary_text)} characters")
            return summary_text
        
        # For longer texts, use map-reduce summarization
        logger.debug("Text is long (>= 3000 words), using map-reduce approach")
        return self._summarize_long_text(text, prompt_template)
    
    def _summarize_long_text(self, text: str, prompt_template: str) -> str:
        """
        Summarize long text using map-reduce approach.
        
        Args:
            text: Long text to summarize
            prompt_template: Template for the summary prompt
            
        Returns:
            Summarized text
        """
        logger.debug("Starting map-reduce summarization for long text")
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=200,
            length_function=len
        )
        
        # Create documents from chunks
        chunks = text_splitter.split_text(text)
        docs = [Document(page_content=chunk) for chunk in chunks]
        logger.debug(f"Text split into {len(docs)} chunks")
        
        # For simplicity with long text, summarize each chunk and combine
        chunk_summaries = []
        for idx, doc in enumerate(docs):
            logger.debug(f"Summarizing chunk {idx + 1}/{len(docs)}")
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["text"]
            )
            chain = prompt | self.llm
            result = chain.invoke({"text": doc.page_content})
            
            if hasattr(result, 'content'):
                content = result.content
                if isinstance(content, str):
                    chunk_summaries.append(content.strip())
                else:
                    chunk_summaries.append(str(content).strip())
            else:
                chunk_summaries.append(str(result).strip())
        
        logger.debug(f"All {len(chunk_summaries)} chunks summarized, creating final summary")
        # Combine all chunk summaries
        combined_text = "\n\n".join(chunk_summaries)
        
        # Create final summary from combined summaries
        final_prompt = PromptTemplate(
            template="""Escribi un resumen final basado en los siguientes resúmenes parciales:

{text}

RESUMEN FINAL:""",
            input_variables=["text"]
        )
        
        final_chain = final_prompt | self.llm
        final_result = final_chain.invoke({"text": combined_text})
        
        if hasattr(final_result, 'content'):
            content = final_result.content
            if isinstance(content, str):
                summary_text = content.strip()
            else:
                summary_text = str(content).strip()
        else:
            summary_text = str(final_result).strip()

        if not summary_text:
            response_metadata = getattr(final_result, "response_metadata", None)
            usage_metadata = getattr(final_result, "usage_metadata", None)
            additional_kwargs = getattr(final_result, "additional_kwargs", None)
            logger.warning(
                "Empty final summary returned by model. response_metadata=%s usage_metadata=%s additional_kwargs=%s",
                response_metadata,
                usage_metadata,
                additional_kwargs
            )
            raise ValueError("Model returned empty summary")

        logger.info(f"Final summary generated successfully: {len(summary_text)} characters")
        return summary_text
    
    def summarize_with_focus(
        self,
        text: str,
        focus_areas: list[str],
        max_length: Optional[int] = None
    ) -> str:
        """
        Summarize text with focus on specific areas or topics.
        
        Args:
            text: Text to summarize
            focus_areas: List of specific areas/topics to focus on
            max_length: Maximum length for the summary in words (optional)
            
        Returns:
            Summarized text focused on the specified areas
        """
        if not text or not text.strip():
            logger.warning("Attempted to summarize empty text with focus")
            raise ValueError("Text cannot be empty")
        
        if not focus_areas:
            logger.error("No focus areas provided for focused summarization")
            raise ValueError("At least one focus area must be provided")
        
        logger.debug(f"Starting focused summarization with {len(focus_areas)} focus areas")
        logger.debug(f"Focus areas: {focus_areas}")
        
        focus_list = "\n".join([f"- {area}" for area in focus_areas])
        
        prompt_template = f"""Resumí el siguiente texto, enfocándote específicamente en estas áreas:

{focus_list}

Texto a resumir:
{{text}}

RESUMEN ENFOCADO:"""
        
        if max_length:
            prompt_template = prompt_template.replace(
                "RESUMEN ENFOCADO:",
                f"RESUMEN ENFOCADO (máximo {max_length} palabras):"
            )
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text"]
        )
        
        chain = prompt | self.llm
        logger.debug("Invoking LLM for focused summarization")
        result = chain.invoke({"text": text})
        
        # Extract content from AIMessage
        if hasattr(result, 'content'):
            content = result.content
            if isinstance(content, str):
                logger.info(f"Focused summary generated successfully: {len(content)} characters")
                return content.strip()
            logger.info(f"Focused summary generated successfully: {len(str(content))} characters")
            return str(content).strip()
        logger.info(f"Focused summary generated successfully: {len(str(result))} characters")
        return str(result).strip()
