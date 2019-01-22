## REST API

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
