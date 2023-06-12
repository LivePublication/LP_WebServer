import pandoc
pandoc.configure(path="C:\Program Files\Pandoc\pandoc.exe")


def md_to_html(filename):
    with open(filename, 'r') as f:
        doc = pandoc.read(f.read())

    return pandoc.write(doc, format='html')
