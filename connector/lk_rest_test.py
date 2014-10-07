import pycurl
import cStringIO
import simplejson as json
import pprint

buf = cStringIO.StringIO()

c = pycurl.Curl()
c.setopt(c.VERBOSE, True)
c.setopt(c.URL, "http://produtos-globocom.leankit.com/kanban/api/Card/History/113658644/129396151/")
c.setopt(pycurl.USERPWD, "rodrigo.abreu@corp.globo.com:reminha")
c.setopt(c.WRITEFUNCTION, buf.write)
c.perform()
string_buffer = buf.getvalue()
history = json.loads(string_buffer)

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(history)


