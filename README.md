# RecURLsive

This plugin implements a custom parser that allows to recursively download all the URLs in a given webpage.
A web page might have many interesting child pages that we may want to read in bulk.
The challenge is traversing the tree of child pages and actually assembling that list.
and we do this using the RecursiveUrlLoader provided by Langchain.

This also gives us the flexibility to exclude some children, customize the extractor, and more.
## Usage

1. Specify the URL of the webpage you want to download recursively.
2. Specify the depth of the recursion.