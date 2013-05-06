# import data into ProDetails

from webapp2_extras.appengine.auth.models import User
from google.appengine.ext import ndb

from baymodels import models as bmodels

from boilerplate import models as models

from tools import docs as docs

import csv
import random

joblist = ['Publisher',
           'Manager',
           'Editor',
           'Professional Reader',
           'Designer',
           'Translator',
           'Proofreader']

lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla scelerisque posuere tortor auctor sagittis. Nulla facilisi. Aliquam eget mauris eu ante convallis dapibus id eu eros. Nullam massa mauris, egestas nec ornare sit amet, consequat vel est. Aenean non lorem eu neque aliquam euismod ac id nulla. Aenean sit amet feugiat massa. Ut in lacus sit amet ipsum rhoncus accumsan. Integer molestie, lacus in sodales ultricies, augue tortor posuere eros, a feugiat libero libero in dolor. Proin porta nunc non purus posuere et rutrum orci semper. Mauris viverra ultricies posuere. Vestibulum placerat eros purus. Etiam diam ipsum, tempus et gravida non, malesuada at ipsum. Nulla facilisi. Sed viverra nisi ut odio rutrum iaculis. Suspendisse potenti. Cras semper lacinia dignissim. Ut dui risus, laoreet et luctus ac, blandit non erat. Pellentesque scelerisque purus non mauris malesuada in ultrices purus blandit. Etiam et urna nec quam hendrerit pretium vel eget metus. Nulla rhoncus bibendum enim, vel sollicitudin nibh sodales in. Nunc id massa a nisi vulputate posuere eget a risus. Nunc quis erat nibh, et varius mi. Nullam congue dictum sollicitudin. Vivamus consectetur, ligula a venenatis vehicula, massa nunc suscipit enim, in auctor orci elit nec tellus. Phasellus eleifend, nibh sit amet aliquam feugiat, dui sem luctus orci, nec condimentum lectus est a est. Aenean hendrerit gravida gravida. Morbi placerat vulputate tortor, eu suscipit erat pretium elementum. Sed sed risus ipsum, nec blandit lacus. Phasellus vel ipsum tellus. Cras laoreet facilisis tellus, ut accumsan sem cursus at. Pellentesque semper sem quis quam sodales in vehicula nunc volutpat. Vivamus imperdiet pellentesque lectus, eget ullamcorper quam congue sit amet. Fusce mi eros, malesuada at sollicitudin ut, bibendum ac tellus. Pellentesque ac nisi est, ut placerat ligula. Aenean sit amet porta sem. Proin porta pretium metus, sit amet tincidunt enim malesuada quis. Cras tempor lectus vitae nulla placerat quis dictum ipsum suscipit. Aliquam sit amet aliquam purus. Integer ut elit leo, non auctor quam. Suspendisse in leo non magna posuere rutrum. Nam velit metus, pulvinar id malesuada in, viverra sed neque. Maecenas volutpat nibh at tellus eleifend porttitor. Nullam lobortis bibendum mi, non aliquam ligula venenatis eu. Etiam eleifend fermentum enim non pellentesque. Phasellus at sem id velit blandit malesuada. Nullam sagittis justo eu dolor sodales et malesuada massa pulvinar. Vestibulum vitae condimentum augue."

lorem_split = lorem.replace(' .', ' ').replace(', ', ' ').split(' ')


def bulkdelete(mdl, number):
    qry = mdl.query()
    ndb.delete_multi(qry.fetch(number, keys_only=True))
    print '%s entities deleted from %s' % (str(number), str(mdl))


def import_users():
    reader = csv.reader(open('/Users/richardhaber/Projects/publishbay/baymodels/fakedata.csv', 'rb'), delimiter=',', quotechar='"')
    count = 0
    for row in reader:
        entity = models.User(
            name=row[1],
            last_name=row[2],
            username=row[9],
            email=row[8],
            country=row[7],
            activated=True,
            auth_ids=['own:'+row[9]]
        )
        entity.put()
        count += 1

    print '%s users imported' % count


def import_prodetails():
    qry = models.User.query().fetch(400)
    reader = csv.reader(open('/Users/richardhaber/Projects/publishbay/baymodels/fakedata.csv', 'rb'), delimiter=',', quotechar='"')
    count = 0

    for i in qry:
        row = reader.next()
        a = bmodels.ProDetails()
        a.user = i.key
        a.display_full_name = random.choice([True, False])
        a.title = ' '.join(random.sample(lorem_split, random.randint(3, 10)))
        a.overview = ' '.join(lorem_split[random.randint(0, 15): random.randint(20, 60)])
        a.english_level = random.randint(0, 5)
        a.jobs = random.sample(joblist, random.randint(1, 7))
        a.profile_visibility = random.choice(['everyone', 'pb_users_only', 'hidden'])
        a.address1 = row[3]
        a.city = row[4]
        a.state = row[5]
        a.zipcode = row[6]
        a.phone = row[10]
        a.put()
        count += 1

    print '%s prodetails imported' % count


def import_users_prodetails():
    reader = csv.reader(open('/Users/richardhaber/Projects/publishbay/baymodels/fakedata.csv', 'rb'), delimiter=',', quotechar='"')
    reader.next()  # stripping header
    count = 0

    for row in reader:
        entity = models.User(
            name=row[1],
            last_name=row[2],
            username=row[9],
            email=row[8],
            country=row[7],
            activated=True,
            auth_ids=['own:'+row[9]]
        )
        entity.put()

        k = entity.key
        # k = models.User.query(models.User.username == entity.username).get().key

        a = bmodels.ProDetails()
        a.user = k
        a.display_full_name = random.choice([True, False])
        a.title = ' '.join(random.sample(lorem_split, random.randint(3, 10)))
        a.overview = ' '.join(lorem_split[random.randint(0, 15): random.randint(20, 60)])
        a.english_level = random.randint(0, 5)
        a.jobs = random.sample(joblist, random.randint(1, 7))
        a.profile_visibility = random.choice(['everyone', 'pb_users_only', 'hidden'])
        a.address1 = row[3]
        a.city = row[4]
        a.state = row[5]
        a.zipcode = row[6]
        a.phone = row[10]

        params = {}
        params['username'] = entity.username
        params['name'] = entity.name
        params['last_name'] = entity.last_name
        params['title'] = a.title
        params['overview'] = a.overview
        params['jobs'] = ' '.join(a.jobs)
        docs.ContractorDoc.buildContractor(params)

        a.put()

        count += 1
