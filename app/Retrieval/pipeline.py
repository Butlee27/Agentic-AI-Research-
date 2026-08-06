from app.Retrieval.router import route_source
def retrieve_document(query:str)->str:
    """
    Retrieve relevant information for the given query.

    This is the single entry point to the retrieval system.
    The caller does not need to know where the data comes from.
    
    """ 
    return route_source(query)