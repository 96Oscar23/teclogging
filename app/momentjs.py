from markupsafe import Markup
class momentjs(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, format):
        
        return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>" % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), format))
    def format(self, fmt):
    
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")


    def format2(self, fmt,disabled,id,clase):
        return Markup("<script>\ndocument.write(\"<input value='\"+moment(\"%s\").format(\"%s\")+\"' %s type='text' id='%s' name='%s' class='%s'>\");\n</script>" % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), fmt,disabled,id,id,clase))

