import sys
import json
class CheckDownload(object):
    def __init__(self, should_download_url_file, download_meta_file)
        self.should_download_url_file = should_download_url_file
        self.download_meta_file = download_meta_file

    def check():
        should_download_urls = []
        with open(self.should_download_url_file) as f: 
            for line in f:
                line = line.strip()
                should_download_urls.append(line)
            

        with open(self.download_meta_file) as f:
            for line in f:
                line = line.strip()
                try:
                    json_data = json.load(line.encode("utf-8"))
                except Exception as e:
                    continue

if __name__ == '__main__':
    if len(sys.args) != 2:
        print "Usage: python ./check_download should_download_url_file download_meta_file"
        sys.exit(0)

    should_download_url_file = sys.argv[0]
    download_meta_file = sys.argv[1]

    check_download = CheckDownload(should_download_url_file, download_meta_file)
    check_download.check()
