from langchain.docstore.document import Document
from typing import List
from recursive_url_parser import RecursiveUrlParser  # Import your custom parser

chunk_size = 512  # Chunk size for the parser
chunk_overlap = 128  # Chunk overlap for the parser
recursive = False  # Recursive flag for the parser
option = {
    "exclude_dirs": None,  # Exclude directories from the parser
    "max_depth": None,  # Maximum depth for the parser
    "timeout": None,  # Timeout for the parser
    "prevent_outside": None  # Prevent outside links for the parser
}

def update_variables(settings):
    global url, chunk_size, chunk_overlap, recursive, option
    chunk_size = settings["chunk_size"]
    chunk_overlap = settings["chunk_overlap"]
    recursive = settings["recursive"]
    option["exclude_dirs"] = settings["option_exclude_dirs"]
    option["max_depth"] = settings["option_max_depth"]
    option["timeout"] = settings["option_timeout"]
    option["prevent_outside"] = settings["option_prevent_outside"]
    
@hook(priority=10)
def before_cat_reads_message(user_message_json, cat):
    settings = cat.mad_hatter.get_plugin().load_settings()
    update_variables(settings)
    return user_message_json

# Hook called just before rabbithole splits text. Input is whole Document
@hook(priority=10)  # Higher priority to ensure it executes before the default behavior
def before_rabbithole_splits_text(doc: Document, cat) -> Document:
    """Hook the `Document` before is split.

    Allows editing the whole uploaded `Document` before the *RabbitHole* recursively splits it in shorter ones.

    For instance, the hook allows to change the text or edit/add metadata.

    Parameters
    ----------
    doc : Document
        Langchain `Document` uploaded in the *RabbitHole* to be ingested.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    doc : Document
        Edited Langchain `Document`.

    """
    # You can check if the document source is a URL and apply your custom parser
    if doc.metadata.get("source_type") == "URL":
        # Instantiate your custom parser with appropriate settings
        parser = RecursiveUrlParser(url=doc.page_content, chunk_size=chunk_size, chunk_overlap=chunk_overlap, recursive=recursive, **option)
        parsed_content = parser.parse()  # This should return the parsed content
        doc.page_content = parsed_content  # Update the document content with parsed content

    return doc

# Hook called when a list of Document is going to be inserted in memory from the rabbit hole.
# Here you can edit/summarize the documents before inserting them in memory
# Should return a list of documents (each is a langchain Document)
@hook(priority=10)  # Higher priority to ensure it executes before the default behavior
def before_rabbithole_stores_documents(docs: List[Document], cat) -> List[Document]:
    """Hook into the memory insertion pipeline.

    Allows modifying how the list of `Document` is inserted in the vector memory.

    For example, this hook is a good point to summarize the incoming documents and save both original and
    summarized contents.
    An official plugin is available to test this procedure.

    Parameters
    ----------
    docs : List[Document]
        List of Langchain `Document` to be edited.
    cat: CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    docs : List[Document]
        List of edited Langchain documents.

    """
    updated_docs = []
    for doc in docs:
        # You can check if the document source is a URL and apply your custom parser
        if doc.metadata.get("source_type") == "URL":
            # Instantiate your custom parser with appropriate settings
            parser = RecursiveUrlParser(url=doc.page_content, chunk_size=chunk_size, chunk_overlap=chunk_overlap, recursive=recursive, **option)
            parsed_content = parser.parse()  # This should return the parsed content
            doc.page_content = parsed_content  # Update the document content with parsed content

        updated_docs.append(doc)

    return updated_docs

@hook(priority=10)
def rabbithole_instantiates_parsers(file_handlers: dict, cat) -> dict:
    new_handlers = {
        "text/html": RecursiveUrlParser(chunk_size=chunk_size, chunk_overlap=chunk_overlap, recursive=recursive, **option)
    }
    file_handlers = file_handlers | new_handlers
    return file_handlers
