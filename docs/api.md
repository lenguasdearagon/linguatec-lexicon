## REST API
All the listing methods (list, search) are paginated, by default '30' items are returned and a maximum of '100' can be retrieved in a query.

### Documentation TODO
- [ ] Include query examples
- [ ] Add output example

### List words
List all the words of the dictionary.
`GET /words/`

### Show word
Show the details of a word of the dictionary using its identifier.
`GET /words/{id}`

### Search words
List the words that maches a query.
`GET /words/?search=querystring`

The `querystring` follows the format described by [Django admin search](https://docs.djangoproject.com/en/stable/ref/contrib/admin/#django.contrib.admin.ModelAdmin.search_fields).

| Prefix | 	Lookup |
|-------|-------|
| ^	| startswith |
| =	| iexact |
| @	| search |
| None	| icontains |

For example, `=foo` should perform a search of `foo` in a case-insensitive **exact** match.


### Search words by term
List the words that have the same term as the value of q parameter. If there is not an exact match it list similar words.
`GET /words/search/?q=term`

### Search words by term and lexicon
List the word that have the same term as the value of q parameter and the same lexicon (or lexicon key) as the value of l parameter. If there is not an exact match it list similar words.
`GET /words/search/?q=term&l=lexicon`