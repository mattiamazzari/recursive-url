from cat.mad_hatter.decorators import hook

from .recursive_url_parser import RecursiveUrlParser


@hook
def rabbithole_instantiates_parsers(file_handlers: dict, cat) -> dict:
    new_handlers = {
        "text/html": RecursiveUrlParser()
    }
    file_handlers = file_handlers | new_handlers
    return file_handlers