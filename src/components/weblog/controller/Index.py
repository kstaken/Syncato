import time

from RESTComponent import RESTComponent
SECONDS_PER_DAY = 60 * 60 *  24;

class Index (RESTComponent):
    def get(self, context):
        query = context['query']
        postID = context['recordID']
        if (postID != -1):
            if (query):
                result = self.db.xpathQueryRecord(postID, query)            
            else:
                result = self.db.getRecord(None, postID)
            
        elif (query):
            result = self.db.xpathQuery(None, query)
        else: 
            query = "/item[pubDate/@seconds > %s]" % (
                str(time.time() - (SECONDS_PER_DAY * float(self.site.getConfigValue("/blog/frontpage-term")))))
            
            result = self.db.xpathQuery(None, query)
            if (context['view'] == ''):
                context['view'] = 'front-page'
            
        return result