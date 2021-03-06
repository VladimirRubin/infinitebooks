from grab.spider import Spider, Task
from grab import Grab
from pymongo import MongoClient
import csv

BASE_URL = 'http://www.e-reading.club'

class eReadingClubSpider(Spider):
    def prepare(self):
        self.client = MongoClient('mongodb://heroku_qq2rrz3t:fl86443lnj8i5ihchkhkoj7q8g@ds059654.mongolab.com:59654/heroku_qq2rrz3t')
        self.db = self.client['heroku_qq2rrz3t']
        self.collection = self.db.books

    def task_generator(self):
        g = Grab()
        g.setup(proxy='95.141.187.216:8080')
        g.setup(url=BASE_URL)        
        yield Task('letters', grab=g)

    def task_letters(self, grab, task):
        for link in grab.xpath_list('//a/@href'):
            if 'letter' in link:
                letter = link.split('=')[-1]
                grab.setup(url=BASE_URL+ '/author.php?letter=' + letter)
                yield Task('letter', grab=grab, letter=letter)

    def task_letter(self, grab, task):
        for link in grab.xpath_list('//a/@href'):
            if 'author=' in link:
                author_id = link.split('=')[-1]
                grab.setup(url=BASE_URL + '/bookbyauthor.php?author=' + author_id)
                yield Task('author', grab=grab, letter=task.letter, author_id=author_id)

    def task_author(self, grab, task):
        for link in grab.xpath_list('//a/@href'):
            if 'book=' in link:
                book_id = link.split('=')[-1]
                grab.setup(url=BASE_URL + '/book.php?book=' + book_id)
                yield Task('book', grab=grab, letter=task.letter, author_id=task.author_id, book_id=book_id)

    def task_book(self, grab, task):
        self.collection.insert({
            'letter': task.letter,
            'author_id': task.author_id,
            'book_id': task.book_id
        })
            


if __name__ == '__main__':
    bot = eReadingClubSpider()
    bot.run()
    print(bot.render_stats())
