from pysqlite2 import dbapi2 as sqlite
from numpy import array, tanh

def dtanh(y):
    return 1.0 - y*y

class searchnet:
    def __init__(self, dbname):
        self.db = sqlite.connect(dbname)

    def __del__(self):
        self.db.close()

    def maketables(self):
        self.db.execute("CREATE TABLE hiddennode(create_key)")
        self.db.execute("CREATE TABLE wordhidden(fromid, toid, strength)")
        self.db.execute("CREATE TABLE hiddenurl(fromid, toid, strength)")
        self.db.commit()

    def getstrength(self, fromid, toid, layer):
        if layer == 0: table = 'wordhidden'
        elif layer == 1: table = 'hiddenurl'
        else: return None  # Should really throw an exception
        res = self.db.execute("SELECT strength FROM %s WHERE fromid=%d AND toid=%d"\
                              % (table, fromid, toid)).fetchone()

        if res is None:
            if layer == 0: return -0.2
            if layer == 1: return 1.0
        return res[0]

    def setstrength(self, fromid, toid, layer, strength):
        if layer == 0: table = 'wordhidden'
        elif layer == 1: table = 'hiddenurl'
        else: return None  # Should really thrown an exception
        res = self.db.execute("SELECT rowid FROM %s WHERE fromid=%d AND toid=%d"\
                              % (table, fromid, toid)).fetchone()

        if res is None:
            self.db.execute("INSERT INTO %s(fromid,toid,strength) VALUES (%d,%d,%f)"\
                            % (table, fromid, toid, strength))
        else:
            rowid = res[0]
            self.db.execute("UPDATE %s SET strength=%f WHERE rowid=%d"\
                            % (table, strength, rowid))

    def generatehiddennode(self, wordids, urlids):
        if len(wordids)>3: return None  # i.e. don't learn from unspecific queries?
        # Check if a hidden node already exists for this set of words
        hiddennodekey = '_'.join(sorted([str(wid) for wid in wordids]))
        res = self.db.execute("SELECT rowid FROM hiddennode WHERE create_key='%s'"\
                              % hiddennodekey).fetchone()

        # If not, create one
        if res is None:
            hiddenid = self.db.execute("INSERT INTO hiddennode(create_key) "+\
                                       " VALUES ('%s')"% hiddennodekey).lastrowid
            for wordid in wordids:
                self.setstrength(wordid, hiddenid, 0, 1.0/len(wordids))
            for urlid in urlids:
                self.setstrength(hiddenid, urlid, 1, 0.1)

            self.db.commit()

    def getrelevanthiddenids(self, wordids, urlids):
        nodes = set([])
        for wordid in wordids:
            for row in self.db.execute("SELECT toid FROM wordhidden "+\
                                       "WHERE fromid=%d" % wordid): nodes.add(row[0])
        for urlid in urlids:
            for row in self.db.execute("SELECT fromid FROM hiddenurl "+\
                                       "WHERE toid=%d" % urlid): nodes.add(row[0])
        return list(nodes)

    def setupnetwork(self, wordids, urlids):
        # value lists
        self.wordids = wordids
        self.hiddenids = self.getrelevanthiddenids(wordids, urlids)
        self.urlids = urlids

        # node outputs
        self.ai = array([[1.0]]*len(self.wordids))
        self.ah = array([[1.0]]*len(self.hiddenids))
        self.ao = array([[1.0]]*len(self.urlids))

        # weight matrices
        self.wi = array([[self.getstrength(wid, hid, 0) for wid in self.wordids]
                   for hid in self.hiddenids])
        self.wo = array([[self.getstrength(hid, uid, 1) for hid in self.hiddenids]
                   for uid in self.urlids])

    def feedforward(self):
        self.ah = tanh(self.wi.dot(self.ai))
        self.ao = tanh(self.wo.dot(self.ah))

        return self.ao

    def getresults(self, wordids, urlids):
        self.setupnetwork(wordids, urlids)
        return self.feedforward()

    def backprop(self, targets, alpha = 0.5):
        # Calculate errors for output
        target_array = array(targets, ndmin = 2).transpose()
        output_deltas = dtanh(self.ao) * (target_array - self.ao)

        hidden_deltas = dtanh(self.ah) * self.wo.transpose().dot(output_deltas)

        self.wo += alpha * output_deltas.dot(self.ah.transpose())
        self.wi += alpha * hidden_deltas.dot(self.ai.transpose())

    def updatedatabase(self):
        for i in range(len(self.wordids)):
            for j in range(len(self.hiddenids)):
                self.setstrength(self.wordids[i], self.hiddenids[j], 0, self.wi[j][i])

        for j in range(len(self.hiddenids)):
            for k in range(len(self.urlids)):
                self.setstrength(self.hiddenids[j], self.urlids[k], 1, self.wo[k][j])

        self.db.commit()

    def trainquery(self, wordids, urlids, selectedurl):
        self.generatehiddennode(wordids, urlids)

        self.setupnetwork(wordids, urlids)
        self.feedforward()
        targets = [0.0] * len(urlids)
        targets[urlids.index(selectedurl)]=1.0
        self.backprop(targets)
        self.updatedatabase()


def setup_test_db():
    nn = searchnet('testnn.db')
    nn.db.execute('DROP TABLE IF EXISTS hiddennode')
    nn.db.execute('DROP TABLE IF EXISTS wordhidden')
    nn.db.execute('DROP TABLE IF EXISTS hiddenurl')
    nn.maketables()

    wWorld,wRiver,wBank =101,102,103
    uWorldBank,uRiver,uEarth =201,202,203
    nn.generatehiddennode([wWorld,wBank],[uWorldBank,uRiver,uEarth])

    allurls=[uWorldBank,uRiver,uEarth]
    for i in range(30):
        nn.trainquery([wWorld,wBank],allurls,uWorldBank)
        nn.trainquery([wRiver,wBank],allurls,uRiver)
        nn.trainquery([wWorld],allurls,uEarth)

    return nn, allurls
