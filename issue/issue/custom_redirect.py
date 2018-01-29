from scrapy.downloadermiddlewares.redirect import RedirectMiddleware
from scrapy.exceptions import CloseSpider
import time
import sys

class CustomRedirectMiddleware(RedirectMiddleware):
    last_sleep = 0
    sleep_interval = 10 * 60
    def _redirect(self, redirected, request, spider, reason):
        # This is scrapy bug, when redict url equal to request url, this url will be ignored
        if request.url == redirected.url:
            request.dont_filter = True

        if not self.is_gruoyan_redict(redirected.url):
            return super(CustomRedirectMiddleware, self)._redirect(redirected, request, spider, reason)

        current = int(time.time())
        if (current - self.last_sleep) > self.last_sleep:
            print "detect an guoyan redict to :%s, will exist" % redirected.url
            raise CloseSpider("detect an guoyan redict")
            print "detect an guoyan redict to :%s, will sleep %d seconds" % (redirected.url, self.sleep_interval)
            time.sleep(self.sleep_interval)
            self.last_sleep = int(time.time())

        else:
            print "detect an guoyan redict to :%s, wont sleep cause has sleep as %s" % (redirected.url, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.last_sleep)) )

        new_url = redirected.url.replace("DocSummary", "docview")
        redirected_new = redirected.replace(url = new_url)
        request_new = request.replace(dont_filter = True)
        return super(CustomRedirectMiddleware, self)._redirect(redirected_new, request_new, spider, reason)


    def is_gruoyan_redict(self, url):
        if url.find("DocSummary") != -1:
            return True
        return False

