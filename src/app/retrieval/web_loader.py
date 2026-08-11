import httpx
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

#This function return 2 things one is title and second is text.
def load_webpage(url: str) -> tuple[str, str]:
    #sending the http request on the url.
    with httpx.Client(
        timeout=20.0,
        follow_redirects=True,
    ) as client:
        response = client.get(url)
        # here we checkt the request status , sucessful or not.
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    #this for loop removes all these tags.
    for tag in soup(
        ["script", "style", "nav", "footer", "header"]
    ):
        tag.decompose()

    title = ( 
        soup.title.get_text(strip=True)
        if soup.title
        else "Untitled"
    )
    #this extract the readable text from the remaining HTML.
    text = soup.get_text(
        separator="\n",
        strip=True,
    )

    return title, text


def split_into_chunks(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )

    return splitter.split_text(text)