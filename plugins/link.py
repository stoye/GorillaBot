# Copyright (c) 2013-2014 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from bs4 import BeautifulSoup
from plugins.util import command
import re
from urllib.parse import urlparse
from urllib.request import urlopen, URLError


@command()
def link(m, urls):
    print(urls)
    for url in urls:
        try:
            html = urlopen(url)
        except URLError:
            # Don't try to do anything fancy, just ignore the URL
            pass
        else:
            parsed = urlparse(url)
            print(parsed.netloc)
            soup = BeautifulSoup(html)
            if parsed.netloc == "www.twitch.tv":
                meta = (soup.find(property="og:title"), soup.find(property="og:description"))
                meta = [x["content"] for x in meta if x]
                message = m.location, " - ".join(meta)
            elif parsed.netloc == "www.youtube.com" or parsed.netloc == "youtu.be":
                title = soup.find(itemprop="name")
                duration = soup.find(itemprop="duration")
                duration = re.match(r'PT(?P<min>\d+)M(?P<sec>\d+)S', duration["content"])
                if duration.group("min") == "00":
                    time = duration.group("sec") + "s"
                else:
                    time = duration.group("min") + "m" + duration.group("sec") + "s"
                message = "YouTube - " + title["content"] + " (" + time + ")"
            elif parsed.netloc == "www.imgur.com":
                message = "Imgur - " + soup.title.string.strip()
            elif parsed.netloc == "www.reddit.com":
                sub = soup.find("h1", class_="redditname")
                if "comments" in url:
                    # TODO : FIXME
                    title = soup.find("p", class_="title")
                    linkinfo = soup.find("div", "linkinfo")
                    up = linkinfo.find("span", "upvotes")
                    down = linkinfo.find("span", "downvotes")
                    message = "Reddit - \"" + title.a.string + "\" (" + up.span.string +"↑, " +\
                              down.span.string + "↓) - " + sub.a.string
                else:
                    message = "Reddit - " + sub.a.string
            else:
                message = soup.title.string
            m.bot.private_message(m.location, "Link: " + message)