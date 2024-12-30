from typing import AsyncGenerator, List, Dict
import json
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
from app.llmops.webcontext import WebScraperVectorDB

class ContextAwareLLMChain:
    def __init__(self, llm, chat_history: List = None):
        self.llm = llm
        self.chat_history = chat_history or []
        self.scraper = WebScraperVectorDB()
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are an AI named Lolamo (abbreviation of Local Language Model). "
                                "Use the provided context if it's relevant to answer the question with maximum information. "
                                "If no context is provided, rely on your own knowledge. "
                                "Cite sources when using context."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "Context: {context}\n\nQuestion: {question}")
        ])
        
        # Chain with context handling
        self.chain = (
            {
                "context": self._get_context,
                "question": itemgetter("input"),
                "chat_history": itemgetter("chat_history")
            }
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
    
    def _format_context(self, context_list: List[Dict]) -> str:
        """Format context into a readable string with sources"""
        if not context_list:
            return "No relevant context found."
        
        formatted_contexts = []
        for idx, ctx in enumerate(context_list, 1):
            formatted_contexts.append(
                f"[Source {idx}: {ctx['source']}]\n{ctx['content']}\n"
            )
        return "\n\n".join(formatted_contexts)
    
    async def _get_context(self, input_dict: Dict) -> str:
        """Retrieve and format context for the input question"""
        question = input_dict["input"]
        
        context_results=[]
        # Check if we need to search the web
        if "search the web" in question.lower() or "find information about" in question.lower():
            # Process the query to update vector store
            self.scraper.process_query(query=question)
        
            # Get context from vector store
            context_results = self.scraper.get_context(query=question)
        return self._format_context(context_results)
    
    async def get_response(self, question: str) -> AsyncGenerator[str, None]:
        """Get streaming response to the query"""
        answer = ""
        
        async for chunk in self.chain.astream({
            "input": question,
            "chat_history": self.chat_history
        }):
            answer += chunk
            print(chunk, end="", flush=True)
            resp = {
                "model": "llama3",
                "message": {
                    "role": "assistant",
                    "content": chunk
                }
            }
            yield json.dumps(resp)
        
        # Update chat history
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))