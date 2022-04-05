data = '''
{
    "description" : "%s",
    "external_url" : "https://example.com/",
    "image" : "https://bafybeid45bk6flrskdfrepvmyxiv23khptsfmro2cbqczyljfasi472fri.ipfs.dweb.link/images/%s.png",
    "name" : "quantum#%s"
}'''

words = open('words.txt', 'r').read().split(' ')

for i in range(10000):
    with open(str(i + 1)) as file:
        file.open(data % (words[i], (i + 1), (i + 1)))
