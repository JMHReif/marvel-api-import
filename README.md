:img: https://raw.githubusercontent.com/JMHReif/marvel-api-import/images

# marvel-api-import

"Data provided by Marvel. © 2014 Marvel"

This repository is to crawl the `developer.marvel.com` API and retrieve Marvel characters, comics, creators, events, series, and stories data they have published.
Our particular use is to retrieve the data from the API and convert it to JSON-formatted flat files for consistent and easy ingestion into other sources - in my personal case, Neo4j graph database.
I want to use this data for analysis to find the connections and relationships between the entities in this dataset and encourage others to analyze it for themselves.

Retrieval of this data requires proper attribution for use, and it requires an individual API key that is granted via access request and a user account.
Steps for this process are included below.

## Requesting an API key

Users interested in following this process for themselves and pulling the data into JSON files can do so with the following steps:

1. Go to https://developer.marvel.com/[developer.marvel.com/^] and create an account.
2. Under the main page header, you should see a white menu bar with `Developer Portal` and a list of links. Choose the `Get a Key` option. This option also shows up on the right side of another white menu bar beneath the central image.
image::{img}marvel_dev_portal.png
3. Fill out the request to receive an API key to access the data and interactive documentation.
4. Once approved, start trying it out! Marvel has good interactive documentation that is very helpful to see what parameters and requests look like, as well as what data comes back and the result formatting.

You can go to the `My Developer Account` option in the `Developer Portal` menu and see your public and private API keys, as well as the limits and domains.
Be sure to think and plan carefully how to retrieve the data based on result limits and rate limits!
This is very tricky.

## Entity amounts

Current existing entity counts from the API are listed here to help others plan retrieval and limits:

|===
|*Characters:* |   1493 |
|*Comics:*     |  46410 |
|*Creators:*   |   5304 |
|*Events:*     |     75 |
|*Series:*     |  11623 |
|*Stories:*    | 107867 |
|===
