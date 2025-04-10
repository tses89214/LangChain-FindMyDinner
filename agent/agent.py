"""
LangChain agent for finding restaurants that are currently open.
"""
from typing import List, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema.messages import SystemMessage
from langchain.tools import BaseTool
from langchain.chat_models import ChatOpenAI

from agent.tools import FindNearbyRestaurantsTool, GetRestaurantDetailsTool
from services.places_api import GooglePlacesService

class FindMyDinnerAgent:
    """
    Agent for finding restaurants that are currently open near a specified location.
    """
    
    def __init__(self, openai_api_key: str, places_api_key: Optional[str] = None):
        """
        Initialize the FindMyDinner agent.
        
        Args:
            openai_api_key: OpenAI API key for the language model
            places_api_key: Google Places API key (optional, will use env var if not provided)
        """
        self.openai_api_key = openai_api_key
        
        # Initialize the Google Places service
        self.places_service = GooglePlacesService(api_key=places_api_key)
        
        # Initialize the tools
        self.tools = self._create_tools()
        
        # Initialize the language model
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o",
            api_key=openai_api_key
        )
        
        # Create the agent
        self.agent_executor = self._create_agent()
    
    def _create_tools(self) -> List[BaseTool]:
        """
        Create the tools for the agent.
        
        Returns:
            List of tools
        """
        return [
            FindNearbyRestaurantsTool(places_service=self.places_service),
            GetRestaurantDetailsTool(places_service=self.places_service)
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """
        Create the agent executor.
        
        Returns:
            Agent executor
        """
        # Define the system message
        system_message = SystemMessage(
            content="""You are a helpful assistant that helps users find restaurants that are currently open near them.
            
Your goal is to help users find places to eat based on their location, preferences, and other criteria.

You have access to tools that can:
1. Find nearby restaurants that are currently open
2. Get detailed information about specific restaurants

When users ask about finding food or restaurants, use the find_nearby_restaurants tool.
When they want more details about a specific restaurant, use the get_restaurant_details tool.

Always be helpful, concise, and focused on helping the user find a place to eat.
"""
        )
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            system_message,
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create memory
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Create the agent
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        
        # Create the agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def run(self, query: str) -> str:
        """
        Run the agent with a user query.
        
        Args:
            query: User query
            
        Returns:
            Agent response
        """
        result = self.agent_executor.invoke({"input": query})
        return result.get("output", "I couldn't find an answer to your question.")
