# ScrapeSE
Web scraping tools targeting systems engineering and technical data sources.
Includes unique modules for targeting specific data resources and schemas. Most
modules contain at least two public methods:

* resolve(), which accepts a search term and returns a URL to a matching
  resource from the respective data store
* query(), which attempts to parse a specific model from the resource URL, like
  the one returned by resolve(). Additional paramters are common when, for
  example, a resource contains with multiple models.
