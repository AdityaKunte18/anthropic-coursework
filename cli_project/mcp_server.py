from mcp.server.fastmcp import FastMCP
from pydantic import Field
from mcp.server.fastmcp.prompts import base
mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# TODO: Write a tool to read a doc
@mcp.tool(
    name="read_doc_contents",
    description="reads the contents of a document, given the document name, and returns it as a string."
)
def read_document(
    doc_id: str = Field(description="id of the document to read")
):
    return docs.get(doc_id, ValueError(f"Document with id {doc_id} not found."))
    
# TODO: Write a tool to edit a doc
@mcp.tool(
    name="edit_document",
    description="Edit a document, given the document name and the new contents. Returns the updated document contents as a string."
)
def edit_document(
    doc_id: str = Field(description="id of the document to edit"),
    old_contents: str = Field(description="The text to be replaced in the document, must be an exact match to a substring of the document."),
    new_contents: str = Field(description="new contents of the document")
):
    if doc_id not in docs:
        raise ValueError(f"Document with id {doc_id} not found.")
    docs[doc_id] = docs[doc_id].replace(old_contents, new_contents)
    return docs[doc_id]

# TODO: Write a resource to return all doc id's
@mcp.resource(
    "docs://documents",
    mime_type="application/json",
)
def list_docs() -> list[str]:
    return list(docs.keys()) #MCP Python SDK automatically converts this list to JSON when returning the response

# TODO: Write a resource to return the contents of a particular doc
@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain",
)
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document with id {doc_id} not found.")
    return docs[doc_id]
# TODO: Write a prompt to rewrite a doc in markdown format

@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in markdown format.",
)
def format_document(
    doc_id: str = Field(description="id of the document to format"),
) -> list[base.Message]:
    prompt = f"""
    Rewrite the following document in markdown format. Only include the markdown formatted text in your response, without any additional commentary.
    The id of the document you need to format is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, or any other markdown formatting you think is appropriate based on the content of the document.
    Use the edit_document tool if you need to make any edits to the document in order to format it correctly. You can call the tool multiple times if needed. 
    """
    return [base.UserMessage(prompt)]
# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
