# Integrating IBM Cloud Functions with the IBM Data Science Experience
This project shows how to use IBM Cloud Functions to provide data processing services to a DSX notebook. This tutorial should take about 5 minutes to complete.

If you're not familiar with the Cloud Functions/OpenWhisk programming model [try the action, trigger, and rule sample first](https://github.com/IBM/openwhisk-action-trigger-rule). [You'll need an IBM Cloud account and the latest OpenWhisk (`wsk`) or IBM Cloud command line plugin (`bx wsk`)](https://github.com/IBM/openwhisk-action-trigger-rule/blob/master/docs/OPENWHISK.md).

This example shows how to create an action that can be integrated with the built in Cloudant changes trigger and read action to execute logic when new data is added.

1. [Configure Data Science Experience](#1-configure-data-science-experience)
2. [Create Cloud Functions](#2-create-cloud-functions)
3. [Clean up](#3-clean-up)


# 1. Configure Data Science Experience

## Provision a Configure Data Science Experience instance
TODO


# 2. Create Cloud Functions

## Create the actions

### Create an action to parse book data
Create a file named `parse-book-data.py`. This file will define an action written as a Python function. It checks for the required book ID parameter (`id`) and returns the book data without metadat, or an error if either parameter is missing.


```python
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
```

## Upload the action
The next step will be to deploy Cloud Functions from the JavaScript files that we just created. We also add the `--web true` flag, to annotate these actions as "Web Actions". This will be necessary later when we add REST endpoints as it makes the actions HTTP-aware.
```bash
wsk action create parse-book-data parse-book-data.py --web true
```

## Unit test the action
Cloud Functions (OpenWhisk actions) are stateless code snippets that can be invoked explicitly or in response to an event. For right now, we will test our action by explicitly invoking it. Later, we will trigger our actions in response to an HTTP request. Invoke the action using the code below and pass the parameters using the `--param` command line argument.

```bash
wsk action invoke \
  --blocking \
  --param id 61 \
  parse-book-data
```

> **Note**: If you see any error messages, refer to the [Troubleshooting](#troubleshooting) section below.

## Create the HTTP API mapping

Now that we have our Cloud Function created, we will expose it through the Bluemix API Gateway. To do this we use: `wsk api create $BASE_PATH $API_PATH $API_VERB $ACTION `

This feature is part of the [IBM Cloud Native API Management](https://console.ng.bluemix.net/docs/openwhisk/openwhisk_apigateway.html#openwhisk_apigateway) service and currently supports very powerful API management features like security, rate limiting, and more. For now though we're just using the CLI to expose our action with a public HTTP GET endpoint.

```bash
# Send along credentials with the command or provide them interactively
wsk bluemix login --user $YOUR_BLUEMIX_USERNAME --password $YOUR_BLUEMIX_PASSWORD

# Exposes /v1/cat?id=1
wsk api create -n "Book API" /v1 /book get parse-book-data
```
The CLI will output the URL required to use the API. Make note of it for the next section.

## Test with `curl` HTTP requests
Take note of the API URL that is generated from the previous command. Send an HTTP GET request using `curl` to test the action. Remember to send the required parameters as a query string for GET. The IBM Cloud Functions system automatically forwards the parameter to the action we created.

```bash
# GET /v1/cat?id=1
curl $THE_URL_FROM_ABOVE?id=1
```


# 3. Clean up
## Remove the API mapping and delete the action

```bash
# Remove API base which removes all mapping
wsk api delete /v1

# Remove action
wsk action delete parse-book-data
```

# Troubleshooting
Check for errors first in the Cloud Functions activation log. Tail the log on the command line with `wsk activation poll` or drill into details visually with the [monitoring console on Bluemix](https://console.ng.bluemix.net/openwhisk/dashboard).

If the error is not immediately obvious, make sure you have the [latest version of the `wsk` CLI installed](https://console.ng.bluemix.net/openwhisk/learn/cli). If it's older than a few weeks, download an update.
```bash
wsk property get --cliversion
```

# License
[Apache 2.0](LICENSE.txt)

