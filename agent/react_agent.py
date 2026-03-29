import json
from typing import List, Dict, Any
from uuid import UUID
from groq import Groq
from core.config import settings
from core.services.pdf_service import PDFService
from core.ports.database import DatabasePort

class PDFAgent:
    def __init__(self, pdf_service: PDFService, db: DatabasePort):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = "llama-3.3-70b-versatile"
        self.pdf_service = pdf_service
        self.db = db

    def get_tools_definition(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_pdfs",
                    "description": "Lists all available PDFs for the current user including their UUIDs and filenames.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "merge_pdfs",
                    "description": "Merges multiple PDFs in the specified order into a single PDF.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of PDF UUIDs to merge in order."
                            },
                            "output_filename": {"type": "string", "description": "Name for the new merged PDF file."}
                        },
                        "required": ["file_ids", "output_filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "split_pdf",
                    "description": "Extracts specific pages from a PDF to create a new one.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_id": {"type": "string", "description": "Source PDF UUID."},
                            "pages": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "List of 1-indexed pages to extract."
                            },
                            "output_filename": {"type": "string", "description": "Name for the new PDF."}
                        },
                        "required": ["file_id", "pages", "output_filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_pages",
                    "description": "Removes specific pages from a PDF to create a new one.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_id": {"type": "string", "description": "Source PDF UUID."},
                            "pages_to_remove": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "List of 1-indexed pages to remove."
                            },
                            "output_filename": {"type": "string", "description": "Name for the new PDF."}
                        },
                        "required": ["file_id", "pages_to_remove", "output_filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compress_pdf",
                    "description": "Compresses a PDF file to reduce its size.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_id": {"type": "string", "description": "Source PDF UUID."},
                            "output_filename": {"type": "string", "description": "Name for the compressed PDF."}
                        },
                        "required": ["file_id", "output_filename"]
                    }
                }
            }
        ]

    def _execute_tool(self, tool_name: str, arguments: dict, user_id: UUID) -> Any:
        try:
            if tool_name == "list_pdfs":
                return self.db.get_user_pdf_files(user_id)
            elif tool_name == "merge_pdfs":
                file_ids = [UUID(fid) for fid in arguments["file_ids"]]
                new_pdf = self.pdf_service.process_merge(user_id, file_ids, arguments["output_filename"])
                return f"Merged successfully. New PDF ID: {new_pdf['id']}"
            elif tool_name == "split_pdf":
                file_id = UUID(arguments["file_id"])
                new_pdf = self.pdf_service.process_split(user_id, file_id, arguments["pages"], arguments["output_filename"])
                return f"Split successfully. New PDF ID: {new_pdf['id']}"
            elif tool_name == "remove_pages":
                file_id = UUID(arguments["file_id"])
                new_pdf = self.pdf_service.process_remove_pages(user_id, file_id, arguments["pages_to_remove"], arguments["output_filename"])
                return f"Pages removed successfully. New PDF ID: {new_pdf['id']}"
            elif tool_name == "compress_pdf":
                file_id = UUID(arguments["file_id"])
                new_pdf = self.pdf_service.process_compress(user_id, file_id, arguments["output_filename"])
                return f"Compressed successfully. New PDF ID: {new_pdf['id']}"
            else:
                return f"Tool {tool_name} not recognized."
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def chat(self, user_id: UUID, message: str, message_history: List[Dict[str, Any]] = None) -> tuple[str, List[Dict[str, Any]]]:
        messages = message_history or []
        if not messages:
            messages.append({
                "role": "system",
                "content": "You are a helpful PDF Manager Agent. You can manipulate user's PDFs using the provided tools. Always list available PDFs first if you need to know their IDs unless the user provided them. Describe what you've done to the user."
            })
            
        messages.append({"role": "user", "content": message})

        for _ in range(5):  # Max iterations
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.get_tools_definition(),
                tool_choice="auto",
                max_tokens=4096
            )
            
            response_message = response.choices[0].message
            # Append the message to keep context
            messages.append({
                "role": response_message.role,
                "content": response_message.content,
                "tool_calls": getattr(response_message, "tool_calls", None)
            })
            
            tool_calls = response_message.tool_calls
            if tool_calls:
                for tool_call in tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    
                    tool_result = self._execute_tool(func_name, func_args, user_id)
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(tool_result, default=str)
                    })
            else:
                return response_message.content, messages
                
        return "I reached my maximum interaction limit while processing your request.", messages
