import requests
import urllib2
import urllib
import threading
import re
import os
from bs4 import BeautifulSoup

basedir = os.path.abspath(os.path.dirname(__file__))

USER_FOLDER = basedir + '/downloads/'
BROWSING_FOLDER = 'http://www.deejayportal.com/download/acapellas/'


class Scraper(object):
    def __init__(self):
        pass

    @staticmethod
    def download_mp3(where_to_find_file, where_to_save_file):
        try:
            mp3file = urllib2.urlopen(where_to_find_file)
            output = open(where_to_save_file, 'wb')
            output.write(mp3file.read())
            output.close()
        except Exception as e:
            print 'failed to download: ', where_to_find_file

    def dispatch_workers(self):
        pool = []
        folders = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
                   's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0-9']

        for folder in folders:
            worker = threading.Thread(
                target=self.work_on_folder,
                kwargs={
                    'start_page': 0,
                    'letter_folder': folder,
                }
            )
            pool.append(worker)
            worker.start()

        for thread in pool:
            thread.join()

    def work_on_folder(self, start_page=0, letter_folder='0-9'):
        payload = {'start': start_page}

        pattern = re.compile('mp3=([^~]*).mp3')

        r = requests.get(BROWSING_FOLDER + letter_folder, params=payload)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text)

            dl_details = soup.find_all(id='djp-dl-details')
            for dl_detail in dl_details:
                params = dl_detail.find_all('param')
                for param in params:
                    try:
                        match = re.match(pattern, param['value'])
                        if match:
                            # 'http://www.deejayportal.com/dldownloaddl/Acapellas/0-1/68 Beats - Free Your Mind
                            # (Acapella).mp3'
                            song_file_path_with_white_space = param['value'][4:match.end()]
                            song_name_with_ext = song_file_path_with_white_space.split('/')[-1]
                            # drop the http:// and urllib encode the path
                            where_to_find_file = 'http://' + urllib.quote(song_file_path_with_white_space[7:])
                            where_to_save_file = USER_FOLDER + song_name_with_ext
                            self.download_mp3(where_to_find_file, where_to_save_file)
                    except KeyError:
                        pass
            page_navs = soup.find_all(class_='pagination-next')
            if page_navs:
                page_nav = page_navs[0]
                # does the page_nav have a link to the next page?
                if page_nav.find('a'):
                    self.work_on_folder(start_page+20, letter_folder=letter_folder)

if __name__ == '__main__':
    scraper = Scraper()
    scraper.dispatch_workers()
