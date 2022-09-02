from typing import Union


def parseStructure(wikis: list) -> Union[dict, bool]:
    """
    Parses the title and name (slug) of the objects inside the given wikis list into a list containing dicts representing it

    @params:
        wikis:
            A list containing the gitlab.v4.objects.wikis.ProjectWiki objects to parse

    @return:
        dict:
            If wikis is not empty.
            A dict containing object with the title and slug in it.
            [{ 'title': 'Some Documentation', 'slug': 'Some Documentation' } ...]
        bool:
            If wiki is empty return False
    """

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