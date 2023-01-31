import requests, time
from TSRUrl import TSRUrl
from exceptions import *


class TSRDownload:
    @classmethod
    def __init__(self, url: TSRUrl):
        self.session: requests.Session = requests.Session()
        self.url: TSRUrl = url
        self.tickedInitializedTime: float = -1.0
        self.__getTSRDLTicketCookie()

    @classmethod
    def download(self):
        timeToSleep = 15000 - (time.time() * 1000 - self.tickedInitializedTime)
        if timeToSleep > 0:
            time.sleep(timeToSleep / 1000)

        downloadUrl = self.__getDownloadUrl()
        file = self.session.get(downloadUrl)
        fileName = file.headers["Content-Disposition"][
            22:-1
        ]  # Remove 'attachment; filename="' from header

        with open(f"./{fileName}", "wb") as f:
            f.write(file.content)

    @classmethod
    def __getDownloadUrl(self) -> str:
        response = self.session.get(
            f"https://www.thesimsresource.com/ajax.php?c=downloads&a=getdownloadurl&ajax=1&itemid={self.url.itemId}&mid=0&lk=0",
            cookies=self.session.cookies,
        )
        responseJSON = response.json()

        if response.status_code == 200:
            if responseJSON["error"] == "":
                return responseJSON["url"]
            elif responseJSON["error"] == "Invalid download ticket":
                raise InvalidDownloadTicket(response.url, self.session.cookies)
        else:
            raise requests.exceptions.HTTPError(response)

    @classmethod
    def __getTSRDLTicketCookie(self) -> str:
        self.session.get(self.url.url)
        response = self.session.get(
            f"https://www.thesimsresource.com/ajax.php?c=downloads&a=initDownload&itemid={self.url.itemId}&format=zip"
        )
        self.session.get(self.url.downloadUrl)
        self.tickedInitializedTime = time.time() * 1000
        return response.cookies.get("tsrdlticket")