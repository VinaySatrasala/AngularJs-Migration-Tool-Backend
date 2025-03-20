from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, PrivateAttr
from functools import lru_cache
from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIModel
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import Settings
from langchain_community.chat_models import AzureChatOpenAI
from langchain_community.embeddings import AzureOpenAIEmbeddings
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing import Optional

class LLMConfig(BaseSettings):
    # Azure OpenAI Configuration
    azure_openai_api_key: SecretStr = Field(..., validation_alias="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field(..., validation_alias="AZURE_OPENAI_API_VERSION")
    azure_openai_endpoint: str = Field(..., validation_alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment_name: str = Field(..., validation_alias="AZURE_OPENAI_DEPLOYMENT_NAME")

    # Azure OpenAI Embedding Configuration
    azure_openai_embed_api_endpoint: str = Field(..., validation_alias="AZURE_OPENAI_EMBED_API_ENDPOINT")
    azure_openai_embed_api_key: SecretStr = Field(..., validation_alias="AZURE_OPENAI_EMBED_API_KEY")
    azure_openai_embed_model: str = Field(..., validation_alias="AZURE_OPENAI_EMBED_MODEL")
    azure_openai_embed_version: str = Field(..., validation_alias="AZURE_OPENAI_EMBED_VERSION")

    # LlamaIndex components
    _llm: Optional[AzureOpenAI] = PrivateAttr(default=None)
    _embed_model: Optional[AzureOpenAIEmbedding] = PrivateAttr(default=None)

    # Langchain components
    _langchain_llm: Optional[AzureChatOpenAI] = PrivateAttr(default=None)
    _langchain_embedding: Optional[AzureOpenAIEmbeddings] = PrivateAttr(default=None)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @classmethod
    @lru_cache(maxsize=1)
    def get_pydantic_model(cls, api_key: str, api_version: str, endpoint: str, deployment_name: str) -> OpenAIModel:
        return OpenAIModel(
            deployment_name, 
            openai_client=AsyncAzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint,
                azure_deployment=deployment_name
            )
        )

    def init_llamaindex(self) -> None:
        """Initialize LlamaIndex settings with Azure OpenAI components"""
        self._llm = AzureOpenAI(
            model="gpt-4o",
            deployment_name=self.azure_openai_deployment_name,
            api_key=self.azure_openai_api_key.get_secret_value(),
            azure_endpoint=self.azure_openai_endpoint,
            api_version=self.azure_openai_api_version,
        )

        self._embed_model = AzureOpenAIEmbedding(
            model="text-embedding-3-large",
            deployment_name=self.azure_openai_embed_model,
            api_key=self.azure_openai_embed_api_key.get_secret_value(),
            azure_endpoint=self.azure_openai_embed_api_endpoint,
            api_version=self.azure_openai_embed_version,
        )
        
        # self._embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Configure global LlamaIndex settings
        Settings.llm = self._llm
        Settings.embed_model = self._embed_model

    def init_langchain(self) -> None:
        """Initialize Langchain components with Azure OpenAI"""
        self._langchain_llm = AzureChatOpenAI(
            deployment_name="gpt-4o",
            openai_api_key=self.azure_openai_api_key.get_secret_value(),
            azure_endpoint=self.azure_openai_endpoint,
            openai_api_version=self.azure_openai_api_version
        )

        self._langchain_embedding = AzureOpenAIEmbeddings(
            azure_deployment=self.azure_openai_embed_model,
            openai_api_key=self.azure_openai_embed_api_key.get_secret_value(),
            azure_endpoint=self.azure_openai_embed_api_endpoint,
            openai_api_version=self.azure_openai_embed_version,
            chunk_size=1000
        )

# ✅ Create singleton instance
llm_config = LLMConfig()
llm_config.init_llamaindex()
llm_config.init_langchain()

# ✅ Keep the Pydantic model (used by LlamaIndex)
pydantic_ai_model = llm_config.get_pydantic_model(
    api_key=llm_config.azure_openai_api_key.get_secret_value(),
    api_version=llm_config.azure_openai_api_version,
    endpoint=llm_config.azure_openai_endpoint,
    deployment_name=llm_config.azure_openai_deployment_name
)
