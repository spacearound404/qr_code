data = '''
{
    "description" : "%s",
    "external_url" : "https://example.com/",
    "image" : "https://bafybeifxjl3ltyx567jyfmb5p4urqvzumrlp4bdyp6yvmdecehcf5fvx7e.ipfs.dweb.link/images/%s.png",
    "name" : "quantum#%s"
}'''

words = open('words.txt', 'r').read().split(' ')

for i in range(10000):
    with open(str(i + 1)) as file:
        file.open(data % (words[i], (i + 1), (i + 1)))
