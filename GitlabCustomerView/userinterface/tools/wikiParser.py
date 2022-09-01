

def parseStructure(wikis):
    
    if wikis:
        structure = {}
        for wiki in wikis:
            parent = '/'
            if '/' in wiki.slug:
                parent = wiki.slug.split('/')[0]
            page = {'title': wiki.title, 'slug': wiki.slug}

            if parent in structure:
                structure[parent].append(page)
            else:
                structure[parent] = [page,]

        return structure
    else:
        return False