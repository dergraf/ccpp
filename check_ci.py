import os
import sys
import urllib2
import xml.etree.ElementTree as ET
from subprocess import call
import config


def cmd(job, c):
    if os.path.exists(job["path"]):
        return call(c.split(), cwd=job["path"])
    else:
        return call(c.split())


def run_cmds(job, category):
    for c in job[category]:
        cmd(job, c)


if __name__ == '__main__':
    request = urllib2.Request(config.ccxml_url)
    if config.username:
        import base64
        base64string = base64.encodestring('%s:%s' % (config.username, config.password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(request)

    if result.getcode() is 200:
        xml = result.read()
        root = ET.fromstring(xml)
        for child in root:
            for job in config.jobs:
                if job["name"] == child.attrib["name"]:
                    if child.attrib["lastBuildStatus"] == "Success":
                        if os.path.exists(job["path"] + "/.git"):
                            cmd(job, "git pull")
                            run_cmds(job, "update")
                        else:
                            cmd(job, "git clone " + job["repo"] + " " + job["path"])
                            run_cmds(job, "init")
                    else:
                        run_cmds(job, "failed")

    else:
        print "problem fetching cc.xml"
        sys.exit(1)
