import urllib

# This retrieves the UTF-8 text of the book from Project Gutenberg and strips headers and footers.
def main(args):

    # Validate the id
    id = args.get("id")
    if not id:
        return {"error": "No id given"}
    id = str(id)

    # Fetch the book result
    print "Fetching book http://www.gutenberg.org/cache/epub/" + id + "/pg" + id + ".txt", id + ".txt"
    urllib.urlretrieve("http://www.gutenberg.org/cache/epub/" + id + "/pg" + id + ".txt", id + ".txt")

    # Extract the lines between the two start and end delimiters
    print "Extracting body data from " + id + ".txt and saving to " + id + "-body.txt"
    with open(id + ".txt") as infile, open(id + "-body.txt", 'w') as outfile:
        copy = False
        for line in infile:
            if line.startswith("*** START OF THIS PROJECT GUTENBERG EBOOK"):
                print "Found the start delimiter"
                copy = True
            elif line.startswith("*** END OF THIS PROJECT GUTENBERG EBOOK"):
                print "Found the end delimiter"
                copy = False
            elif copy:
                outfile.write(line)

    # Read that data back into a variable to return
    print "Extracting body data from " + id + "-body.txt"
    with open(id + "-body.txt") as bodyfile:
        return {"body": bodyfile.read()}